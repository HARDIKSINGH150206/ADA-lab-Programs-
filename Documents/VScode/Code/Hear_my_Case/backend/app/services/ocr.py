"""Optional OCR and text extraction helpers."""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_file(filename: str, content_type: Optional[str], raw_bytes: bytes) -> str:
    """Extract text from PDFs, images, or plain files when possible."""
    suffix = Path(filename or "").suffix.lower()
    mime = (content_type or "").lower()

    if suffix == ".pdf" or "pdf" in mime:
        text = _extract_pdf_text(raw_bytes)
        if text:
            return text

    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"} or mime.startswith("image/"):
        text = _extract_image_text(raw_bytes)
        if text:
            return text

    return _extract_plain_text(raw_bytes)


def _extract_pdf_text(raw_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        logger.debug("pypdf not available; skipping PDF extraction")
        return ""

    try:
        reader = PdfReader(io.BytesIO(raw_bytes))
        parts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                parts.append(page_text.strip())
        return "\n\n".join(parts).strip()
    except Exception as exc:
        logger.warning("PDF extraction failed: %s", exc)
        return ""


def _extract_image_text(raw_bytes: bytes) -> str:
    try:
        from PIL import Image
    except Exception:
        logger.debug("Pillow not available; skipping image OCR")
        return ""

    try:
        import pytesseract
    except Exception:
        logger.debug("pytesseract not available; skipping image OCR")
        return ""

    try:
        image = Image.open(io.BytesIO(raw_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as exc:
        logger.warning("Image OCR failed: %s", exc)
        return ""


def _extract_plain_text(raw_bytes: bytes) -> str:
    try:
        return raw_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        try:
            return raw_bytes.decode("latin-1").strip()
        except Exception:
            return ""

