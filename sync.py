from openai import OpenAI
from pinecone import Pinecone

import config
from googleapiclient.discovery import build
from google.oauth2 import service_account

pc = Pinecone(
    api_key=config.PINECONE_API_KEY
)

openai = OpenAI(
    api_key=config.OPENAI_API_KEY
)

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        config.SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return build('drive', 'v3', credentials=creds)

def list_drive_files():
    service = get_drive_service()
    results = service.files().list(
        q=f"'{config.GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed = false",
        fields="files(id, name, mimeType)"
    ).execute()
    return results.get('files', [])

def extract_doc_text(file_id: str) -> str:
    service = get_drive_service()
    doc = service.files().export(
        fileId=file_id,
        mimeType='text/plain'
    ).execute()
    return doc.decode('utf-8')


if __name__ == "__main__":
    files = list_drive_files()

    for file in files:
        try:
            content = extract_doc_text(file['id'])
            print(f"Processing file: {file['name']}")
            # log the content
            print(f"Content of {file['name']}:\n{content[:500]}...")  # Print first 500 chars for brevity


        except Exception as e:
            print(f"Failed to process {file['name']}: {str(e)}")
