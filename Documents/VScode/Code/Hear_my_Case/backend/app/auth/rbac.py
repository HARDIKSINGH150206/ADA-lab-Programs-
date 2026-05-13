"""Role-Based Access Control (RBAC) for authorization"""
from typing import List, Optional
from fastapi import HTTPException, status
from functools import wraps
from app.models.user import UserRole
import logging

logger = logging.getLogger(__name__)


def require_role(*allowed_roles: UserRole):
    """
    Decorator to check if user has required role
    
    Args:
        allowed_roles: Roles allowed to access endpoint
        
    Usage:
        @require_role(UserRole.WORKER, UserRole.LAWYER)
        async def my_endpoint(current_user = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )
            
            user_role = current_user.get("role")
            if user_role not in [role.value for role in allowed_roles]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}",
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


def check_role(user_role: str, required_roles: List[str]) -> bool:
    """
    Check if user role is in required roles list
    
    Args:
        user_role: User's role
        required_roles: List of required roles
        
    Returns:
        True if user has one of the required roles
    """
    return user_role in required_roles


class RBACException(HTTPException):
    """Custom exception for RBAC violations"""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def check_user_owns_resource(user_id: str, resource_user_id: str) -> bool:
    """
    Check if user owns the resource (for user isolation)
    
    Args:
        user_id: Authenticated user ID
        resource_user_id: Owner of the resource
        
    Returns:
        True if user owns the resource
    """
    return user_id == resource_user_id


def ensure_user_owns_resource(user_id: str, resource_user_id: str) -> None:
    """
    Ensure user owns the resource, raise exception if not
    
    Args:
        user_id: Authenticated user ID
        resource_user_id: Owner of the resource
        
    Raises:
        HTTPException: If user doesn't own the resource
    """
    if not check_user_owns_resource(user_id, resource_user_id):
        logger.warning(f"User {user_id} attempted to access resource owned by {resource_user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource",
        )


# Role hierarchies (admin > lawyer > worker)
ROLE_HIERARCHY = {
    "super_admin": 4,
    "ngo_admin": 3,
    "lawyer": 2,
    "worker": 1,
}


def check_role_hierarchy(user_role: str, min_role: str) -> bool:
    """
    Check if user role meets minimum role requirement
    
    Args:
        user_role: User's role
        min_role: Minimum required role
        
    Returns:
        True if user role meets minimum requirement
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    min_level = ROLE_HIERARCHY.get(min_role, 0)
    return user_level >= min_level
