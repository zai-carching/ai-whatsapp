from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import logging
import time
import config
from googleapiclient.discovery import build
from google.oauth2 import service_account
import utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

pc = Pinecone(
    api_key=config.PINECONE_API_KEY
)

openai = OpenAI(
    api_key=config.OPENAI_API_KEY
)

if pc.has_index("testo-1"):
    logger.info("Deleting existing index 'testo-1'")
    pc.delete_index("testo-1")

logger.info("Creating new Pinecone index 'testo-1'")
pc.create_index("testo-1", dimension=1536, metric="cosine", spec=ServerlessSpec(cloud="aws", region="us-east-1"))

index = pc.Index("testo-1")


def get_drive_service():
    logger.debug("Initializing Google Drive service")
    creds = service_account.Credentials.from_service_account_file(
        config.SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return build('drive', 'v3', credentials=creds)


def list_drive_files():
    logger.info("Fetching files from Google Drive folder")
    service = get_drive_service()
    results = service.files().list(
        q=f"'{config.GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed = false",
        fields="files(id, name, mimeType)"
    ).execute()
    files = results.get('files', [])
    logger.info(f"Found {len(files)} files in Drive folder")
    return files


def extract_doc_text(file_id: str) -> str:
    logger.debug(f"Extracting text content from file ID: {file_id}")
    service = get_drive_service()
    doc = service.files().export(
        fileId=file_id,
        mimeType='text/plain'
    ).execute()
    return doc.decode('utf-8')


def create_embedding(text: str):
    logger.debug("Generating embedding")
    response = openai.embeddings.create(
        model=config.EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding


def upsert_to_pinecone(file_id, file_name, chunks):
    """Store chunks in Pinecone with metadata"""
    start_time = time.time()
    logger.info(f"Processing {len(chunks)} chunks for file: {file_name}")

    vectors = []
    for idx, chunk in enumerate(chunks):
        vectors.append({
            'id': f"{file_id}_{idx}",
            'values': create_embedding(chunk),
            'metadata': {
                'text': chunk,
                'source': 'google-drive',
                'file_id': file_id,
                'file_name': file_name,
                'chunk_num': idx
            }
        })

        if (idx + 1) % 10 == 0:
            logger.debug(f"Processed {idx + 1}/{len(chunks)} chunks")

    # Batch upsert
    total_batches = (len(vectors) + 99) // 100
    for i in range(0, len(vectors), 100):
        batch = vectors[i:i + 100]
        current_batch = (i // 100) + 1
        logger.debug(f"Upserting batch {current_batch}/{total_batches}")
        index.upsert(vectors=batch)

    elapsed_time = time.time() - start_time
    logger.info(f"Completed processing {file_name} in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    logger.info("Starting document processing")
    files = list_drive_files()

    for file in files:
        try:
            logger.info(f"Processing file: {file['name']} (ID: {file['id']})")
            content = extract_doc_text(file['id'])

            chunks = utils.split_text(content)
            logger.info(f"Split {file['name']} into {len(chunks)} chunks")

            upsert_to_pinecone(file['id'], file['name'], chunks)
            logger.info(f"Successfully indexed {file['name']}")

        except Exception as e:
            logger.error(f"Failed to process {file['name']}: {str(e)}", exc_info=True)

    logger.info("Document processing completed")