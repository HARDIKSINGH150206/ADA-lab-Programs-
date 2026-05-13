"""Demo/bootstrap endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.services.demo import seed_demo_data

router = APIRouter(prefix="/api/demo", tags=["demo"])


def _ensure_demo_mode() -> None:
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo endpoints disabled")


@router.get("/status")
async def demo_status():
    """Return demo mode status and bootstrap configuration."""
    _ensure_demo_mode()
    return {
        "demo_mode": True,
        "auto_seed_demo_data": settings.AUTO_SEED_DEMO_DATA,
        "message": "Demo endpoints enabled",
    }


@router.post("/bootstrap")
async def bootstrap_demo(db: AsyncSession = Depends(get_db)):
    """Seed demo data on demand."""
    _ensure_demo_mode()
    return await seed_demo_data(db)

