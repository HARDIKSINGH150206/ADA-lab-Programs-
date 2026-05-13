# Case Management API - Implementation Guide

## Overview

This document explains the complete implementation of the Case Management API for the "Hear My Case" application, including architecture, features, and integration details.

## Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
├─────────────────────────────────────────┤
│         Authentication (JWT)             │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐   │
│  │   Case Management API Routes    │   │
│  │  (POST, GET, PATCH, DELETE)    │   │
│  └─────────────────────────────────┘   │
│                                          │
│  ┌─────────────────────────────────┐   │
│  │   AI Analysis Service           │   │
│  │  (Claude API Integration)       │   │
│  └─────────────────────────────────┘   │
├─────────────────────────────────────────┤
│         Database Layer                   │
│     (AsyncSQLAlchemy + PostgreSQL)      │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────┐  │
│  │  Case Model │  │  CaseStep Model │  │
│  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
```

## File Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py (updated - includes cases)
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── cases.py (NEW - 380+ lines)
│   ├── models/
│   │   ├── case.py (existing - Case, CaseStep models)
│   │   └── ...
│   ├── schemas/
│   │   ├── cases.py (existing - request/response schemas)
│   │   └── ...
│   ├── auth/
│   │   └── jwt_handler.py (existing - JWT handling)
│   ├── config.py (existing - has ANTHROPIC_API_KEY)
│   ├── main.py (updated - includes cases router)
│   └── ...
├── API_DOCUMENTATION.md (NEW - comprehensive API guide)
├── IMPLEMENTATION_GUIDE.md (NEW - this file)
└── test_cases_api.py (NEW - API test examples)
```

## Core Components

### 1. Case Model (`app/models/case.py`)

```python
class Case(Base):
    __tablename__ = "cases"
    
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    case_type = Column(Enum(CaseType))
    status = Column(Enum(CaseStatus))
    
    # Case details
    employer_name = Column(String)
    amount_owed = Column(Float)
    period_start = Column(String)
    period_end = Column(String)
    contract_type = Column(String)
    
    # AI-generated content
    case_summary = Column(JSONB)
    applicable_laws = Column(Text)
    what_should_happen = Column(Text)
    next_steps = Column(JSONB)
    
    # Relationships
    group_id = Column(UUID, ForeignKey("groups.id"))
    lawyer_id = Column(UUID, ForeignKey("lawyers.id"))
    
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

### 2. CaseStep Model

Represents milestones/steps in a case's progress:

```python
class CaseStep(Base):
    __tablename__ = "case_steps"
    
    id = Column(UUID, primary_key=True)
    case_id = Column(UUID, ForeignKey("cases.id"))
    step_number = Column(String)
    title = Column(String)
    description = Column(Text)
    status = Column(String)  # pending, in_progress, completed
    
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

### 3. Schemas (`app/schemas/cases.py`)

**Request Schemas:**
- `CreateCaseRequest` - Create new case
- `UpdateCaseRequest` - Update case fields

**Response Schemas:**
- `CaseResponse` - Single case
- `CaseListResponse` - Paginated list
- `CaseStepResponse` - Case step

### 4. API Routes (`app/api/cases.py`)

#### CRUD Operations

```python
# Create
POST /api/cases
- Input: CreateCaseRequest
- Output: CaseResponse
- Status: 201 Created

# Read
GET /api/cases
- Query: skip, limit, case_type, status, search
- Output: CaseListResponse
- Status: 200 OK

GET /api/cases/{case_id}
- Output: CaseResponse
- Status: 200 OK or 404 Not Found

# Update
PATCH /api/cases/{case_id}
- Input: UpdateCaseRequest
- Output: CaseResponse
- Status: 200 OK

# Delete
DELETE /api/cases/{case_id}
- Output: MessageResponse
- Status: 200 OK
```

#### AI Analysis

```python
# Analyze case with Claude AI
POST /api/cases/{case_id}/analyze
- Calls Claude API with case details
- Generates: case_summary, applicable_laws, what_should_happen, next_steps
- Updates case status to REPORT_GENERATED
- Output: CaseResponse
- Status: 200 OK or 500 Internal Server Error
```

#### Case Steps

```python
# Get all steps for a case
GET /api/cases/{case_id}/steps
- Output: List[CaseStep]
- Status: 200 OK

# Update step status
PATCH /api/cases/{case_id}/steps/{step_id}
- Query: status (pending|in_progress|completed)
- Output: MessageResponse
- Status: 200 OK
```

## AI Integration

### Claude API Integration

The `/analyze` endpoint integrates with Anthropic's Claude API to generate intelligent legal analysis.

**Prompt Design:**
```
Analyze this legal case and provide comprehensive guidance for an Indian worker:

Case Type: {case_type}
Employer: {employer_name}
Amount Owed: ₹{amount_owed}
Period: {period_start} to {period_end}
Contract Type: {contract_type}

Please provide in JSON format:
{
    "case_summary": "2-3 sentence summary",
    "applicable_laws": "Comma-separated Indian labor laws",
    "what_should_happen": "Expected outcome",
    "next_steps": ["Step 1", "Step 2", "Step 3"]
}

Be specific to Indian labor laws and worker rights.
```

**Configuration:**
- Model: `claude-3-5-sonnet-20241022`
- Max tokens: 1024
- API Key: From `ANTHROPIC_API_KEY` environment variable
- Timeout: 30 seconds

**Error Handling:**
- Logs API failures
- Returns empty dict on error
- Returns 500 error to client if analysis fails

### Response Parsing

The API extracts JSON from Claude's response, handling cases where Claude includes extra text:

```python
json_start = content.find("{")
json_end = content.rfind("}") + 1
if json_start != -1 and json_end > json_start:
    content = content[json_start:json_end]
analysis = json.loads(content)
```

## Security Features

### 1. Authentication

All endpoints require JWT authentication:
- Check Bearer token in Authorization header
- Validate token signature and expiration
- Extract user ID from token

### 2. Authorization

User ownership validation:
- Users can only access their own cases
- 403 Forbidden returned for unauthorized access
- User ID comparison: `str(case.user_id) != current_user["sub"]`

### 3. Input Validation

Pydantic validation on all requests:
- Type checking
- Length constraints
- Pattern validation (dates)
- Custom validators

### 4. Error Handling

Proper HTTP status codes:
- 201 Created - Successful creation
- 200 OK - Successful operation
- 400 Bad Request - Invalid input
- 403 Forbidden - Unauthorized access
- 404 Not Found - Resource not found
- 500 Internal Server Error - Server error

## Database Design

### Relationships

```
User (1) ───────→ (Many) Case
Group (1) ───────→ (Many) Case
Lawyer (1) ───────→ (Many) Case
Case (1) ───────→ (Many) CaseStep
```

### Indexing

```python
# Indexed columns for fast queries
Case.user_id - index for user's cases lookup
Case.case_type - filter by type
Case.status - filter by status
CaseStep.case_id - get steps for a case
```

### Migrations Required

If creating fresh database:

```sql
CREATE TABLE cases (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    case_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    employer_name VARCHAR(255) NOT NULL,
    amount_owed FLOAT,
    period_start VARCHAR(10),
    period_end VARCHAR(10),
    contract_type VARCHAR(50),
    case_summary JSONB,
    applicable_laws TEXT,
    what_should_happen TEXT,
    next_steps JSONB,
    group_id UUID REFERENCES groups(id),
    lawyer_id UUID REFERENCES lawyers(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cases_user_id ON cases(user_id);
CREATE INDEX idx_cases_case_type ON cases(case_type);
CREATE INDEX idx_cases_status ON cases(status);

CREATE TABLE case_steps (
    id UUID PRIMARY KEY,
    case_id UUID NOT NULL REFERENCES cases(id),
    step_number VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_case_steps_case_id ON case_steps(case_id);
```

## Setup & Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis (for caching/queues)

### Environment Variables

Add to `.env` file:

```env
# Required for AI analysis
ANTHROPIC_API_KEY=sk-ant-[your-key-here]

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hear_my_case

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Other configs
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations (if using Alembic)
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

### Using provided test file

```bash
# Set AUTH_TOKEN in test_cases_api.py first
python test_cases_api.py
```

### Using cURL

```bash
# Get token first
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210", "otp": "123456"}'

# Create case
curl -X POST http://localhost:8000/api/cases \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_type": "unpaid_wages",
    "employer_name": "ABC Corp",
    "amount_owed": 50000
  }'

# Analyze case
curl -X POST http://localhost:8000/api/cases/{case_id}/analyze \
  -H "Authorization: Bearer TOKEN"

# List cases
curl -X GET "http://localhost:8000/api/cases?case_type=unpaid_wages" \
  -H "Authorization: Bearer TOKEN"
```

## Performance Considerations

### Query Optimization

1. **Indexing**: All frequently filtered columns are indexed
2. **Pagination**: Default 20 items, max 100 per request
3. **Async Operations**: Full async/await for database queries
4. **Connection Pooling**: Configured via SQLAlchemy

### Claude API Optimization

1. **Rate Limiting**: Consider implementing request throttling
2. **Caching**: Cache analysis results for same cases
3. **Batching**: Could batch multiple analyses

### Future Optimizations

- [ ] Add Redis caching for case analysis
- [ ] Implement request rate limiting
- [ ] Add API versioning (/api/v2/cases)
- [ ] Add batch analysis endpoint
- [ ] Add webhooks for case updates

## Logging

All operations are logged for debugging:

```python
logger.info(f"Case created: {new_case.id} for user {user_id}")
logger.info(f"Case updated: {case.id}")
logger.info(f"Case analysis generated: {case.id}")
logger.error(f"Claude API error: {response.text}")
```

View logs:
```bash
tail -f logs/app.log
```

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:** Add to `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Issue: "Invalid case id" error

**Solution:** Ensure case_id is a valid UUID format
```
Valid: 550e8400-e29b-41d4-a716-446655440000
Invalid: 12345
```

### Issue: "You do not have permission to access this case"

**Solution:** Users can only access their own cases. Check:
1. Your JWT token is valid
2. You're accessing your own case_id
3. Case owner matches your user_id

### Issue: Claude API timeouts

**Solution:** 
1. Check API key is correct
2. Check network connectivity
3. Increase timeout if needed (currently 30s)
4. Check Claude API status

## Future Enhancements

### Phase 2
- [ ] Case evidence/document upload
- [ ] Case history timeline
- [ ] Real-time notifications
- [ ] Multi-language support

### Phase 3
- [ ] Advanced search with Elasticsearch
- [ ] Analytics dashboard
- [ ] Integration with SMS/WhatsApp
- [ ] Lawyer assignment workflow

### Phase 4
- [ ] Mobile app support
- [ ] Video consultation scheduling
- [ ] Blockchain for case records
- [ ] Integration with govt systems

## API Reference

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete endpoint reference with examples.

## Support

For issues or questions:
1. Check logs: `logs/app.log`
2. Check .env configuration
3. Verify database connectivity
4. Review error response messages
5. Test individual endpoints with cURL

---

**Last Updated:** May 2026
**API Version:** 1.0
**Status:** Production Ready
