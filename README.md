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

# Create your first superuser account
python scripts/create_superuser.py

# Create additional tokens for testing (optional)
python scripts/create_token.py --type system --name "Development Token"

# Run the app
uvicorn app.main:app --reload

# Run tests
pytest
```

- **API:** http://localhost:8000
- **Interactive Docs (Swagger UI):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **OpenAPI Spec:** http://localhost:8000/openapi.json
- **Health Check:** http://localhost:8000

## Features

- **FastAPI REST API with automatic documentation**
  - Interactive Swagger UI at `/docs`
  - Professional ReDoc interface at `/redoc`
  - OpenAPI specification at `/openapi.json`
- PostgreSQL database with SQLAlchemy ORM
- Alembic migrations
- Comprehensive test suite with pytest
- **Secure password hashing** using PBKDF2 with SHA256 and automatic salting
- **Full API authentication** - All endpoints require valid tokens
- Token-based authentication system (user, system, and API tokens)
- User management with authentication-ready structure
- **Guild management** - Full CRUD operations with role-based access control
- Team management (planned)

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Testing:** Pytest, TestClient
- **Migrations:** Alembic
- **Python:** 3.13.5

## Password Authentication

GuildRoster implements secure password authentication following industry best practices:

- **PBKDF2 Hashing**: All passwords are hashed using PBKDF2 with SHA256 and automatic salting
- **Secure Storage**: Only hashed passwords are stored in the database
- **Token-Based Access**: Successful authentication returns secure API tokens
- **Password Validation**: Minimum 8 characters with strength requirements
- **No Plain Text**: Passwords are never stored or transmitted in plain text

The authentication system integrates seamlessly with the existing token-based API security, providing both user authentication and API access control.

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

## API Documentation

GuildRoster automatically generates comprehensive API documentation using FastAPI's built-in OpenAPI support.

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API explorer
  - Try endpoints directly in your browser
  - Real-time request/response testing
  - Authentication support (Bearer tokens)

- **ReDoc**: http://localhost:8000/redoc
  - Professional documentation interface
  - Better for sharing with non-technical users
  - Clean, organized layout

- **OpenAPI Specification**: http://localhost:8000/openapi.json
  - Raw OpenAPI 3.0 specification
  - Used by API clients and tools
  - Machine-readable format

### Using the Interactive Docs

1. **Start the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Create a token for testing**:
   ```bash
   python scripts/create_token.py --type system --name "API Testing"
   ```

3. **Access the docs**:
   - Visit http://localhost:8000/docs
   - Click the "Authorize" button (🔒 icon)
   - Enter your token: `Bearer YOUR_TOKEN_HERE`
   - Now you can test all endpoints interactively

### Documentation Features

✅ **Automatic Schema Generation** - All Pydantic models are documented  
✅ **Authentication Support** - Bearer token auth is fully integrated  
✅ **Request/Response Examples** - Auto-generated examples for all endpoints  
✅ **Validation Rules** - Shows required fields, data types, and constraints  
✅ **Error Responses** - All possible HTTP status codes are documented  
✅ **Always Up-to-Date** - Documentation matches your actual API code  

## API Endpoints

**Note:** All endpoints now require authentication. Use the token created in the setup steps.

### Health Check
- `GET /` - Health check (requires any valid token)

### Users
- `POST /users/` - Create new user (superuser only)
- `POST /users/login` - Authenticate user and get token
- `GET /users/` - List users (paginated, requires any valid token)
- `GET /users/{id}` - Get user by ID (requires any valid token)
- `GET /users/username/{username}` - Get user by username (requires any valid token)
- `PUT /users/{id}` - Update user (superuser only)
- `DELETE /users/{id}` - Delete user (superuser only)

### Tokens
- `POST /tokens/` - Create new token (superuser only)
- `GET /tokens/` - List tokens (superuser only)
- `GET /tokens/{id}` - Get token by ID (superuser only)
- `DELETE /tokens/{id}` - Delete token (superuser only)

### Guilds
- `POST /guilds/` - Create new guild (superuser only)
- `GET /guilds/` - List all guilds (any valid token)
- `GET /guilds/{guild_id}` - Get guild by ID (any valid token)
- `PUT /guilds/{guild_id}` - Update guild (superuser only)
- `DELETE /guilds/{guild_id}` - Delete guild (superuser only)

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

## User Authentication

The application now supports secure user authentication with password hashing using bcrypt.

### Creating a Superuser

To create the first superuser account:

```bash
python scripts/create_superuser.py
```

This interactive script will:
- Prompt for username and password
- Hash the password securely using bcrypt
- Create a superuser account
- Generate an authentication token
- Display the token for API access

### User Login

Users can authenticate and get tokens via the login endpoint:

```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

This returns:
```json
{
  "access_token": "your_token_here",
  "token_type": "bearer",
  "user_id": 1,
  "username": "your_username",
  "is_superuser": false
}
```

### Password Security

- **Hashing**: All passwords are hashed using PBKDF2 with SHA256 and automatic salting
- **Verification**: Password verification is done securely without storing plain text
- **Strength**: Passwords must be at least 8 characters long
- **Storage**: Only hashed passwords are stored in the database

## Guild Management System

GuildRoster now includes a comprehensive Guild management system that allows superusers to create, manage, and organize guilds within the application.

### Guild Features

#### **Core Functionality**
- **Create Guilds**: Superusers can create new guilds with unique names
- **List Guilds**: Any authenticated user can view all guilds
- **View Guild Details**: Get specific guild information by ID
- **Update Guilds**: Superusers can modify guild information
- **Delete Guilds**: Superusers can remove guilds from the system

#### **Security & Access Control**
- **Superuser-Only Operations**: Create, update, and delete operations require superuser privileges
- **Read Access**: Any valid token can view guild information
- **Unique Names**: Guild names must be unique across the system
- **Foreign Key Validation**: Guilds must reference valid users as creators

#### **Data Model**
Each guild contains:
- **ID**: Unique identifier (auto-generated)
- **Name**: Unique guild name (max 50 characters)
- **Created By**: Reference to the user who created the guild
- **Created At**: Timestamp of creation
- **Updated At**: Timestamp of last modification

#### **API Response Format**
```json
{
  "id": 1,
  "name": "Epic Raiders",
  "created_by": 1,
  "created_at": "2024-01-15T10:30:45",
  "updated_at": "2024-01-15T10:30:45"
}
```

#### **Error Handling**
- **400 Bad Request**: Duplicate guild names, invalid data
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Insufficient permissions (non-superuser trying to modify)
- **404 Not Found**: Guild ID doesn't exist

### Testing Guild Functionality

The Guild system includes comprehensive test coverage:

```bash
# Run guild-specific tests
pytest tests/feature/test_guild_router.py -v

# Run all tests including guild tests
pytest
```

**Test Coverage:**
- ✅ Create guild with valid data
- ✅ Create guild with duplicate name (validation)
- ✅ Update guild information
- ✅ Delete guild
- ✅ Access control (superuser vs regular user)
- ✅ List guilds
- ✅ Get guild by ID

## API Testing Examples

**Note:** All endpoints now require authentication. Replace `YOUR_TOKEN` with the token key from the setup step (e.g., the output from `python scripts/create_token.py --type system --name "Development Token"`).

### Health Check
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/
```

### User Endpoints
```bash
# Create a new user (superuser only)
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  -d '{
    "username": "newuser",
    "password": "securepassword123",
    "is_active": true,
    "is_superuser": false
  }'

# Login and get token
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword123"
  }'

# Get all users (paginated)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/users/

# Get user by ID
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/users/1

# Get user by username
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/users/username/someuser

# Update user (superuser only)
curl -X PUT http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  -d '{
    "username": "updateduser",
    "password": "newpassword123",
    "is_active": true
  }'

# Delete user (superuser only)
curl -X DELETE -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  http://localhost:8000/users/1
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

### Guild Endpoints
```bash
# Create a new guild (superuser only)
curl -X POST http://localhost:8000/guilds/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  -d '{
    "name": "Epic Raiders",
    "created_by": 1
  }'

# List all guilds (any valid token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/guilds/

# Get specific guild by ID (any valid token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/guilds/1

# Update guild (superuser only)
curl -X PUT http://localhost:8000/guilds/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  -d '{
    "name": "Epic Raiders Updated"
  }'

# Delete guild (superuser only)
curl -X DELETE -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  http://localhost:8000/guilds/1

# Test duplicate guild name (should fail)
curl -X POST http://localhost:8000/guilds/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  -d '{
    "name": "Epic Raiders",
    "created_by": 1
  }'
```
```

**Note:** Replace `YOUR_SUPERUSER_TOKEN` with an actual token from your database. You'll need to create a superuser and token first through your application or database.

## Database Schema

The application uses a relational database with the following core tables and relationships:

![Database Schema](schema.png)

**Core Tables:**
- **Users** - Authentication and user management
- **Tokens** - API authentication for both users and frontend applications (supports user, system, and API token types)
- **Guilds** - Guild information and settings (✅ **Implemented**)
- **Teams** - Team organization within guilds (planned)
- **Members** - Guild member profiles (planned)
- **Toons** - Character information for guild members (planned)
- **Raids** - Raid scheduling and tracking (planned)
- **Attendance** - Raid attendance records (planned)
- **Scenarios** - Raid instance lookup (planned)
- **Invites** - User registration system (planned)

**Key Relationships:**
- Users can belong to multiple guilds and have multiple tokens
- Tokens support user authentication, system operations, and frontend API access (with expiration and naming)
- **Guilds are created by users and contain multiple teams and members** (✅ **Implemented**)
- Members can have multiple characters (toons) (planned)
- Raids track attendance for specific scenarios (planned)
- Invites control user registration and guild membership (planned)

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

### API Documentation Development

When developing new endpoints, the documentation is automatically generated from your code:

- **Function docstrings** become endpoint descriptions
- **Pydantic models** become request/response schemas  
- **Type hints** become parameter documentation
- **Dependencies** (like auth) are automatically documented

Example:
```python
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_token: Token = Depends(require_any_token),
):
    """
    Retrieve a specific user by ID.
    
    **Parameters:**
    - `user_id`: The unique identifier of the user
    
    **Returns:**
    - User object with all details
    
    **Authentication:**
    - Requires any valid token
    """
    # Implementation here
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
