import os
from langchain_google_community import GoogleDriveLoader

import src.constants as con
from src.utils import create_oauth_credentials_file, create_service_account_credentials_file

create_oauth_credentials_file()
create_service_account_credentials_file()


def load_google_docs(folder_id: str = con.JOB_FOLDER_ID, 
                     credentials_path: str = con.OAUTH_CREDENTIALS_PATH, 
                     token_path: str = con.TOKEN_PATH, 
                     service_account_key_path: str = con.SERVICE_ACCOUNT_CREDENTIALS_PATH, 
                     file_types: list = ["document"], 
                     recursive: bool = False):
    
    loader = GoogleDriveLoader(
        folder_id=folder_id,
        credentials_path= os.getcwd() + credentials_path,
        token_path= os.getcwd() + token_path,
        service_account_key= os.getcwd() + service_account_key_path,
        file_types=file_types,
        recursive=recursive,)
    
    docs = loader.load()

    return docs