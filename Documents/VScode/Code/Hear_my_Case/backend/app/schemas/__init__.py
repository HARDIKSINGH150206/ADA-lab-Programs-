"""Pydantic schemas for request/response validation"""
from app.schemas.auth import (
    RegisterRequest,
    VerifyOTPRequest,
    SendOTPRequest,
    LoginRequest,
    RefreshTokenRequest,
    OTPResponse,
    TokenResponse,
    UserResponse,
    LoginResponse,
    MessageResponse,
)
from app.schemas.cases import (
    CreateCaseRequest,
    UpdateCaseRequest,
    CaseResponse,
    CaseListResponse,
    CaseStepResponse,
)
from app.schemas.users import (
    UserProfileUpdateRequest,
    UserAdminUpdateRequest,
    UserListResponse,
)
from app.schemas.evidence import (
    EvidenceResponse,
    EvidenceListResponse,
    EvidenceMetadataResponse,
    EvidenceUpdateRequest,
)
from app.schemas.notifications import (
    NotificationResponse,
    NotificationListResponse,
    NotificationCreateRequest,
    NotificationUpdateRequest,
)
from app.schemas.resources import (
    GroupCreateRequest,
    GroupUpdateRequest,
    GroupResponse,
    LawyerCreateRequest,
    LawyerUpdateRequest,
    LawyerResponse,
    NGOCreateRequest,
    NGOUpdateRequest,
    NGOResponse,
)
