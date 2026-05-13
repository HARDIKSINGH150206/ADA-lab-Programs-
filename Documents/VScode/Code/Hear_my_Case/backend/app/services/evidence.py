"""Evidence service helpers"""
from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Optional

from fastapi import UploadFile

from app.services.ai import infer_evidence_tags, summarize_evidence_text
from app.services.ocr import extract_text_from_file
from app.services.storage import build_storage_key, store_upload


@dataclass
class EvidenceUploadResult:
    file_url: str
    file_size: int
    category: str
    confidence_score: float
    tags: list[str]
    extracted_text: str
    ai_summary: str


async def store_evidence_file(upload_file: UploadFile, max_size_bytes: int | None = None) -> EvidenceUploadResult:
    """Persist an evidence file and infer metadata."""
    key = build_storage_key("evidence", upload_file.filename or "upload.bin")
    raw = await upload_file.read()
    file_size = len(raw)
    if max_size_bytes is not None and file_size > max_size_bytes:
        raise ValueError("File exceeds maximum allowed size")
    file_obj = io.BytesIO(raw)
    file_url = store_upload(file_obj, key, content_type=upload_file.content_type)
    category, confidence, tags = infer_evidence_tags(upload_file.filename or "upload.bin", upload_file.content_type)
    extracted_text = extract_text_from_file(upload_file.filename or "upload.bin", upload_file.content_type, raw)
    ai_summary = await summarize_evidence_text(extracted_text, upload_file.filename) if extracted_text else ""
    return EvidenceUploadResult(
        file_url=file_url,
        file_size=file_size,
        category=category,
        confidence_score=confidence,
        tags=tags,
        extracted_text=extracted_text,
        ai_summary=ai_summary,
    )
