"""API route modules"""
from app.api import auth
from app.api import users
from app.api import cases
from app.api import evidence
from app.api import notifications
from app.api import admin
from app.api import demo

__all__ = ["auth", "users", "cases", "evidence", "notifications", "admin", "demo"]
