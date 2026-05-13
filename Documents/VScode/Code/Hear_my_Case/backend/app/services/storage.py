"""Storage helpers for local and S3 file uploads"""
from __future__ import annotations

import os
import uuid
from urllib.parse import urlparse
from pathlib import Path
from typing import BinaryIO, Optional

import boto3

from app.config import settings


def _has_s3_credentials() -> bool:
    return bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.AWS_S3_BUCKET)


def build_storage_key(prefix: str, original_name: str) -> str:
    suffix = Path(original_name).suffix
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    return f"{prefix.rstrip('/')}/{safe_name}"


def upload_to_s3(file_obj: BinaryIO, key: str, content_type: Optional[str] = None) -> str:
    client = boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    upload_kwargs = {
        "Fileobj": file_obj,
        "Bucket": settings.AWS_S3_BUCKET,
        "Key": key,
    }
    if extra_args:
        upload_kwargs["ExtraArgs"] = extra_args

    client.upload_fileobj(**upload_kwargs)

    return f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"


def save_locally(file_obj: BinaryIO, key: str) -> str:
    base_dir = Path(settings.UPLOAD_DIR)
    base_dir.mkdir(parents=True, exist_ok=True)
    target_path = base_dir / key
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with target_path.open("wb") as output:
        while True:
            chunk = file_obj.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)

    return f"/uploads/{key}"


def store_upload(file_obj: BinaryIO, key: str, content_type: Optional[str] = None) -> str:
    if _has_s3_credentials():
        return upload_to_s3(file_obj, key, content_type=content_type)
    return save_locally(file_obj, key)


def delete_stored_file(file_url: str) -> None:
    """Best-effort cleanup for stored files."""
    if file_url.startswith("/uploads/"):
        relative = file_url.removeprefix("/uploads/")
        path = Path(settings.UPLOAD_DIR) / relative
        if path.exists():
            path.unlink()
        return

    if file_url.startswith("http") and _has_s3_credentials():
        parsed = urlparse(file_url)
        key = parsed.path.lstrip("/")
        if key:
            client = boto3.client(
                "s3",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            client.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
