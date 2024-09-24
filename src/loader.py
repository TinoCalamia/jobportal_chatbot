import os
from langchain_google_community import GoogleDriveLoader
from langchain_community.document_loaders import DirectoryLoader, UnstructuredWordDocumentLoader

import src.constants as con

def load_folder_docs(path=os.path.join(os.getcwd(), 'src', 'documents')):
    loader = DirectoryLoader(path, glob="*.docx", use_multithreading=True, loader_cls=UnstructuredWordDocumentLoader)

    docs = loader.load()

    return docs



# def load_google_docs(folder_id: str = con.JOB_FOLDER_ID, 
#                      credentials_path: str = con.OAUTH_CREDENTIALS_PATH, 
#                      token_path: str = con.TOKEN_PATH, 
#                      service_account_key_path: str = con.SERVICE_ACCOUNT_CREDENTIALS_PATH, 
#                      file_types: list = ["document"], 
#                      recursive: bool = False):
    
#     """
#     Loads documents from Google Drive using the GoogleDriveLoader class.

#     Args:
#         folder_id (str): The ID of the folder containing the documents.
#         credentials_path (str): The path to the credentials file.
#         token_path (str): The path to the token file.
#         service_account_key_path (str): The path to the service account key file.
#         file_types (list): The types of files to load."""

#     loader = GoogleDriveLoader(
#         folder_id=folder_id,
#         credentials_path= os.getcwd() + credentials_path,
#         token_path= os.getcwd() + token_path,
#         # service_account_key= os.getcwd() + service_account_key_path,
#         file_types=file_types,
#         recursive=recursive,)
    
#     docs = loader.load()

#     return docs