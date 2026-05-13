"""Authentication and authorization module"""
from app.auth.jwt_handler import JWTHandler, get_current_user, get_current_user_optional
from app.auth.otp_handler import OTPHandler
from app.auth.rbac import require_role, check_role, ensure_user_owns_resource

__all__ = [
    "JWTHandler",
    "OTPHandler",
    "get_current_user",
    "get_current_user_optional",
    "require_role",
    "check_role",
    "ensure_user_owns_resource",
]
