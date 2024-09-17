import os
import shutil

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit as st

import src.constants as con
from src.utils import access_secret_version

os.environ['LANGCHAIN_TRACING_V2'] = "true"
os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGCHAIN_API_KEY'] = access_secret_version("jobportal-chatbot", "LANGCHAIN_API_KEY")


from src.loader import load_google_docs
import src.prompts as pr
from src.utils import token_generator, format_docs
from src.vectorstore import create_vectorstore_from_documents, split_documents, add_documents_to_vectorstore

if not os.path.exists('.credentials/token.json'):
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


if con.PROMPT_TEMPLATE == "basic":
    prompt = ChatPromptTemplate.from_template(pr.create_basic_prompt())
# else:
#     prompt = hub.pull("rlm/rag-prompt")

# Chain
rag_chain = (
     {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

####################SETUP STREAMLIT APP#####################
print('---------- Load Streamlit App -------------')
st.set_page_config(page_title="Job Finder ChatBot", page_icon="💼")
st.title("💼 Job Finder Assistant")
@st.experimental_fragment
def run_app():
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Job Finder Assistant. I can help you find the best job match based on your skills and preferences. What would you like to know about our open positions?"}
        ]
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if st.session_state.question_count < 3:
        if prompt := st.chat_input("Ask about job positions (you have 3 questions):"):
            st.session_state.question_count += 1
            
            # Display user input
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get chatbot response
            response = rag_chain.invoke(prompt)
            
            # Display chatbot response
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Check if it's the last question
            if st.session_state.question_count == 3:
                st.session_state.messages.append({"role": "assistant", "content": "Thank you for your questions! I hope I've helped you find a suitable job position. If you need more information, please visit our website or contact our HR department."})
    else:
        st.info("You've reached the maximum number of questions. Thank you for using the Job Finder Assistant!")
run_app()