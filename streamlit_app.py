import os
import shutil
from PIL import Image

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit as st

import src.constants as con
from css.css import streamlit_css
from src.utils import access_secret_version

os.environ['LANGCHAIN_TRACING_V2'] = "true"
os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGCHAIN_API_KEY'] = access_secret_version("jobportal-chatbot", "LANGCHAIN_API_KEY")


from src.loader import load_google_docs
import src.prompts as pr
from src.utils import token_generator, format_docs, check_token_expiry
from src.vectorstore import create_vectorstore_from_documents, split_documents, add_documents_to_vectorstore


############# LOAD TOKEN IF NEEDED #############
if (not os.path.exists('.credentials/token.json')) or (check_token_expiry('.credentials/token.json')):
    token_generator()
    shutil.move(os.getcwd() + '/token.json', os.path.join(os.getcwd() + '/.credentials/', os.path.basename('token.json')))

############# DEFINE TEXT SPLITTER #############
text_splitter = RecursiveCharacterTextSplitter(chunk_size=con.SPLITTER_CHUNK_SIZE, chunk_overlap=con.SPLITTER_CHUNK_OVERLAP)
############# DEFINE LLM #######################
llm = ChatOpenAI(model_name=con.MODEL_NAME, temperature=con.MODEL_TEMPERATURE)

############# LOAD AND SPLIT JOBS #######################
print('---------- Load Jobs -------------')
job_docs = load_google_docs(folder_id = con.JOB_FOLDER_ID, file_types=["document", "pdf"])
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

####################SETUP STREAMLIT APP#####################
print('---------- Load Streamlit App -------------')
# Custom CSS for a brighter appearance with blue title and lighter input field
st.set_page_config(page_title="Job Finder ChatBot", page_icon="💼", layout="centered")

st.markdown(streamlit_css, unsafe_allow_html=True)

# Title and Image
st.markdown("<h1 style='text-align: center; color: #1e90ff;'>💼 Job Assistent</h1>", unsafe_allow_html=True)

# Load and display the image
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(Image.open("src/images/Bayernlb-logo.png"), use_column_width=True)
    
@st.experimental_fragment
def run_app():
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hey! Ich bin dein Job-Assistent. Ich helfe dir deinen Traumjob zu finden. Wie kann ich Ihnen heute behilflich sein?"}
        ]
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "current_question" not in st.session_state:
        st.session_state.current_question = None

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if st.session_state.question_count < 3:
        prompt = st.chat_input(f"Frag mich Dinge bzgl. Jobs (Du hast noch {3 - st.session_state.question_count} Fragen):")
        
        if prompt and prompt != st.session_state.current_question:
            st.session_state.current_question = prompt
            st.session_state.question_count += 1
            
            # Display user input
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # If it's not the third question, just acknowledge and ask for the next
            if st.session_state.question_count < 3:
                response = f"Danke für deine {st.session_state.question_count}. Frage. Hast du noch eine weitere Frage?"
            else:
                # Generate response after the third question
                combined_questions = " ".join([msg["content"] for msg in st.session_state.messages if msg["role"] == "user"])
                response = rag_chain.invoke(combined_questions)
            
            # Display chatbot response
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            if st.session_state.question_count == 3:
                st.session_state.messages.append({"role": "assistant", "content": "Danke für deine Fragen! Ich hoffe ich konnte dir bei der Suche nach einem passenden Job behilflich sein. Wenn du noch weitere Fragen hast, kannst du mich jederzeit fragen."})
    else:
        st.markdown('<div class="stAlert">Du hast die maximale Anzahl von Fragen erreicht. Ich hoffe ich konnte dir bei der Suche nach einem passenden Job behilflich sein. Wenn du noch weitere Fragen hast, kannst du mich jederzeit fragen.</div>', unsafe_allow_html=True)
run_app()