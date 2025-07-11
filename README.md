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
│   └── __pycache__/
├── tests/
│   ├── features/
│   ├── models/
├── requirements.txt
├── README.md
└── ...
```

- The `app/` directory contains the FastAPI application code.
- The `tests/` directory contains test modules, organized by feature and model.

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
