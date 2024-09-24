import os
import json
import shutil
from PIL import Image
import random

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
st.markdown("<h1 style='text-align: center; color: ##0582BC;'>💼 Job Assistent</h1>", unsafe_allow_html=True)

# Load and display the image
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(Image.open("src/images/Bayernlb-logo.png"))
    
def run_app():
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hey! Ich bin dein Job-Assistent. Ich helfe dir deinen Traumjob zu finden. Wie kann ich dir heute behilflich sein?"}
        ]
    if "current_question" not in st.session_state:
        st.session_state.current_question = None

    counter=0

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    prompt = st.chat_input(f"Frag mich Dinge bzgl. Jobs.")
    
    if prompt and prompt != st.session_state.current_question:
        
        # Display user input
        st.session_state.messages.append({"role": "user", "content": prompt})
        counter = len([True for item in st.session_state['messages'] if item['role'] == 'user'])
        print(counter)

        with st.chat_message("user"):
            print(st.session_state)
            print(st.session_state.current_question)
            st.markdown(prompt)
        
        # If it's not the third question, just acknowledge and ask for the next
        if counter < 3:
            response_list = responses = [
                "Super, danke für die Info! Wusstest Du, dass BayernLB einst als ‚Hausbank der bayerischen Könige‘ galt? Na gut, vielleicht nicht ganz, aber ein bisschen königlich sind wir schon! Kannst du mir noch mehr Informationen geben?",
                "Vielen Dank! Weißt Du, neulich habe ich Elon Musk gefragt, ob er BayernLB kennt. Er meinte, er braucht noch einen Kredit für sein nächstes Weltraumprojekt – vielleicht sollten wir ihm helfen! Beschreib deine Stärken oder Interessen noch ein wenig mehr.",
                "Haha, das klingt genau wie das, was ich von unserem CEO gehört habe! Fun Fact: Wusstest Du, dass BayernLB eine der wenigen Banken ist, die auch wirklich noch in Bayern verankert sind? Nicht nur im Namen! Beschreib deine Stärken oder Interessen noch ein wenig mehr.",
                "Danke für Deine Antwort! Apropos, BayernLB hat einmal eine Kuh auf einem Bauernhof in Bayern gesponsert. Naja, nicht wirklich, aber wir machen uns stark für regionale Projekte! Beschreib deine Stärken oder Interessen noch ein wenig mehr.",
                "Klasse Info! Wusstest Du, dass wir bei BayernLB so regional sind, dass wir sogar die Weißwurst lieben? Natürlich nicht in der Bank, aber das gehört zu unserem bayerischen Herz! Kannst du mir noch mehr Informationen geben?",
                "Interessant, vielen Dank! Fun Fact: BayernLB hat sogar in der bayerischen Bierbraukunst investiert! Okay, das ist vielleicht übertrieben, aber wir sind definitiv Fans davon. Beschreib deine Stärken oder Interessen noch ein wenig mehr.",
                "Das ist spannend! Wusstest Du, dass BayernLB Kunden hat, die vom Tegernsee bis zur Zugspitze reichen? So viele Höhenmeter haben wir schon erklommen – zumindest auf dem Papier! Kannst du mir noch mehr Informationen geben?",
                "Danke Dir! Apropos, BayernLB ist ein bisschen wie der FC Bayern München – wir spielen ganz oben mit! Okay, vielleicht nicht auf dem Fußballfeld, aber definitiv im Finanzwesen. Kannst du mir noch mehr Informationen geben?",
                "Super, danke! Fun Fact: BayernLB hat fast so viele Mitarbeiter wie es Biergärten in München gibt! Na gut, vielleicht nicht ganz, aber wir kommen nah dran. Beschreib deine Stärken oder Interessen noch ein wenig mehr.",
                "Vielen Dank! Wusstest Du, dass BayernLB die einzige Bank ist, die sowohl in der Finanzwelt als auch in den Bergen von Bayern fest verwurzelt ist? Das ist wahre Bodenhaftung! Beschreib deine Stärken oder Interessen noch ein wenig mehr."
            ]

            response = random.choice(response_list)
        else:
            # Generate response after the third question
            combined_questions = " ".join([msg["content"] for msg in st.session_state.messages if msg["role"] == "user"])
            response = rag_chain.invoke(combined_questions)
        
        # Display chatbot response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        if counter == 3:
           st.session_state.messages.append({"role": "assistant", "content": "Danke für deine Fragen! Ich hoffe ich konnte dir bei der Suche nach einem passenden Job behilflich sein. Wenn du noch weitere Fragen hast, kannst du mich jederzeit fragen."})
run_app()