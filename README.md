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

tests/
├── model/           # Model tests
├── unit/            # Unit tests
└── feature/         # Integration tests
```

## API Endpoints

### Users
- `GET /users/` - List users (paginated)
- `GET /users/{id}` - Get user by ID
- `GET /users/username/{username}` - Get user by username

## Database Schema

The application uses a relational database with tables for:
- **Users** - Authentication and user management
- **Guilds** - Guild information
- **Teams** - Team organization within guilds
- **Members** - Guild member profiles
- **Toons** - Character information
- **Raids** - Raid scheduling and tracking
- **Attendance** - Raid attendance records
- **Scenarios** - Raid instance lookup
- **Invites** - User registration system

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

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT
