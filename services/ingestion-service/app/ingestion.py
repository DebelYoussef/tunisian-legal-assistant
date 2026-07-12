"""
Orchestrates the full ingestion pipeline:
  read PDFs -> extract text per page -> chunk -> embed -> upsert to Qdrant

Designed so that a single corrupt/unreadable PDF does not abort the whole run;
failures are collected and reported back in the response.
"""
import logging
import time
from dataclasses import dataclass, field

from app.config import settings
from app.embeddings import chunk_text, embed_passages, get_embedding_dimension
from app.pdf_processor import extract_pages, list_pdfs
from app.qdrant_store import ensure_collection, upsert_chunks

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    files_processed: int = 0
    chunks_ingested: int = 0
    files_failed: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


def run_ingestion() -> IngestionResult:
    """
    Synchronously run the full ingestion pipeline over every PDF in
    settings.pdf_dir. Safe to call repeatedly (re-ingests / duplicates
    points on each run unless the caller clears the collection first).
    """
    start_time = time.monotonic()
    result = IngestionResult()

    pdf_paths = list_pdfs(settings.pdf_dir)
    if not pdf_paths:
        logger.warning("No PDF files found in %s. Nothing to ingest.", settings.pdf_dir)
        result.duration_seconds = time.monotonic() - start_time
        return result

    # Ensure the Qdrant collection exists before we try to write to it.
    vector_size = get_embedding_dimension()
    ensure_collection(vector_size)

    for pdf_path in pdf_paths:
        try:
            _ingest_single_pdf(pdf_path, result)
            result.files_processed += 1
        except Exception as exc:
            logger.exception("Failed to ingest '%s': %s", pdf_path.name, exc)
            result.files_failed.append(pdf_path.name)

    result.duration_seconds = time.monotonic() - start_time
    logger.info(
        "Ingestion complete: %d file(s) processed, %d chunk(s) ingested, "
        "%d file(s) failed, took %.2fs",
        result.files_processed,
        result.chunks_ingested,
        len(result.files_failed),
        result.duration_seconds,
    )
    return result


def _ingest_single_pdf(pdf_path, result: IngestionResult) -> None:
    logger.info("Processing '%s'...", pdf_path.name)

    chunk_index = 0
    for page in extract_pages(pdf_path):
        chunks = chunk_text(page.text)
        if not chunks:
            continue

        try:
            embeddings = embed_passages(chunks)
        except Exception as exc:
            logger.error(
                "Embedding generation failed for %s page %d: %s",
                page.filename,
                page.page_number,
                exc,
            )
            raise

        filenames = [page.filename] * len(chunks)
        page_numbers = [page.page_number] * len(chunks)
        chunk_indices = list(range(chunk_index, chunk_index + len(chunks)))
        chunk_index += len(chunks)

        try:
            upserted = upsert_chunks(
                texts=chunks,
                embeddings=embeddings,
                filenames=filenames,
                page_numbers=page_numbers,
                chunk_indices=chunk_indices,
            )
        except Exception as exc:
            logger.error(
                "Qdrant upsert failed for %s page %d: %s",
                page.filename,
                page.page_number,
                exc,
            )
            raise

        result.chunks_ingested += upserted

    logger.info("Finished '%s': %d chunk(s) so far.", pdf_path.name, chunk_index)
