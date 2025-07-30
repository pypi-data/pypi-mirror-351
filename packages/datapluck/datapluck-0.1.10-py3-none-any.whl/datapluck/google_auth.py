import os
import pickle
from pathlib import Path
from shutil import rmtree
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_user_config_dir():
    if os.name == "nt":  # Windows
        return Path(os.environ.get("APPDATA", "")) / "DataPluck"
    else:  # Unix-like
        return (
            Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
            / "datapluck"
        )


USER_CONFIG_DIR = get_user_config_dir()
TOKEN_FILE = USER_CONFIG_DIR / "token.pickle"

CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"

USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        with TOKEN_FILE.open("rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Credentials file not found. This file should be packaged with the tool."
                )

            flow = Flow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
            )
            auth_url, _ = flow.authorization_url(prompt="consent")

            print("Please go to this URL: {}".format(auth_url))
            code = input("Enter the authorization code: ")
            flow.fetch_token(code=code)

            session = flow.authorized_session()
            creds = flow.credentials
            print(session.get("https://www.googleapis.com/userinfo/v2/me").json())

        with TOKEN_FILE.open("wb") as token:
            pickle.dump(creds, token)

    return creds


def connect_gsheet():
    creds = get_credentials()
    # Here we're just getting the credentials, not returning a service object
    return creds


def get_sheets_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)
