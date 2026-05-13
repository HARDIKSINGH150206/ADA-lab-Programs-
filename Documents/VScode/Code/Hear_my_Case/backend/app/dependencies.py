"""Dependency injection setup"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

__all__ = ["get_db"]
