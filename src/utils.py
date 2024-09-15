import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import src.constants as con

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