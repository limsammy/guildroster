# GuildRoster

A FastAPI-based web and API application to manage and track your guild's roster across multiple teams in World of Warcraft.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
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

- Python 3.13.5
- FastAPI
- Uvicorn (ASGI server)
- Pytest
- PostgreSQL
- Docker
- SQLAlchemy

## Getting Started

### Prerequisites

- Python 3.13.5
- PostgreSQL
- Docker

### Installation

```bash
git clone https://github.com/limsammy/guildroster.git
cd guildroster
pyenv virtualenv 3.13.5 guildroster
pyenv activate guildroster
pip install -r requirements.txt
```

# REST OF README IS WIP

### Running the Application

```bash
uvicorn app.main:app --reload
```

- The API will be available at: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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

## Schema

Here is the schema for the database with the tables and their relationships (Designed with [wwwsqldesigner](https://github.com/ondras/wwwsqldesigner)):

![Schema](./guildroster_schema_v0.3.png)

### Schema Description

The GuildRoster database schema is designed to manage guilds, teams, members, raids, and attendance for a World of Warcraft guild environment. Here’s an overview of the main tables and their relationships:

- **Users**:  
  Stores user account information, including username, password, invite code, superuser status, and the guilds they belong to.

- **Guilds**:  
  Represents a guild, with a name and relationships to its members and teams. Each guild can have multiple members and teams.

- **Members**:  
  Represents individual guild members, storing their display name and Discord username. Each member can have multiple toons (characters).

- **Toons**:  
  Represents a character (toon) belonging to a member. Each toon has a username and a flag indicating if it is the member’s main character. Toons are linked to attendance records for raids.

- **Teams**:  
  Represents a team within a guild, with a name and relationships to its members and raids. Teams are used to organize members for specific raid groups or activities.

- **Raids**:  
  Represents a scheduled raid event, including the date/time, scenario (raid instance), difficulty, and size. Each raid is associated with a team and has attendance records for participating toons.  
  - **scenario_id**: Foreign key to the Scenarios table (lookup table/enum for raid instances).
  - **difficulty**: Enum representing the difficulty level of the raid (e.g., Normal, Heroic, Mythic).
  - **size**: Enum representing the size of the raid group (e.g., 10, 25, 40).

- **Attendance**:  
  Tracks which toons attended which raids, and whether they were present or absent.

- **Scenarios**:  
  Lookup table (or enum) representing different raid scenarios or instances (e.g., specific dungeons or raid zones).

#### Relationships

- **Users ↔ Guilds**:  
  An account can have many guilds.

- **Guilds ↔ Members**:  
  A guild has many members.

- **Guilds ↔ Teams**:  
  A guild can have many teams.

- **Members ↔ Toons**:  
  A member can have many toons (characters).

- **Teams ↔ Members**:  
  Teams are composed of many members.

- **Teams ↔ Raids**:  
  Each team can participate in many raids.

- **Raids ↔ Scenarios**:  
  Each raid is associated with a scenario (raid instance) from the lookup table.

- **Raids ↔ Attendance ↔ Toons**:  
  Attendance records link toons to raids, tracking their presence.

## Testing

To run tests, ensure you are in the project root directory and use:

```bash
pytest
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
