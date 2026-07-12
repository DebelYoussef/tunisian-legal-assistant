"""
PDF text extraction using PyMuPDF (fitz).
"""
import logging
from pathlib import Path
from typing import Iterator, NamedTuple

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PageText(NamedTuple):
    filename: str
    page_number: int  # 1-indexed
    text: str


def list_pdfs(pdf_dir: str) -> list[Path]:
    """Return all .pdf files in the given directory (non-recursive)."""
    directory = Path(pdf_dir)
    if not directory.exists():
        raise FileNotFoundError(f"PDF directory does not exist: {pdf_dir}")
    if not directory.is_dir():
        raise NotADirectoryError(f"PDF path is not a directory: {pdf_dir}")

    pdf_files = sorted(directory.glob("*.pdf"))
    logger.info("Found %d PDF file(s) in %s", len(pdf_files), pdf_dir)
    return pdf_files


def extract_pages(pdf_path: Path) -> Iterator[PageText]:
    """
    Yield (filename, page_number, text) for every non-empty page in the PDF.
    Raises an exception if the file cannot be opened; callers should catch
    per-file errors so one corrupt PDF doesn't abort the whole ingestion run.
    """
    doc = fitz.open(pdf_path)
    try:
        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            text = page.get_text("text").strip()
            if not text:
                logger.debug(
                    "Skipping empty page %d in %s", page_index + 1, pdf_path.name
                )
                continue
            yield PageText(
                filename=pdf_path.name,
                page_number=page_index + 1,
                text=text,
            )
    finally:
        doc.close()
