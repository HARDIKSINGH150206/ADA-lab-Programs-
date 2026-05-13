"""Authentication API routes"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import bcrypt
import logging

from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    RegisterRequest,
    VerifyOTPRequest,
    SendOTPRequest,
    LoginRequest,
    RefreshTokenRequest,
    OTPResponse,
    TokenResponse,
    LoginResponse,
    UserResponse,
    MessageResponse,
)
from app.auth.jwt_handler import JWTHandler, get_current_user
from app.auth.otp_handler import OTPHandler
from app.services.sms import send_otp_sms
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# ==================== REGISTRATION FLOW ====================

@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(request: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Send OTP to phone number
    
    - **phone_number**: User's phone number (10-15 digits)
    
    Returns OTP expiry time in seconds
    """
    phone_number = request.phone_number
    
    try:
        # Check if user already exists
        stmt = select(User).where(User.phone_number == phone_number)
        result = await db.execute(stmt)
        existing_user = result.scalars().first()
        
        if existing_user and existing_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered with this phone number",
            )
        
        # Generate and store OTP
        otp = OTPHandler.generate_otp()
        OTPHandler.store_otp(phone_number, otp)
        sms_sent = send_otp_sms(phone_number, otp)

        # Log for development (remove in production)
        if not sms_sent:
            logger.info(f"Generated OTP for {phone_number}: {otp}")

        expiry_time = OTPHandler.get_otp_expiry_time(phone_number) or 300
        
        return OTPResponse(
            success=True,
            message="OTP sent successfully",
            expires_in_seconds=expiry_time,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP",
        )


@router.post("/register", response_model=MessageResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register user with phone and password
    
    Note: User must have verified phone with OTP first
    """
    phone_number = request.phone_number
    
    try:
        # Check if user exists
        stmt = select(User).where(User.phone_number == phone_number)
        result = await db.execute(stmt)
        existing_user = result.scalars().first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        if request.email:
            stmt = select(User).where(User.email == request.email)
            result = await db.execute(stmt)
            if result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use",
                )
        
        # Create new user
        new_user = User(
            id=uuid.uuid4(),
            phone_number=phone_number,
            full_name=request.full_name,
            email=request.email,
            password_hash=hash_password(request.password),
            role=UserRole.WORKER,
            is_active=True,
            is_verified=False,
            state=request.state,
        )
        
        db.add(new_user)
        await db.commit()
        
        logger.info(f"User registered: {phone_number}")
        
        return MessageResponse(
            success=True,
            message="User registered successfully. Please verify OTP to complete registration.",
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Verify OTP and complete registration
    
    Returns JWT access and refresh tokens
    """
    phone_number = request.phone_number
    otp = request.otp
    
    try:
        # Verify OTP
        is_valid, message = OTPHandler.verify_otp(phone_number, otp)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )
        
        # Get user and mark as verified
        stmt = select(User).where(User.phone_number == phone_number)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        user.is_verified = True
        await db.commit()
        
        # Generate tokens
        access_token = JWTHandler.create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        refresh_token = JWTHandler.create_refresh_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        
        logger.info(f"User verified: {phone_number}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in_seconds=3600,  # 1 hour
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"OTP verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP",
        )


# ==================== LOGIN FLOW ====================

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login with phone and password
    
    Returns user info and JWT tokens
    """
    phone_number = request.phone_number
    password = request.password
    
    try:
        # Get user
        stmt = select(User).where(User.phone_number == phone_number)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        
        # Verify password
        if not user.password_hash or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        
        # Check if user is verified
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not verified. Please verify OTP first.",
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive",
            )
        
        # Generate tokens
        access_token = JWTHandler.create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        refresh_token = JWTHandler.create_refresh_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        
        logger.info(f"User logged in: {phone_number}")
        
        return LoginResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


# ==================== TOKEN MANAGEMENT ====================

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    
    Returns new access and refresh tokens
    """
    try:
        payload = JWTHandler.verify_token(request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        user_id = payload.get("sub")
        role = payload.get("role")
        
        # Generate new tokens
        new_access_token = JWTHandler.create_access_token(
            data={"sub": user_id, "role": role}
        )
        new_refresh_token = JWTHandler.create_refresh_token(
            data={"sub": user_id, "role": role}
        )
        
        logger.info(f"Tokens refreshed for user: {user_id}")
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in_seconds=3600,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token",
        )


# ==================== LOGOUT ====================

@router.post("/logout", response_model=MessageResponse)
async def logout(current_user = Depends(get_current_user)):
    """
    Logout user
    
    Note: JWT tokens are stateless, so logout is just a client-side operation.
    Implement token blacklisting if needed.
    """
    logger.info(f"User logged out: {current_user.get('sub')}")
    
    return MessageResponse(
        success=True,
        message="Logged out successfully",
    )


# ==================== VERIFY CURRENT USER ====================

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user's profile
    """
    user_id = current_user.get("sub")
    
    try:
        user_uuid = uuid.UUID(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user id in token",
        )

    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user)
