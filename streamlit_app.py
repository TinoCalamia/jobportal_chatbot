# %%
import json
import os
import shutil
import src.constants as con


# %%
with open(os.getcwd()+ con.API_KEYS_PATH, "r") as f:
    credentials = json.load(f)


os.environ['LANGCHAIN_TRACING_V2'] = credentials["LANGCHAIN_TRACING_V2"]
os.environ['LANGCHAIN_ENDPOINT'] = credentials["LANGCHAIN_ENDPOINT"]
os.environ['LANGCHAIN_API_KEY'] = credentials["LANGCHAIN_API_KEY"]
os.environ['OPENAI_API_KEY'] = credentials["OPENAI_API_KEY"]
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials["GOOGLE_APPLICATION_CREDENTIALS"]

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit as st 


from src.loader import load_content_from_web, load_google_docs
import src.prompts as pr
from src.utils import token_generator, format_docs
from src.vectorstore import create_vectorstore_from_documents, split_documents, add_documents_to_vectorstore

# %%
if not os.path.exists('.credentials/token.json'):
    token_generator()

    shutil.move(os.getcwd() + '/token.json', os.path.join(os.getcwd() + '/.credentials/', os.path.basename('token.json')))

# Define the document loader
text_splitter = RecursiveCharacterTextSplitter(chunk_size=con.SPLITTER_CHUNK_SIZE, chunk_overlap=con.SPLITTER_CHUNK_OVERLAP)
# Define the LLM
llm = ChatOpenAI(model_name=con.MODEL_NAME, temperature=con.MODEL_TEMPERATURE)

# %%
#### ADDING INTERVIEW CONTEXT ####
print('load interview coneent')

job_docs = load_google_docs(folder_id = con.RESOURCE_FOLDER_ID, file_types=["document", "pdf"])
job_splits = split_documents(job_docs, text_splitter=text_splitter)
vector_db = create_vectorstore_from_documents(job_splits)


# %%

retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 5})

if con.PROMPT_TEMPLATE == "basic":
    prompt = ChatPromptTemplate.from_template(pr.create_basic_prompt())
else:
    prompt = hub.pull("rlm/rag-prompt")

# Chain
rag_chain = (
     {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# %%
print('load st app')
# Set page configuration including title and icon
st.set_page_config(page_title="ChatBot",
                page_icon="🤔")
st.title("🦜🔗 Quickstart App")
@st.experimental_fragment
def run_app():

    # Initialize session state to store chat messages if not already present
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Display previous chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # Accept user input in the chat interface
    if prompt := st.chat_input("What is your question?"):
        @st.experimental_fragment
        def run_conversation():
            # Display user input as a chat message
            with st.chat_message("user"):
                st.markdown(prompt)
            # Append user input to session state
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get response from the chatbot based on user input
            response = rag_chain.invoke(prompt)
            
            # Display response from the chatbot as a chat message
            with st.chat_message("assistant"):
                # Write response with modified output (if any)
                st.write(response)
            # Append chatbot response to session state
            st.session_state.messages.append({"role": "assistant", "content": response})
        run_conversation()
run_app()