# HEAR MY CASE - Legal Case Management Platform

A comprehensive legal case management platform for workers in India, powered by AI.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local development)
- Node.js 18+ (for frontend development)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/hear-my-case.git
cd hear-my-case

# Copy environment file
cp backend/.env.example backend/.env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
```

Access the API at: http://localhost:8000
Swagger Docs: http://localhost:8000/docs

### Demo Mode

To boot the backend with seeded demo data, add these variables to `backend/.env`:

```env
DEMO_MODE=True
AUTO_SEED_DEMO_DATA=True
```

Demo logins:

- Worker: `+919900000001` / `Demo@1234`
- Admin: `+919900000099` / `Admin@1234`
- Lawyer: `+919900000002` / `Lawyer@1234`

Demo bootstrap endpoint:

- `POST /api/demo/bootstrap`

Readiness endpoint:

- `GET /health/ready`

### Option 2: Local Development

#### Backend
```bash
cd backend

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## Project Structure

```
hear-my-case/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # Route handlers
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── auth/        # Authentication
│   │   ├── db/          # Database config
│   │   └── utils/       # Utilities
│   ├── tests/           # Test suite
│   └── requirements.txt  # Dependencies
├── frontend/            # React frontend (coming soon)
├── docker-compose.yml   # Docker Compose config
└── README.md
```

## Development

### Running Tests
```bash
cd backend
pytest --cov
```

### Code Quality
```bash
black .
flake8 .
mypy .
```

## Documentation

- [API Documentation](./docs/API.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Security Guidelines](./docs/SECURITY.md)
- [Contributing Guidelines](./docs/CONTRIBUTING.md)

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please create an issue on GitHub or contact the team.
