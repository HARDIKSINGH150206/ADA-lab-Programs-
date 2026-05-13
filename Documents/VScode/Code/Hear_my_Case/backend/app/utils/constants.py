"""Constants used throughout the application"""

# User Roles
USER_ROLE_WORKER = "worker"
USER_ROLE_LAWYER = "lawyer"
USER_ROLE_NGO_ADMIN = "ngo_admin"
USER_ROLE_SUPER_ADMIN = "super_admin"

USER_ROLES = [
    USER_ROLE_WORKER,
    USER_ROLE_LAWYER,
    USER_ROLE_NGO_ADMIN,
    USER_ROLE_SUPER_ADMIN,
]

# Case Types
CASE_TYPE_UNPAID_WAGES = "unpaid_wages"
CASE_TYPE_WORKPLACE_INJURY = "workplace_injury"
CASE_TYPE_HARASSMENT = "harassment"
CASE_TYPE_WRONGFUL_TERMINATION = "wrongful_termination"
CASE_TYPE_DISCRIMINATION = "discrimination"
CASE_TYPE_OTHER = "other"

CASE_TYPES = [
    CASE_TYPE_UNPAID_WAGES,
    CASE_TYPE_WORKPLACE_INJURY,
    CASE_TYPE_HARASSMENT,
    CASE_TYPE_WRONGFUL_TERMINATION,
    CASE_TYPE_DISCRIMINATION,
    CASE_TYPE_OTHER,
]

# Case Status
CASE_STATUS_DRAFT = "draft"
CASE_STATUS_INTAKE_COMPLETE = "intake_complete"
CASE_STATUS_REPORT_GENERATED = "report_generated"
CASE_STATUS_LAWYER_ASSIGNED = "lawyer_assigned"
CASE_STATUS_GROUP_ASSIGNED = "group_assigned"
CASE_STATUS_IN_PROGRESS = "in_progress"
CASE_STATUS_COMPLETED = "completed"
CASE_STATUS_CLOSED = "closed"

CASE_STATUSES = [
    CASE_STATUS_DRAFT,
    CASE_STATUS_INTAKE_COMPLETE,
    CASE_STATUS_REPORT_GENERATED,
    CASE_STATUS_LAWYER_ASSIGNED,
    CASE_STATUS_GROUP_ASSIGNED,
    CASE_STATUS_IN_PROGRESS,
    CASE_STATUS_COMPLETED,
    CASE_STATUS_CLOSED,
]

# Evidence Types
EVIDENCE_TYPE_WAGE_SLIP = "wage_slip"
EVIDENCE_TYPE_CONTRACT = "contract"
EVIDENCE_TYPE_MESSAGE = "message_screenshot"
EVIDENCE_TYPE_PHOTO = "photo"
EVIDENCE_TYPE_VOICE_NOTE = "voice_note"
EVIDENCE_TYPE_PAYMENT_RECORD = "payment_record"
EVIDENCE_TYPE_OTHER = "other"

EVIDENCE_TYPES = [
    EVIDENCE_TYPE_WAGE_SLIP,
    EVIDENCE_TYPE_CONTRACT,
    EVIDENCE_TYPE_MESSAGE,
    EVIDENCE_TYPE_PHOTO,
    EVIDENCE_TYPE_VOICE_NOTE,
    EVIDENCE_TYPE_PAYMENT_RECORD,
    EVIDENCE_TYPE_OTHER,
]

# Languages
LANGUAGE_ENGLISH = "en"
LANGUAGE_HINDI = "hi"
LANGUAGE_KANNADA = "kn"
LANGUAGE_TAMIL = "ta"
LANGUAGE_TELUGU = "te"

LANGUAGES = [
    LANGUAGE_ENGLISH,
    LANGUAGE_HINDI,
    LANGUAGE_KANNADA,
    LANGUAGE_TAMIL,
    LANGUAGE_TELUGU,
]

# States in India
INDIAN_STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
]
