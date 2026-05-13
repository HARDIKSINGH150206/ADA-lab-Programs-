"""AI helpers for case analysis and evidence tagging"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def generate_case_analysis(case_data: dict[str, Any]) -> dict[str, Any]:
    """Generate structured legal guidance using Claude."""
    if not settings.ANTHROPIC_API_KEY:
        return _fallback_case_analysis(case_data)


async def summarize_evidence_text(text: str, file_name: str | None = None) -> str:
    """Generate a concise evidence summary."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return ""
    if not settings.ANTHROPIC_API_KEY:
        return cleaned[:280]

    prompt = f"""
Summarize this evidence text in 1-2 concise sentences for a legal case file.

File name: {file_name or "unknown"}
Text:
{cleaned[:8000]}

Return only the summary text.
"""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 256,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
        if response.status_code != 200:
            return cleaned[:280]
        content = response.json().get("content", [{}])[0].get("text", "").strip()
        return content or cleaned[:280]
    except Exception as exc:
        logger.debug("Evidence summary generation failed: %s", exc)
        return cleaned[:280]

    prompt = f"""
Analyze this legal case for an Indian worker and return JSON only:

Case Type: {case_data.get("case_type")}
Employer: {case_data.get("employer_name")}
Amount Owed: {case_data.get("amount_owed", "Not specified")}
Period: {case_data.get("period_start")} to {case_data.get("period_end")}
Contract Type: {case_data.get("contract_type", "Not specified")}
Evidence Count: {case_data.get("evidence_count", 0)}

Return:
{{
  "case_summary": "2-3 sentence summary",
  "applicable_laws": "Comma-separated relevant Indian labour laws",
  "what_should_happen": "Expected lawful outcome",
  "next_steps": ["Step 1", "Step 2", "Step 3"]
}}
"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )

        if response.status_code != 200:
            logger.error("Claude API error: %s", response.text)
            return {}

        content = response.json().get("content", [{}])[0].get("text", "{}")
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            content = content[start:end]
        return json.loads(content)
    except Exception as exc:
        logger.error("Failed to generate case analysis: %s", exc)
        return _fallback_case_analysis(case_data)


def infer_evidence_tags(file_name: str, mime_type: Optional[str]) -> tuple[str, float, list[str]]:
    """Infer a rough category and tags from filename and mime type."""
    name = file_name.lower()
    mime = (mime_type or "").lower()
    tags: list[str] = []

    if any(token in name for token in ("wage", "salary", "payslip", "pay slip")) or "pdf" in mime and "wage" in name:
        return "wage_slip", 0.92, ["wage", "salary", "financial"]
    if any(token in name for token in ("contract", "agreement", "offer")):
        return "contract", 0.9, ["contract", "employment", "agreement"]
    if any(token in name for token in ("msg", "message", "chat", "whatsapp", "screenshot")):
        return "message_screenshot", 0.86, ["message", "screenshot", "communication"]
    if any(token in name for token in ("photo", "image", "img", "receipt")) or mime.startswith("image/"):
        return "photo", 0.74, ["photo", "image", "visual"]
    if any(token in name for token in ("voice", "audio", "record", "call")) or mime.startswith("audio/"):
        return "voice_note", 0.8, ["audio", "voice", "recording"]
    if any(token in name for token in ("payment", "bank", "upi", "transaction", "transfer")):
        return "payment_record", 0.88, ["payment", "transaction", "bank"]

    tags.extend(["other"])
    return "other", 0.5, tags


def _fallback_case_analysis(case_data: dict[str, Any]) -> dict[str, Any]:
    case_type = case_data.get("case_type", "other")
    employer = case_data.get("employer_name", "the employer")
    amount = case_data.get("amount_owed")
    amount_text = f"₹{amount}" if amount else "the unpaid amount"
    return {
        "case_summary": f"This appears to be a {case_type.replace('_', ' ')} matter against {employer}. The worker reports an unresolved claim involving {amount_text}.",
        "applicable_laws": "Indian labour law, wage protection laws, and relevant state labour regulations",
        "what_should_happen": "The worker should receive a lawful resolution, including payment or corrective action depending on the facts.",
        "next_steps": [
            "Review the evidence and employment records",
            "Prepare a formal complaint or legal notice",
            "Escalate to the appropriate labour authority or counsel",
        ],
    }
