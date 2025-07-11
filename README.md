# GuildRoster

A FastAPI-based web and API application to manage and track your guild's roster across multiple teams in World of Warcraft.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running Locally (Development)](#running-locally-development)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Briefly describe what your application does, its purpose, and the main use cases.

## Features

- FastAPI-powered RESTful API
- Interactive API docs (Swagger UI & ReDoc)
- [Add more features here]

## Tech Stack

- `Python 3.13.5`
- `FastAPI`
- `Uvicorn` (ASGI server)
- `Pytest`
- `PostgreSQL`
- `Docker`
- `SQLAlchemy`

## Getting Started

### Prerequisites

- `Python 3.13.5`
- `PostgreSQL`
- `Docker`
- `psycopg2`
- `Alembic` (for database migrations)

### Installation

```bash
git clone https://github.com/limsammy/guildroster.git
cd guildroster
pyenv virtualenv 3.13.5 guildroster
pyenv activate guildroster
pip install -r requirements.txt
```

### Running Locally (Development)

From the project root, start the development server with:

```bash
uvicorn app.main:app --reload
```

- The API will be available at: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`  # TODO: Not yet implemented

**Note:**
- Always run Uvicorn from the project root and use the correct module path (`app.main:app`).
- If you see an error like `Could not import module "main"`, it usually means you are either in the wrong directory or using the wrong import path. Double-check your working directory and the command.

### FastAPI App Structure

The main FastAPI app is now located in `app/main.py`. This file sets up logging, database initialization, and provides a root health check endpoint. You can add routers, middleware, and other features to this file as your project grows.

## API Documentation

FastAPI automatically generates interactive API docs:

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   └── utils/
├── tests/
│   ├── features/
│   ├── models/
├── requirements.txt
├── README.md
└── ...
```

- The `app/` directory contains the FastAPI application code.
- The `tests/` directory contains test modules, organized by `features/` and `models/` subdirectories.


### App Factory Pattern

This project uses the **app factory design pattern** for creating the FastAPI application instance. The factory function `create_app` is located in `app/__init__.py`. The main entrypoint for running the app is `main.py` at the project root, which imports and uses this factory.

#### Example Usage

```python
from app import create_app

app = create_app()
```

- In production, the app factory is called by the ASGI server (e.g., Uvicorn or Gunicorn) via `main.py`.
- In tests, you can call `create_app(test_config)` to inject test-specific settings.

### Benefits
- Clean separation of configuration and initialization
- Easier to test and extend
- Flexible for different environments

---

## Schema

Here is the schema for the database with the tables and their relationships (Designed with [wwwsqldesigner](https://github.com/ondras/wwwsqldesigner)):

![Schema](./schema.png)

### Schema Description

The GuildRoster database schema is designed to manage guilds, teams, members, raids, attendance, and an invite-based signup system for a World of Warcraft guild environment. Here’s an overview of the main tables, their fields, and relationships:

- **Invites**:  
  - `id`: Primary key
  - `code`: Unique invite code
  - `created_by`: User ID of the superuser who generated the invite
  - `used_by`: User ID of the user who redeemed the invite (nullable)
  - `created_at`: When the invite was created
  - `date_used`: When the invite was used (nullable)
  - `is_active`: Whether the invite is still valid

- **Users**:  
  - `id`: Primary key
  - `username`: Unique username
  - `password`: Hashed password
  - `invite_code`: Code used to sign up (references Invites.code)
  - `is_superuser`: Whether the user is a superuser
  - `created_at`: When the user was created
  - `guilds`: Relationship to guilds the user belongs to
  - `updated_at`: When the user was last updated

- **Guilds**:  
  - `id`: Primary key
  - `name`: Guild name
  - `teams`: Relationship to teams in the guild
  - `members`: Relationship to members in the guild
  - `created_at`: When the guild was created
  - `updated_at`: When the guild was last updated

- **Teams**:  
  - `id`: Primary key
  - `name`: Team name
  - `members`: Relationship to members in the team
  - `raids`: Relationship to raids for the team
  - `created_at`: When the team was created
  - `updated_at`: When the team was last updated

- **Members**:  
  - `id`: Primary key
  - `display_name`: Member's display name
  - `discord_username`: Discord username
  - `toons`: Relationship to toons (characters) for the member
  - `created_at`: When the member was created
  - `updated_at`: When the member was last updated

- **Toons**:  
  - `id`: Primary key
  - `username`: Toon (character) name
  - `is_main`: Whether this is the member's main toon
  - `created_at`: When the toon was created
  - `updated_at`: When the toon was last updated

- **Raids**:  
  - `id`: Primary key
  - `datetime`: Date and time of the raid
  - `scenario_id`: Foreign key to Scenarios.id
  - `difficulty`: Enum for raid difficulty
  - `size`: Enum for raid size
  - `created_at`: When the raid was created
  - `updated_at`: When the raid was last updated

- **Attendance**:  
  - `id`: Primary key
  - `raid_id`: Foreign key to Raids.id
  - `toon_id`: Foreign key to Toons.id
  - `is_present`: Whether the toon was present at the raid
  - `created_at`: When the attendance record was created
  - `date_modified`: When the attendance record was last modified (if applicable)
  - `updated_at`: When the attendance record was last updated

- **Scenarios**:  
  - `id`: Primary key
  - `name`: Scenario name
  - `created_at`: When the scenario was created
  - `date_modified`: When the scenario was last modified (if applicable)
  - `updated_at`: When the scenario was last updated

**Field Notes:**
- `created_at`: Timestamp for when the record was first created.
- `updated_at`: Timestamp for the most recent update to the record.
- `date_modified`: Used in some tables for additional tracking of modification events (may be redundant with `updated_at` in some cases).

**Relationships:**
- **Invites ↔ Users**: Each invite is created by a superuser (`created_by`) and, once used, is linked to the user who redeemed it (`used_by`). Users reference the invite code they used to sign up.
- **Users ↔ Guilds**: An account can have many guilds.
- **Guilds ↔ Members**: A guild has many members.
- **Guilds ↔ Teams**: A guild can have many teams.
- **Members ↔ Toons**: A member can have many toons (characters).
- **Teams ↔ Members**: Teams are composed of many members.
- **Teams ↔ Raids**: Each team can participate in many raids.
- **Raids ↔ Scenarios**: Each raid is associated with a scenario (raid instance) from the lookup table.
- **Raids ↔ Attendance ↔ Toons**: Attendance records link toons to raids, tracking their presence.

## Testing

To run tests, ensure you are in the project root directory and use:

```bash
pytest
```

To measure test coverage, this project uses [pytest-cov](https://pytest-cov.readthedocs.io/). Run:

```bash
pytest --cov=app
```

If you encounter import errors (e.g., `ModuleNotFoundError: No module named 'app'`), run:

```bash
PYTHONPATH=$(pwd) pytest
```

- All test directories should contain an `__init__.py` file for best compatibility.
- Test discovery and imports are set up for standard Python and pytest usage.

## Deployment

- [Instructions for deploying to production, e.g., using Gunicorn, Docker, etc.]

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

[MIT](LICENSE) (or your license of choice)
