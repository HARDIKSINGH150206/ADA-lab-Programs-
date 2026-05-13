"""Service layer for business logic"""
from app.services.ai import generate_case_analysis, infer_evidence_tags
from app.services.ai import summarize_evidence_text
from app.services.evidence import store_evidence_file, EvidenceUploadResult
from app.services.notifications import create_notification, mark_all_notifications_read
from app.services.ocr import extract_text_from_file
from app.services.sms import send_otp_sms
from app.services.demo import seed_demo_data
from app.services.storage import build_storage_key, store_upload

__all__ = [
    "generate_case_analysis",
    "infer_evidence_tags",
    "summarize_evidence_text",
    "store_evidence_file",
    "EvidenceUploadResult",
    "create_notification",
    "mark_all_notifications_read",
    "extract_text_from_file",
    "send_otp_sms",
    "seed_demo_data",
    "build_storage_key",
    "store_upload",
]
