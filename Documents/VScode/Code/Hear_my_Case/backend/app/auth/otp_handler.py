"""OTP handler for SMS verification"""
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Tuple
import redis
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Redis connection for OTP storage
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class OTPHandler:
    """Handle OTP generation, storage, and verification"""
    
    OTP_LENGTH = 6
    OTP_EXPIRY_KEY = "otp_expiry"
    OTP_ATTEMPTS_KEY = "otp_attempts"
    
    @staticmethod
    def generate_otp() -> str:
        """
        Generate a 6-digit OTP
        
        Returns:
            6-digit OTP as string
        """
        return "".join([str(random.randint(0, 9)) for _ in range(OTPHandler.OTP_LENGTH)])
    
    @staticmethod
    def store_otp(phone_number: str, otp: str) -> bool:
        """
        Store OTP in Redis with expiry
        
        Args:
            phone_number: User's phone number
            otp: OTP to store
            
        Returns:
            True if stored successfully
        """
        try:
            otp_key = f"otp:{phone_number}"
            attempts_key = f"otp_attempts:{phone_number}"
            
            # Store OTP with expiry in seconds
            redis_client.setex(
                otp_key,
                settings.OTP_EXPIRY_MINUTES * 60,
                otp
            )
            
            # Initialize attempts counter
            if not redis_client.exists(attempts_key):
                redis_client.setex(
                    attempts_key,
                    settings.OTP_EXPIRY_MINUTES * 60,
                    0
                )
            
            logger.info(f"OTP stored for phone: {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to store OTP: {e}")
            return False
    
    @staticmethod
    def verify_otp(phone_number: str, otp: str) -> Tuple[bool, str]:
        """
        Verify OTP against stored value
        
        Args:
            phone_number: User's phone number
            otp: OTP to verify
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            otp_key = f"otp:{phone_number}"
            attempts_key = f"otp_attempts:{phone_number}"
            
            # Check if OTP exists
            stored_otp = redis_client.get(otp_key)
            if not stored_otp:
                return False, "OTP expired or not found"
            
            # Check attempts
            attempts = int(redis_client.get(attempts_key) or 0)
            if attempts >= settings.MAX_OTP_ATTEMPTS:
                redis_client.delete(otp_key)
                redis_client.delete(attempts_key)
                return False, "Maximum OTP attempts exceeded. Please request a new OTP."
            
            # Verify OTP
            if stored_otp == otp:
                # OTP is correct, delete it
                redis_client.delete(otp_key)
                redis_client.delete(attempts_key)
                logger.info(f"OTP verified successfully for phone: {phone_number}")
                return True, "OTP verified successfully"
            else:
                # Increment attempts
                redis_client.incr(attempts_key)
                remaining = settings.MAX_OTP_ATTEMPTS - (attempts + 1)
                return False, f"Invalid OTP. {remaining} attempts remaining."
        
        except Exception as e:
            logger.error(f"OTP verification failed: {e}")
            return False, "OTP verification error"
    
    @staticmethod
    def get_otp_expiry_time(phone_number: str) -> Optional[int]:
        """
        Get remaining expiry time for OTP in seconds
        
        Args:
            phone_number: User's phone number
            
        Returns:
            Remaining time in seconds, or None if not found
        """
        try:
            otp_key = f"otp:{phone_number}"
            ttl = redis_client.ttl(otp_key)
            return ttl if ttl > 0 else None
        except Exception as e:
            logger.error(f"Failed to get OTP expiry: {e}")
            return None
    
    @staticmethod
    def resend_otp(phone_number: str, max_resends: int = 3) -> Tuple[str, str]:
        """
        Resend OTP to user
        
        Args:
            phone_number: User's phone number
            max_resends: Maximum number of resends allowed
            
        Returns:
            Tuple of (otp, message)
        """
        try:
            resend_key = f"otp_resends:{phone_number}"
            resends = int(redis_client.get(resend_key) or 0)
            
            if resends >= max_resends:
                return "", "Maximum resends exceeded. Please try after some time."
            
            # Generate and store new OTP
            new_otp = OTPHandler.generate_otp()
            OTPHandler.store_otp(phone_number, new_otp)
            
            # Increment resend counter
            redis_client.incr(resend_key)
            redis_client.expire(resend_key, settings.OTP_EXPIRY_MINUTES * 60)
            
            logger.info(f"OTP resent for phone: {phone_number}")
            return new_otp, "OTP resent successfully"
        except Exception as e:
            logger.error(f"OTP resend failed: {e}")
            return "", "Failed to resend OTP"
