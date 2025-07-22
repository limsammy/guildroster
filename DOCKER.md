# Docker Setup for GuildRoster

This document provides comprehensive instructions for running GuildRoster using Docker and Docker Compose.

## Quick Start

### Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)

### Automated Setup

The easiest way to get started is using our automated setup script:

```bash
# Production mode (recommended for first-time setup)
./scripts/docker-setup.sh prod

# Development mode (with hot reloading)
./scripts/docker-setup.sh dev
```

### Manual Setup

If you prefer to set up manually:

1. **Copy environment file:**
   ```bash
   cp env.docker.example .env
   ```

2. **Edit the environment file:**
   ```bash
   # Edit .env with your configuration
   nano .env
   ```

3. **Start the application:**
   ```bash
   # Production mode
   docker-compose up -d --build

   # Development mode
   docker-compose -f docker-compose.dev.yml up -d --build
   ```

## Architecture

The Docker setup includes the following services:

### Core Services

- **PostgreSQL Database** (`db`)
  - Port: 5432
  - Persistent volume for data storage
  - Health checks for reliability
  - Automatic database creation via environment variables

- **FastAPI Backend** (`backend`)
  - Port: 8000
  - Automatic Alembic migrations on startup
  - Health checks and logging

- **React Frontend** (`frontend`)
  - Port: 3000
  - Production-optimized build
  - Static file serving

### Optional Services

- **Nginx Reverse Proxy** (`nginx`)
  - Ports: 80, 443
  - Load balancing and SSL termination
  - Rate limiting and security headers
  - Use with `--profile proxy` flag

## Environment Configuration

### Production Environment

Copy `env.docker.example` to `.env` and configure:

```env
# Database Configuration
DB_USER=guildroster
DB_PASSWORD=secure_password_here
DB_HOST=db
DB_PORT=5432
DB_NAME=guildroster

# Application Configuration
SECRET_KEY=your_super_secret_key_here_change_this_in_production
ENV=production

# WarcraftLogs API Configuration (Optional)
WARCRAFTLOGS_CLIENT_ID=your_client_id_here
WARCRAFTLOGS_CLIENT_SECRET=your_client_secret_here

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
```

### Development Environment

Copy `env.docker.dev.example` to `.env` for development:

```env
# Database Configuration
DB_USER=guildroster
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432
DB_NAME=guildroster_dev

# Application Configuration
SECRET_KEY=dev_secret_key_change_in_production
ENV=dev

# WarcraftLogs API Configuration (Optional)
WARCRAFTLOGS_CLIENT_ID=your_client_id_here
WARCRAFTLOGS_CLIENT_SECRET=your_client_secret_here

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
```

## Usage

### Starting the Application

```bash
# Production mode
docker-compose up -d

# Development mode (with hot reloading)
docker-compose -f docker-compose.dev.yml up -d

# With Nginx reverse proxy
docker-compose --profile proxy up -d
```

### Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Accessing Services

Once running, you can access:

- **Frontend Application:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Alternative API Docs:** http://localhost:8000/redoc
- **Database:** localhost:5432

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U guildroster -d guildroster

# Run migrations manually (usually automatic on startup)
docker-compose exec backend alembic upgrade head

# Create superuser
docker-compose exec backend python scripts/create_superuser.py

# Create API token
docker-compose exec backend python scripts/create_token.py --type system --name "Docker Token"

# View migration history
docker-compose exec backend alembic history

# Check current migration
docker-compose exec backend alembic current
```

## Development Mode

Development mode provides:

- **Hot Reloading:** Code changes automatically restart services
- **Volume Mounting:** Source code is mounted for live editing
- **Development Dependencies:** All dev tools and dependencies included
- **Debugging:** Enhanced logging and error reporting

### Development Workflow

1. **Start in development mode:**
   ```bash
   ./scripts/docker-setup.sh dev
   ```

2. **Make code changes** in your local files

3. **See changes immediately** (hot reloading)

4. **View logs in real-time:**
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f
   ```

## Production Deployment

### Security Considerations

1. **Change default passwords** in `.env`
2. **Use strong SECRET_KEY**
3. **Enable HTTPS** with proper SSL certificates
4. **Configure firewall rules**
5. **Regular security updates**

### Performance Optimization

1. **Resource Limits:** Set appropriate memory and CPU limits
2. **Database Tuning:** Configure PostgreSQL for your workload
3. **Caching:** Consider Redis for session storage
4. **CDN:** Use CDN for static assets

### Monitoring

```bash
# Check service health
docker-compose ps

# Monitor resource usage
docker stats

# View health check status
docker-compose exec backend curl -f http://localhost:8000/
```

## Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check database status
docker-compose exec db pg_isready -U guildroster

# View database logs
docker-compose logs db

# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d
```

#### Backend Startup Issues

```bash
# Check backend logs
docker-compose logs backend

# Run migrations manually
docker-compose exec backend alembic upgrade head

# Check database connectivity
docker-compose exec backend python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection successful')
"
```

#### Frontend Build Issues

```bash
# Rebuild frontend
docker-compose build frontend

# Check frontend logs
docker-compose logs frontend

# Access frontend container
docker-compose exec frontend sh
```

### Log Analysis

```bash
# Follow all logs
docker-compose logs -f

# Filter logs by service
docker-compose logs -f backend | grep ERROR

# Export logs for analysis
docker-compose logs > guildroster.log
```

### Container Management

```bash
# Restart specific service
docker-compose restart backend

# Rebuild specific service
docker-compose build backend

# Remove and recreate containers
docker-compose down
docker-compose up -d --force-recreate
```

## Advanced Configuration

### Custom Nginx Configuration

1. **Edit nginx.conf** for custom routing rules
2. **Add SSL certificates** to `ssl/` directory
3. **Enable HTTPS** by uncommenting SSL section in nginx.conf

### Database Backup and Restore

```bash
# Create backup
docker-compose exec db pg_dump -U guildroster guildroster > backup.sql

# Restore backup
docker-compose exec -T db psql -U guildroster guildroster < backup.sql
```

### Scaling Services

```bash
# Scale backend instances
docker-compose up -d --scale backend=3

# Scale with load balancer
docker-compose --profile proxy up -d --scale backend=3
```

### Environment-Specific Configurations

Create environment-specific compose files:

```bash
# Production with monitoring
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Development with debugging
docker-compose -f docker-compose.dev.yml -f docker-compose.debug.yml up -d
```

## Support

For issues and questions:

1. **Check logs:** `docker-compose logs -f`
2. **Verify configuration:** Review `.env` file
3. **Test connectivity:** Use health check endpoints
4. **Review documentation:** Check API docs at `/docs`

## Security Notes

- **Never commit `.env` files** to version control
- **Use strong passwords** for database and application
- **Regularly update** Docker images and dependencies
- **Monitor logs** for suspicious activity
- **Backup data** regularly
- **Use HTTPS** in production environments 