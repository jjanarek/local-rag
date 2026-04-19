import asyncio
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from core.embeddings import EmbeddingService
from core.processor import IngestionPipeline
from core.qdrant_store import QdrantStore

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def main():
    embedder = EmbeddingService()
    vector_store = QdrantStore(url="http://localhost:6333", collection_name="test_collection")

    pipeline = IngestionPipeline(vector_store=vector_store, embedder=embedder)

    logger.info("Starting ingestion...")
    test_file = Path("tests/data/test.pdf")
    result = await pipeline.ingest_file(test_file)
    logger.info(f"Ingestion Result: {result.status}")

    logger.info("Testing search...")
    test_query = "A few sentences"  # explicit content of the document page 1
    embedding = await embedder.embed_query(text=test_query)

    # perform the search
    document_hits = await vector_store.search(query_vector=embedding, limit=3)

    for i, chunk in enumerate(document_hits, 1):
        logger.info("###" * 8)
        logger.info(f"Hit {i}")
        logger.info(f"\tSource: {chunk.metadata.source}")
        logger.info(f"\tPage: {chunk.metadata.page_number}")
        logger.info(f"\tCountent snippet: {chunk.content[:100]}...")
        logger.info("###" * 8)
    await vector_store.close()


if __name__ == "__main__":
    asyncio.run(main())
