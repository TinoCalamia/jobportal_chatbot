import os
import json
from google.cloud import secretmanager
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Secret Manager function to retrieve secrets
def access_secret_version(project_id, secret_id, version_id="latest"):
    """Retrieve secret from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

# Function to generate and save tokens for Google APIs (Drive, etc.)
def token_generator(scopes=['https://www.googleapis.com/auth/drive'], token_path='token.json', credentials_path='oauth_credentials.json') -> Credentials:
    """Handle OAuth2 flow and return valid credentials."""
    creds = None
    # Check if token.json exists and is valid
    if os.path.exists(token_path):
        with open(token_path, 'r') as token_file:
            creds = Credentials.from_authorized_user_file(token_path, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # If no valid token exists, run OAuth2 flow to get new credentials
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
    return creds

# Function to create OAuth credentials file from Secret Manager
def create_oauth_credentials_file(project_id):
    """Create OAuth credentials file from Secret Manager."""
    oauth_credentials = access_secret_version(project_id, "OAUTH_CREDENTIALS")
    credentials_dir = os.path.join(os.getcwd(), ".credentials")
    credentials_file = os.path.join(credentials_dir, "oauth_credentials.json")
    os.makedirs(credentials_dir, exist_ok=True)
    with open(credentials_file, 'w') as f:
        f.write(oauth_credentials)
    print(f"OAuth credentials saved to {credentials_file}")

# Function to create service account credentials file from Secret Manager
def create_service_account_credentials_file(project_id):
    """Create service account credentials file from Secret Manager."""
    sa_key = access_secret_version(project_id, "SERVICE_ACCOUNT_KEY")
    credentials_dir = os.path.join(os.getcwd(), ".credentials")
    credentials_file = os.path.join(credentials_dir, "service_account.json")
    os.makedirs(credentials_dir, exist_ok=True)
    with open(credentials_file, 'w') as f:
        f.write(sa_key)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
    print(f"Service account credentials saved to {credentials_file}")

# Function to retrieve and save OpenAI API key from Secret Manager
def create_openai_api_key_file(project_id):
    """Retrieve and save the OpenAI API key from Secret Manager."""
    openai_api_key = access_secret_version(project_id, "OPENAI_API_KEY")
    credentials_dir = os.path.join(os.getcwd(), ".credentials")
    credentials_file = os.path.join(credentials_dir, "openai_api_key.json")
    os.makedirs(credentials_dir, exist_ok=True)
    with open(credentials_file, 'w') as f:
        f.write(openai_api_key)
    os.environ["OPENAI_API_KEY"] = openai_api_key
    print(f"OpenAI API key saved to {credentials_file} and environment variable 'OPENAI_API_KEY'")

# Main function to run all credential retrieval steps
def main():
    project_id = "jobportal-chatbot-436116"  # Replace with your project ID

    # Step 1: Create OAuth credentials file
    create_oauth_credentials_file(project_id)

    # Step 2: Create service account credentials file
    create_service_account_credentials_file(project_id)

    # Step 3: Create OpenAI API key file
    create_openai_api_key_file(project_id)

    # Step 4: Generate and print Google Drive credentials
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = token_generator(scopes=scopes, token_path='token.json', credentials_path='.credentials/oauth_credentials.json')
    print(f"Retrieved and saved Google Drive credentials: {creds}")

if __name__ == '__main__':
    main()