from src.utils import create_oauth_credentials_file, create_service_account_credentials_file, create_api_key_file

# Load credentials
create_oauth_credentials_file()
create_service_account_credentials_file()
create_api_key_file('OPENAI_API_KEY','openai_key.json')
create_api_key_file('LANGCHAIN_API_KEY','langchain_key.json')