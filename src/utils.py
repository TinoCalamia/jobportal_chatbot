import os.path
import os
import json
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.cloud import secretmanager

import src.constants as con


def check_token_expiry(token_path):
    with open(token_path, 'r') as token_file:
        token_data = json.load(token_file)
    expiry_str = token_data.get('expiry', '0')
    expiry_timestamp = int(expiry_str) if expiry_str.isdigit() else 0
    current_timestamp = int(datetime.now().timestamp())
    return expiry_timestamp > current_timestamp


def access_secret_version(project_id, secret_id, version_id="latest"):
    # Create the Secret Manager client
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version
    response = client.access_secret_version(name=name)

    # Return the payload as a string
    return response.payload.data.decode("UTF-8")

def token_generator(*,
                    scopes: list=['https://www.googleapis.com/auth/drive'],
                    token_path: str='token.json',
                    credentials_path: str=os.getcwd()+ con.OAUTH_CREDENTIALS_PATH
                    ) -> Credentials:
    """Given a path to a saved token (which may not exist) and a path to
    your credentials file, return a `Credentials` instance.
    """

    def recertify():
        """Create a new Credentials instance using InstalledAppFlow."""
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, scopes)
        return flow.run_local_server(port=0)

    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        # We have a token file. Recreate the credentials"
        creds = Credentials.from_authorized_user_file(token_path, scopes)
        if creds.valid:
            # We have valid credentials
            return creds

    # Either token_path does not exist or the credentials are no longer valid.
    if creds and creds.expired and creds.refresh_token:
        # The credentials have expired. Try to refresh the credentials:
        try:
            creds.refresh(Request())
        except Exception:
            # Probaly the refresh token has expired, so we must start anew
            creds = recertify()
    else:
        creds = recertify()

    # Save the credentials for the next run
    with open(token_path, 'w') as token_file:
        token_file.write(creds.to_json())

    return creds

# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def create_oauth_credentials_file():
    oauth_credentials = access_secret_version("jobportal-chatbot", "OAUTH_CREDENTIALS")

    # Ensure the directory exists
    credentials_dir = os.path.join(os.getcwd(), ".credentials")
    # Define the full path for the credentials file
    credentials_file = os.path.join(credentials_dir, "oauth_credentials.json")
    os.makedirs(credentials_dir, exist_ok=True)
    with open(credentials_file, 'w') as f:
        f.write(oauth_credentials)

def create_service_account_credentials_file():
    sa_key = access_secret_version("jobportal-chatbot", "SERVICE_ACCOUNT_KEY")

    # Write the service account JSON to a temporary file
    with open('/tmp/google_credentials.json', 'w') as f:
        f.write(sa_key)

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/tmp/google_credentials.json"
