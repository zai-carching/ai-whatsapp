from typing import Tuple

from flask import Blueprint
import config
from app.utils import friday
from app.utils import gdoc
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import logging
import time

sync_blueprint = Blueprint("sync", __name__)
logger = logging.getLogger(__name__)

pc = Pinecone(
    api_key=config.PINECONE_API_KEY
)

openai = OpenAI(
    api_key=config.OPENAI_API_KEY
)


def create_embedding(text: str):
    logger.debug("Generating embedding")
    response = openai.embeddings.create(
        model=config.EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding


def sync_api_data(index_name: str, contexts: list[Tuple[str, str]]) -> None:
    index = pc.Index(index_name)

    logger.info("Starting API data synchronization")

    for name, content in contexts:
        try:
            logger.info(f"Processing context: {name}")
            chunks = gdoc.split_text(content)
            logger.info(f"Split context '{name}' into {len(chunks)} chunks")
            vectors = []
            for idx, chunk in enumerate(chunks):
                vectors.append({
                    'id': f"{name}_{idx}",
                    'values': create_embedding(chunk),
                    'metadata': {
                        'text': chunk,
                        'source': 'database',
                        'name': name,
                        'chunk_num': idx
                    }
                })

                if (idx + 1) % 10 == 0:
                    logger.debug(f"Processed {idx + 1}/{len(chunks)} chunks for context '{name}'")
            # Batch upsert
            total_batches = (len(vectors) + 99) // 100
            for i in range(0, len(vectors), 100):
                batch = vectors[i:i + 100]
                current_batch = (i // 100) + 1
                logger.debug(f"Upserting batch {current_batch}/{total_batches} for context '{name}'")
                index.upsert(vectors=batch)

            logger.info(f"Successfully indexed context '{name}'")

        except Exception as e:
            logger.error(f"Failed to process context {name}: {str(e)}", exc_info=True)



def sync_docs_data(index_name: str) -> None:
    index = pc.Index(index_name)

    logger.info("Starting document processing")
    files = gdoc.list_drive_files()

    for file in files:
        try:
            logger.info(f"Processing file: {file['name']} (ID: {file['id']})")
            content = gdoc.extract_doc_text(file['id'])

            chunks = gdoc.split_text(content)
            logger.info(f"Split {file['name']} into {len(chunks)} chunks")

            file_id, file_name = file['id'], file['name']

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
            logger.info(f"Successfully indexed {file['name']}")

        except Exception as e:
            logger.error(f"Failed to process {file['name']}: {str(e)}", exc_info=True)

@sync_blueprint.route('/sync', methods=['POST'])
def handle_sync():
    demo_index = config.DEMO_INDEX_NAME
    actual_index = config.INDEX_NAME

    try:
        if pc.has_index(demo_index):
            logger.info(f"Deleting existing index '{demo_index}'")
            pc.delete_index(demo_index)

        logger.info(f"Creating new Pinecone index '{demo_index}'")
        pc.create_index(demo_index, dimension=1536, metric="cosine", spec=ServerlessSpec(cloud="aws", region="us-east-1"))

        contexts = friday.get_ai_context()
        sync_api_data(demo_index, contexts)
        sync_docs_data(demo_index)
    except Exception as e:
        logger.error(f"Failed to sync demo index: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Demo index sync failed: {str(e)}"}, 500

    try:
        if pc.has_index(actual_index):
            logger.info(f"Deleting existing index '{actual_index}'")
            pc.delete_index(actual_index)

        logger.info(f"Creating new Pinecone index '{actual_index}'")
        pc.create_index(actual_index, dimension=1536, metric="cosine", spec=ServerlessSpec(cloud="aws", region="us-east-1"))

        contexts = friday.get_ai_context()
        sync_api_data(actual_index, contexts)
        sync_docs_data(actual_index)
    except Exception as e:
        logger.error(f"Failed to sync actual index: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Actual index sync failed: {str(e)}"}, 500

    return {"status": "success", "message": "Data synchronized successfully"}, 200