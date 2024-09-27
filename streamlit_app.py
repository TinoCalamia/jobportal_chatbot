import os
import json
import shutil
from PIL import Image
import random
import numpy as np

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit as st

import src.constants as con
from src.utils import access_secret_version, create_api_key_file, create_service_account_credentials_file

os.environ['LANGCHAIN_TRACING_V2'] = "true"
os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"

# create_service_account_credentials_file()
# create_api_key_file('OPENAI_API_KEY','openai_key.json')


from src.loader import load_folder_docs
import src.prompts as pr
from src.utils import token_generator, format_docs, check_token_expiry
from src.vectorstore import create_vectorstore_from_documents, split_documents, add_documents_to_vectorstore

st.set_page_config(page_title="Job Finder ChatBot", page_icon="💼", layout="centered")

############# LOAD TOKEN IF NEEDED #############
#if (not os.path.exists('.credentials/token.json')) or (check_token_expiry('.credentials/token.json')):
# token_generator()
# shutil.move(os.getcwd() + '/token.json', os.path.join(os.getcwd() + '/.credentials/', os.path.basename('token.json')))


@st.cache_resource()
def prepare_data():
    ############# DEFINE TEXT SPLITTER #############
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=con.SPLITTER_CHUNK_SIZE, chunk_overlap=con.SPLITTER_CHUNK_OVERLAP)
    ############# DEFINE LLM #######################
    llm = ChatOpenAI(model_name=con.MODEL_NAME, temperature=con.MODEL_TEMPERATURE)

    ############# LOAD AND SPLIT JOBS #######################
    print('---------- Load Jobs -------------')
    job_docs = load_folder_docs()
    if not job_docs:
        raise ValueError("No documents found in the specified folder.")
    job_splits = split_documents(job_docs, text_splitter=text_splitter)

    ############# DEFINE VECTOR DB #######################
    print('---------- Create vector DB -------------')
    vector_db = create_vectorstore_from_documents(job_splits)   
    retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    ############# GET PROMPT #######################
    if con.PROMPT_TEMPLATE == "basic":
        prompt = ChatPromptTemplate.from_template(pr.create_basic_prompt())
    if con.PROMPT_TEMPLATE == "job":
        prompt = ChatPromptTemplate.from_template(pr.create_job_prompt())

    ############# DEFINE RAG CHAIN #######################
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

rag_chain = prepare_data()

####################SETUP STREAMLIT APP#####################
print('---------- Load Streamlit App -------------')

# Title and Image
st.markdown("<h1 style='text-align: center; color: ##0582BC;'>Traumjob-Finder</h1>", unsafe_allow_html=True)
saenger_img = Image.open("src/images/blb_saenger.png")
fee_img = Image.open("src/images/blb_fee.png")
# Load and display the image
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(Image.open("src/images/Bayernlb-logo.png"))
    
def run_app():
    # Initialize session state
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", 
             "content": "Hey! Schön, dass Du Dich für einen Job bei der BayernLB interessierst. Ich helfe Dir gerne dabei, Deinen Traumjob zu finden. Dafür brauche ich zunächst ein paar Angaben von Dir. Welche Einsatzbereiche interessieren Dich?"}
        ]
    if "current_question" not in st.session_state:
        st.session_state.current_question = None

    counter=0

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "user":
            avatar = fee_img
        elif message["role"] != "assistant":
            avatar = None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Accept user input
    prompt = st.chat_input(f"Chatte mit mir.")
    
    if prompt and prompt != st.session_state.current_question:
        
        # Display user input
        st.session_state.messages.append({"role": "user", "content": prompt})
        counter = len([True for item in st.session_state['messages'] if item['role'] == 'user'])
        print(counter)

        with st.chat_message("user", avatar=None):
            st.markdown(prompt)
        
        # If it's not the third question, just acknowledge and ask for the next
        if counter < 5:
            response_list = [
                "Das klingt schon einmal spannend! Bei der BayernLB legen wir Wert darauf, dass sich unsere Mitarbeitenden mit unserem Unternehmen identifizieren können. Erzähl mir mehr: Was ist Dir bei einem Job wichtig?",
                "Vielen Dank! Um das perfekte Job-Match für Dich zu finden, beschreibe mir bitte noch Deine Stärken: Worin bist Du besonders gut?",
                "Super – das hilft mir weiter. Apropos Traumjob, kurze Frage am Rande: Von welchem Job hast Du eigentlich als Kind geträumt? 💭",
                "Interessant! Bei der BayernLB brauchen wir Menschen wie Dich, die Großes bewirken möchten. Als Team arbeiten wir jeden Tag daran, großen Ideen zum Fortschritt zu verhelfen. Bist Du bereit, ein Teil davon zu werden?"
            ]

            response = response_list[counter-1]
            response_list = response_list[counter:]

        else:
            # Generate response after the third question
            combined_questions = " ".join([msg["content"] for msg in st.session_state.messages if msg["role"] == "user"])
            response = rag_chain.invoke(combined_questions)
        
        # Display chatbot response
        with st.chat_message("assistant", avatar=np.array(fee_img)):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        if counter == 5:
           st.session_state.messages.append({"role": "assistant", "content": "Danke für deine Fragen! Ich hoffe ich konnte dir bei der Suche nach einem passenden Job behilflich sein. Wenn du noch weitere Fragen hast, kannst du mich jederzeit fragen."})
run_app()