# Case Management API - Quick Reference

## Quick Start

### 1. Set Environment Variable
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Start Server
```bash
cd backend
uvicorn app.main:app --reload
```

### 3. Get Auth Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210", "otp": "123456"}'
```

---

## Common Operations

### Create Case
```bash
curl -X POST http://localhost:8000/api/cases \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_type": "unpaid_wages",
    "employer_name": "ABC Corp",
    "amount_owed": 50000,
    "period_start": "2025-01-01",
    "period_end": "2026-05-13"
  }'
```

### Get Case
```bash
curl http://localhost:8000/api/cases/{case_id} \
  -H "Authorization: Bearer TOKEN"
```

### List Cases (Filtered)
```bash
# All cases
curl "http://localhost:8000/api/cases" \
  -H "Authorization: Bearer TOKEN"

# By type
curl "http://localhost:8000/api/cases?case_type=unpaid_wages" \
  -H "Authorization: Bearer TOKEN"

# By status
curl "http://localhost:8000/api/cases?status=draft" \
  -H "Authorization: Bearer TOKEN"

# Search
curl "http://localhost:8000/api/cases?search=ABC" \
  -H "Authorization: Bearer TOKEN"

# Paginated
curl "http://localhost:8000/api/cases?skip=0&limit=20" \
  -H "Authorization: Bearer TOKEN"
```

### Update Case
```bash
curl -X PATCH http://localhost:8000/api/cases/{case_id} \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "intake_complete",
    "amount_owed": 75000
  }'
```

### Analyze Case (AI)
```bash
curl -X POST http://localhost:8000/api/cases/{case_id}/analyze \
  -H "Authorization: Bearer TOKEN"
```

### Delete Case
```bash
curl -X DELETE http://localhost:8000/api/cases/{case_id} \
  -H "Authorization: Bearer TOKEN"
```

### Get Case Steps
```bash
curl http://localhost:8000/api/cases/{case_id}/steps \
  -H "Authorization: Bearer TOKEN"
```

### Update Step Status
```bash
curl -X PATCH "http://localhost:8000/api/cases/{case_id}/steps/{step_id}?status=completed" \
  -H "Authorization: Bearer TOKEN"
```

---

## Response Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Success ✓ |
| 201 | Created | Resource created ✓ |
| 400 | Bad Request | Check input data |
| 403 | Forbidden | Not authorized for this resource |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Check logs/API key |

---

## Case Types

- `unpaid_wages` - Wage disputes
- `workplace_injury` - Injury claims
- `harassment` - Harassment claims
- `wrongful_termination` - Termination disputes
- `discrimination` - Discrimination claims
- `other` - Other issues

---

## Case Statuses

- `draft` - Being created
- `intake_complete` - Form filled
- `report_generated` - AI analysis done
- `lawyer_assigned` - Lawyer assigned
- `group_assigned` - NGO/Group assigned
- `in_progress` - Active work
- `completed` - Work finished
- `closed` - Case closed

---

## Step Statuses

- `pending` - Not started
- `in_progress` - In work
- `completed` - Finished

---

## Useful Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/cases` | Create case |
| GET | `/api/cases` | List cases |
| GET | `/api/cases/{id}` | Get case |
| PATCH | `/api/cases/{id}` | Update case |
| DELETE | `/api/cases/{id}` | Delete case |
| POST | `/api/cases/{id}/analyze` | AI analysis |
| GET | `/api/cases/{id}/steps` | List steps |
| PATCH | `/api/cases/{id}/steps/{sid}` | Update step |

---

## Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hear_my_case
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRATION_HOURS=24
```

---

## Files

| File | Purpose |
|------|---------|
| `app/api/cases.py` | API routes |
| `app/models/case.py` | Database models |
| `app/schemas/cases.py` | Request/response schemas |
| `API_DOCUMENTATION.md` | Full API docs |
| `IMPLEMENTATION_GUIDE.md` | Architecture & setup |
| `test_cases_api.py` | Test examples |

---

## Python Test Example

```python
import httpx
import asyncio

async def test():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        # Create
        resp = await client.post(
            "http://localhost:8000/api/cases",
            headers=headers,
            json={"case_type": "unpaid_wages", "employer_name": "ABC"}
        )
        case_id = resp.json()["id"]
        
        # Analyze
        resp = await client.post(
            f"http://localhost:8000/api/cases/{case_id}/analyze",
            headers=headers
        )
        print(resp.json()["case_summary"])

asyncio.run(test())
```

---

## Debug

### View Logs
```bash
tail -f logs/app.log
```

### Check API Key
```bash
echo $ANTHROPIC_API_KEY
```

### Test Claude API
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-3-5-sonnet-20241022", "max_tokens": 100, "messages": [{"role": "user", "content": "Test"}]}'
```

### Verify DB Connection
```bash
psql $DATABASE_URL -c "SELECT 1;"
```

---

## Tips

1. Always include `Authorization` header with Bearer token
2. Use UUIDs for IDs (not integers)
3. Dates must be YYYY-MM-DD format
4. Case analysis requires valid ANTHROPIC_API_KEY
5. Users can only access their own cases
6. Paginate large result sets (use `skip` and `limit`)

---

## Links

- [Full API Documentation](./API_DOCUMENTATION.md)
- [Implementation Guide](./IMPLEMENTATION_GUIDE.md)
- [Test Examples](./test_cases_api.py)

---

**API Version:** 1.0  
**Last Updated:** May 2026
