# GuildRoster

A FastAPI-based web and API application to manage and track your guild's roster across multiple teams in World of Warcraft.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/limsammy/guildroster.git
cd guildroster
pyenv virtualenv 3.13.5 guildroster
pyenv activate guildroster
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Edit with your settings

# Create a development token for testing
python scripts/create_token.py --type system --name "Development Token"

# Run the app
uvicorn app.main:app --reload

# Run tests
pytest
```

- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000

## Features

- FastAPI REST API with automatic documentation
- PostgreSQL database with SQLAlchemy ORM
- Alembic migrations
- Comprehensive test suite with pytest
- **Full API authentication** - All endpoints require valid tokens
- Token-based authentication system (user, system, and API tokens)
- User management with authentication-ready structure
- Guild and team management (planned)

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Testing:** Pytest, TestClient
- **Migrations:** Alembic
- **Python:** 3.13.5

## Project Structure

```
app/
├── main.py          # FastAPI app entry point
├── config.py        # Environment configuration
├── database.py      # SQLAlchemy setup
├── models/          # Database models
├── schemas/         # Pydantic schemas
├── routers/         # API endpoints
└── utils/           # Utilities

scripts/
└── create_token.py  # Token creation utility

tests/
├── model/           # Model tests
├── unit/            # Unit tests
└── feature/         # Integration tests
```

## API Endpoints

**Note:** All endpoints now require authentication. Use the token created in the setup steps.

### Health Check
- `GET /` - Health check (requires any valid token)

### Users
- `GET /users/` - List users (paginated, requires any valid token)
- `GET /users/{id}` - Get user by ID (requires any valid token)
- `GET /users/username/{username}` - Get user by username (requires any valid token)

### Tokens
- `POST /tokens/` - Create new token (superuser only)
- `GET /tokens/` - List tokens (superuser only)
- `GET /tokens/{id}` - Get token by ID (superuser only)
- `DELETE /tokens/{id}` - Delete token (superuser only)

## Creating API Tokens

Before testing the API, you need to create a token for authentication. Use the provided script:

```bash
# Create a system token for development/testing
python scripts/create_token.py --type system --name "Development Token"

# Create an API token for frontend applications
python scripts/create_token.py --type api --name "Frontend App"

# Create a user token (requires existing user ID)
python scripts/create_token.py --type user --user-id 1 --name "User Token"

# Create a token with expiration (30 days)
python scripts/create_token.py --type system --name "Temporary Token" --expires 30
```

The script will output the token key that you can use in your API requests.

## API Testing Examples

**Note:** All endpoints now require authentication. Replace `YOUR_TOKEN` with the token key from the setup step (e.g., the output from `python scripts/create_token.py --type system --name "Development Token"`).

### Health Check
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/
```

### User Endpoints
```bash
# Get all users (paginated)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/users/

# Get user by ID
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/users/1

# Get user by username
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/users/username/someuser
```

### Token Endpoints (require superuser authentication)
```bash
# Create a system token
curl -X POST http://localhost:8000/tokens/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  -d '{
    "token_type": "system",
    "name": "Test System Token"
  }'

# Create a user token
curl -X POST http://localhost:8000/tokens/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  -d '{
    "token_type": "user",
    "user_id": 1,
    "name": "Test User Token"
  }'

# Get all tokens
curl -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  http://localhost:8000/tokens/

# Get tokens by type
curl -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  "http://localhost:8000/tokens/?token_type=system"

# Get specific token
curl -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  http://localhost:8000/tokens/1

# Delete a token
curl -X DELETE -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  http://localhost:8000/tokens/1

# Deactivate a token
curl -X POST -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  http://localhost:8000/tokens/1/deactivate

# Activate a token
curl -X POST -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  http://localhost:8000/tokens/1/activate
```

### Testing Authentication
```bash
# Should return 401 Unauthorized
curl http://localhost:8000/tokens/

# Should return 401 Unauthorized
curl -X POST http://localhost:8000/tokens/ \
  -H "Content-Type: application/json" \
  -d '{"token_type": "system", "name": "Test"}'

# Test with invalid token
curl -H "Authorization: Bearer invalid_token" \
  http://localhost:8000/tokens/
```

**Note:** Replace `YOUR_SUPERUSER_TOKEN` with an actual token from your database. You'll need to create a superuser and token first through your application or database.

## Database Schema

The application uses a relational database with the following core tables and relationships:

![Database Schema](schema.png)

**Core Tables:**
- **Users** - Authentication and user management
- **Tokens** - API authentication for both users and frontend applications (supports user, system, and API token types)
- **Guilds** - Guild information and settings
- **Teams** - Team organization within guilds
- **Members** - Guild member profiles
- **Toons** - Character information for guild members
- **Raids** - Raid scheduling and tracking
- **Attendance** - Raid attendance records
- **Scenarios** - Raid instance lookup
- **Invites** - User registration system

**Key Relationships:**
- Users can belong to multiple guilds and have multiple tokens
- Tokens support user authentication, system operations, and frontend API access (with expiration and naming)
- Guilds contain multiple teams and members
- Members can have multiple characters (toons)
- Raids track attendance for specific scenarios
- Invites control user registration and guild membership

## Development

### Prerequisites
- Python 3.13.5
- PostgreSQL
- pyenv (recommended)

### Environment Setup
Create a `.env` file with:
```env
DB_USER=guildroster
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=guildroster
SECRET_KEY=your-secret-key
```

### Testing
```bash
# Run all tests
pytest

# With coverage
pytest --cov=app

# Fix import issues
PYTHONPATH=$(pwd) pytest
```

### Type Checking and Linting

This project uses [mypy](http://mypy-lang.org/) for static type checking. Due to the dynamic nature of SQLAlchemy ORM and Pydantic integration, some mypy errors (such as assignments to SQLAlchemy model fields, or passing ORM models to Pydantic schemas) are expected and safe to ignore. These are well-known false positives and do not affect runtime correctness.

If you see `# type: ignore` comments in the codebase, they are used only for these unavoidable cases. All other mypy errors should be fixed or reported.

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### Logging

The application uses a centralized logging utility that provides both console and file output with daily rotation.

**Usage:**
```python
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Log levels
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning messages")
logger.error("Error messages")
logger.critical("Critical errors")
```

**Features:**
- **Console output** with colorized formatting
- **File output** with daily rotation (keeps 7 days of logs)
- **Structured format** with timestamp, level, module name, and message
- **Automatic log directory creation** (`logs/app.log`)

**Example output:**
```
INFO     | 2024-01-15 10:30:45 | app.main | Starting GuildRoster v0.1.0 in dev environment
WARNING  | 2024-01-15 10:30:46 | app.routers.user | User not found: unknown_user
ERROR    | 2024-01-15 10:30:47 | app.database | Database connection failed
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

TODO
