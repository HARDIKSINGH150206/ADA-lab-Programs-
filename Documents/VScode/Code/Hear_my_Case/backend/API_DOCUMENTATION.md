# Case Management API Documentation

This document provides complete information about the Case Management API endpoints, including CRUD operations, AI-powered case analysis, and case step management.

## Overview

The Case Management API (`/api/cases`) provides comprehensive functionality for managing legal cases, including:

- **CRUD Operations**: Create, read, update, and delete cases
- **AI-Powered Analysis**: Generate intelligent case analysis using Claude API
- **Case Steps**: Track and manage case milestones
- **Filtering & Search**: List cases with multiple filter options
- **Authentication**: All endpoints require JWT authentication

## Base URL

```
http://localhost:8000/api/cases
```

## Authentication

All endpoints require JWT authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Create Case

**POST** `/api/cases`

Creates a new case for the current authenticated user.

**Request Body:**
```json
{
  "case_type": "unpaid_wages",
  "employer_name": "ABC Manufacturing",
  "amount_owed": 50000.00,
  "period_start": "2025-01-01",
  "period_end": "2026-05-13",
  "contract_type": "written"
}
```

**Case Types:**
- `unpaid_wages` - Wage-related disputes
- `workplace_injury` - Workplace injury claims
- `harassment` - Workplace harassment
- `wrongful_termination` - Wrongful termination claims
- `discrimination` - Workplace discrimination
- `other` - Other legal issues

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "644e2f16-756c-436c-aa8f-33de4f769b31",
  "case_type": "unpaid_wages",
  "status": "draft",
  "employer_name": "ABC Manufacturing",
  "amount_owed": 50000.00,
  "period_start": "2025-01-01",
  "period_end": "2026-05-13",
  "contract_type": "written",
  "case_summary": null,
  "applicable_laws": null,
  "what_should_happen": null,
  "next_steps": null,
  "group_id": null,
  "lawyer_id": null,
  "created_at": "2026-05-14T10:30:00Z",
  "updated_at": "2026-05-14T10:30:00Z"
}
```

---

### 2. List Cases

**GET** `/api/cases`

Lists all cases for the current user with optional filtering and pagination.

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 20, max: 100) - Number of records to return
- `case_type` (string, optional) - Filter by case type
- `status` (string, optional) - Filter by case status
- `search` (string, optional) - Search by employer name

**Example Request:**
```
GET /api/cases?skip=0&limit=20&case_type=unpaid_wages&status=draft
GET /api/cases?search=ABC
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "644e2f16-756c-436c-aa8f-33de4f769b31",
      "case_type": "unpaid_wages",
      "status": "draft",
      "employer_name": "ABC Manufacturing",
      "amount_owed": 50000.00,
      "period_start": "2025-01-01",
      "period_end": "2026-05-13",
      "contract_type": "written",
      "case_summary": null,
      "applicable_laws": null,
      "what_should_happen": null,
      "next_steps": null,
      "group_id": null,
      "lawyer_id": null,
      "created_at": "2026-05-14T10:30:00Z",
      "updated_at": "2026-05-14T10:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

---

### 3. Get Case

**GET** `/api/cases/{case_id}`

Retrieves a specific case by ID.

**Path Parameters:**
- `case_id` (string, UUID format) - The case ID to retrieve

**Example Request:**
```
GET /api/cases/550e8400-e29b-41d4-a716-446655440000
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "644e2f16-756c-436c-aa8f-33de4f769b31",
  "case_type": "unpaid_wages",
  "status": "report_generated",
  "employer_name": "ABC Manufacturing",
  "amount_owed": 50000.00,
  "period_start": "2025-01-01",
  "period_end": "2026-05-13",
  "contract_type": "written",
  "case_summary": "Worker claim for unpaid wages from January 2025 to May 2026...",
  "applicable_laws": "Payment of Wages Act, 1936; The Code on Social Security, 2020",
  "what_should_happen": "Worker should receive full payment with interest...",
  "next_steps": ["File complaint with Labour Department", "Submit evidence"],
  "group_id": null,
  "lawyer_id": null,
  "created_at": "2026-05-14T10:30:00Z",
  "updated_at": "2026-05-14T11:45:00Z"
}
```

---

### 4. Update Case

**PATCH** `/api/cases/{case_id}`

Updates specific fields of a case.

**Path Parameters:**
- `case_id` (string, UUID format) - The case ID to update

**Request Body (all fields optional):**
```json
{
  "case_type": "unpaid_wages",
  "employer_name": "Updated Company Name",
  "amount_owed": 75000.00,
  "period_start": "2025-01-01",
  "period_end": "2026-05-13",
  "contract_type": "written",
  "status": "intake_complete"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "644e2f16-756c-436c-aa8f-33de4f769b31",
  "case_type": "unpaid_wages",
  "status": "intake_complete",
  "employer_name": "Updated Company Name",
  "amount_owed": 75000.00,
  "period_start": "2025-01-01",
  "period_end": "2026-05-13",
  "contract_type": "written",
  "case_summary": null,
  "applicable_laws": null,
  "what_should_happen": null,
  "next_steps": null,
  "group_id": null,
  "lawyer_id": null,
  "created_at": "2026-05-14T10:30:00Z",
  "updated_at": "2026-05-14T11:50:00Z"
}
```

---

### 5. Delete Case

**DELETE** `/api/cases/{case_id}`

Deletes a case (soft delete).

**Path Parameters:**
- `case_id` (string, UUID format) - The case ID to delete

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Case deleted successfully"
}
```

---

### 6. Analyze Case (AI-Powered)

**POST** `/api/cases/{case_id}/analyze`

Generates AI-powered case analysis using Claude API. Populates:
- `case_summary`: Concise summary of the case
- `applicable_laws`: Relevant Indian labor laws
- `what_should_happen`: Expected outcome
- `next_steps`: Recommended actions

The case status is automatically updated to `report_generated`.

**Path Parameters:**
- `case_id` (string, UUID format) - The case ID to analyze

**Example Request:**
```
POST /api/cases/550e8400-e29b-41d4-a716-446655440000/analyze
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "644e2f16-756c-436c-aa8f-33de4f769b31",
  "case_type": "unpaid_wages",
  "status": "report_generated",
  "employer_name": "ABC Manufacturing",
  "amount_owed": 50000.00,
  "period_start": "2025-01-01",
  "period_end": "2026-05-13",
  "contract_type": "written",
  "case_summary": "Worker claim for unpaid wages during the period from January 2025 to May 2026 at ABC Manufacturing company.",
  "applicable_laws": "Payment of Wages Act, 1936; The Code on Social Security, 2020; Factories Act, 1948",
  "what_should_happen": "The worker should receive the full unpaid wage amount of ₹50,000 with interest as per the Payment of Wages Act, 1936.",
  "next_steps": [
    "File a complaint with the Labour Department",
    "Submit employment contract and wage slips as evidence",
    "Participate in conciliation proceedings",
    "If unresolved, escalate to Labour Court"
  ],
  "group_id": null,
  "lawyer_id": null,
  "created_at": "2026-05-14T10:30:00Z",
  "updated_at": "2026-05-14T12:00:00Z"
}
```

---

### 7. Get Case Steps

**GET** `/api/cases/{case_id}/steps`

Retrieves all steps/milestones for a specific case.

**Path Parameters:**
- `case_id` (string, UUID format) - The case ID

**Response (200 OK):**
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "case_id": "550e8400-e29b-41d4-a716-446655440000",
    "step_number": "1",
    "title": "File Complaint",
    "description": "File formal complaint with Labour Department",
    "status": "completed",
    "created_at": "2026-05-14T10:30:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "case_id": "550e8400-e29b-41d4-a716-446655440000",
    "step_number": "2",
    "title": "Submit Evidence",
    "description": "Submit wage slips and employment contract",
    "status": "in_progress",
    "created_at": "2026-05-14T10:35:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440003",
    "case_id": "550e8400-e29b-41d4-a716-446655440000",
    "step_number": "3",
    "title": "Conciliation",
    "description": "Participate in conciliation proceedings",
    "status": "pending",
    "created_at": "2026-05-14T10:40:00Z"
  }
]
```

---

### 8. Update Case Step

**PATCH** `/api/cases/{case_id}/steps/{step_id}`

Updates the status of a specific case step.

**Path Parameters:**
- `case_id` (string, UUID format) - The case ID
- `step_id` (string, UUID format) - The step ID

**Query Parameters:**
- `status` (string, required) - New status: `pending`, `in_progress`, or `completed`

**Example Request:**
```
PATCH /api/cases/550e8400-e29b-41d4-a716-446655440000/steps/660e8400-e29b-41d4-a716-446655440002?status=completed
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Step status updated to completed"
}
```

---

## Case Statuses

| Status | Description |
|--------|-------------|
| `draft` | Case is being created/filled out |
| `intake_complete` | Initial intake form completed |
| `report_generated` | AI analysis report generated |
| `lawyer_assigned` | Case assigned to a lawyer |
| `group_assigned` | Case assigned to an advocacy group |
| `in_progress` | Case is actively being worked on |
| `completed` | Case work completed |
| `closed` | Case closed |

---

## Environment Configuration

The API requires the following environment variables to be set in your `.env` file:

```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hear_my_case

# Other required variables
JWT_SECRET_KEY=your-secret-key
ENVIRONMENT=development
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid case id"
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to access this case"
}
```

### 404 Not Found
```json
{
  "detail": "Case not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to generate case analysis"
}
```

---

## Usage Examples

### cURL Examples

#### Create a case
```bash
curl -X POST http://localhost:8000/api/cases \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_type": "unpaid_wages",
    "employer_name": "ABC Manufacturing",
    "amount_owed": 50000.00,
    "period_start": "2025-01-01",
    "period_end": "2026-05-13",
    "contract_type": "written"
  }'
```

#### Analyze a case
```bash
curl -X POST http://localhost:8000/api/cases/550e8400-e29b-41d4-a716-446655440000/analyze \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### List cases with filters
```bash
curl -X GET "http://localhost:8000/api/cases?case_type=unpaid_wages&status=draft" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Update case status
```bash
curl -X PATCH http://localhost:8000/api/cases/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "intake_complete"}'
```

---

## Implementation Notes

### AI Analysis Generation

The `/analyze` endpoint integrates with Claude API to generate intelligent legal analysis. The analysis includes:

1. **Case Summary**: 2-3 sentence summary based on case details
2. **Applicable Laws**: Comma-separated list of relevant Indian labor laws
3. **What Should Happen**: Expected outcome according to labor laws
4. **Next Steps**: Ordered list of recommended actions

The prompt is designed specifically for Indian labor law context and worker rights.

### Database Operations

All operations use async SQLAlchemy with PostgreSQL:
- Relationships are properly indexed for fast queries
- Soft deletes can be implemented by adding a `deleted_at` column if needed
- Case steps are automatically created when a case is analyzed

### Authentication

The API uses JWT tokens for authentication. Users must:
1. Register and get a JWT token from the `/api/auth/register` endpoint
2. Include the token in all requests using `Authorization: Bearer <token>`
3. Tokens expire after the configured `JWT_EXPIRATION_HOURS`

---

## Future Enhancements

- [ ] Add case evidence/document upload support
- [ ] Implement case timeline visualization
- [ ] Add real-time notifications for case updates
- [ ] Support for multi-language case analysis
- [ ] Integration with SMS/WhatsApp for case updates
- [ ] Advanced analytics and reporting dashboard
- [ ] Integration with lawyer directory and case assignment workflow
