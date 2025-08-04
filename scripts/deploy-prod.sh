#!/bin/bash

# GuildRoster Production Deployment Script
# Usage: ./scripts/deploy-prod.sh [command] [options]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        print_error ".env file not found in project root. Please create one based on env.docker.example"
        exit 1
    fi
}

# Function to deploy the application
deploy() {
    print_status "Starting production deployment..."
    
    check_docker
    check_env_file
    
    print_status "Stopping existing containers..."
    cd "$PROJECT_ROOT"
    docker-compose down
    
    print_status "Building and starting containers..."
    docker-compose up -d --build
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Deployment completed successfully!"
        print_status "Services status:"
        docker-compose ps
    else
        print_error "Deployment failed. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Function to restart services
restart() {
    print_status "Restarting services..."
    
    check_docker
    cd "$PROJECT_ROOT"
    docker-compose restart
    
    print_success "Services restarted successfully!"
}

# Function to stop services
stop() {
    print_status "Stopping services..."
    
    check_docker
    cd "$PROJECT_ROOT"
    docker-compose down
    
    print_success "Services stopped successfully!"
}

# Function to view logs
logs() {
    local service=${1:-""}
    
    check_docker
    cd "$PROJECT_ROOT"
    
    if [ -n "$service" ]; then
        print_status "Showing logs for $service..."
        docker-compose logs -f "$service"
    else
        print_status "Showing all logs..."
        docker-compose logs -f
    fi
}

# Function to create superuser
create_superuser() {
    print_status "Creating superuser..."
    
    check_docker
    cd "$PROJECT_ROOT"
    
    # Check if backend is running
    if ! docker-compose ps backend | grep -q "Up"; then
        print_error "Backend service is not running. Please start the services first."
        exit 1
    fi
    
    print_status "Running superuser creation script..."
    docker-compose exec backend python -c "
import asyncio
from app.database import get_db
from app.models.user import User
from app.utils.password import hash_password
from sqlalchemy.orm import Session

def create_superuser():
    db = next(get_db())
    try:
        # Check if superuser already exists
        existing_user = db.query(User).filter(User.username == 'admin').first()
        if existing_user:
            print('Superuser already exists!')
            return
        
        # Create superuser
        hashed_password = hash_password('admin123')
        superuser = User(
            username='admin',
            email='admin@guildroster.io',
            hashed_password=hashed_password,
            is_superuser=True,
            is_active=True
        )
        db.add(superuser)
        db.commit()
        print('Superuser created successfully!')
        print('Username: admin')
        print('Password: admin123')
        print('Please change the password after first login!')
    except Exception as e:
        print(f'Error creating superuser: {e}')
        db.rollback()
    finally:
        db.close()

create_superuser()
"
    
    print_success "Superuser creation completed!"
}

# Function to create API token
create_token() {
    local username=${1:-"admin"}
    local token_name=${2:-"production-token"}
    
    print_status "Creating API token for user: $username"
    
    check_docker
    cd "$PROJECT_ROOT"
    
    # Check if backend is running
    if ! docker-compose ps backend | grep -q "Up"; then
        print_error "Backend service is not running. Please start the services first."
        exit 1
    fi
    
    print_status "Creating token..."
    docker-compose exec backend python -c "
import asyncio
from app.database import get_db
from app.models.user import User
from app.models.token import Token
from app.utils.token import create_access_token
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def create_api_token(username, token_name):
    db = next(get_db())
    try:
        # Find user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f'User {username} not found!')
            return
        
        # Create token
        expires_at = datetime.utcnow() + timedelta(days=365)  # 1 year
        token_data = create_access_token(
            data={'sub': user.username, 'user_id': user.id},
            expires_delta=expires_at
        )
        
        # Save token to database
        token = Token(
            user_id=user.id,
            name=token_name,
            token_hash=token_data['token_hash'],
            expires_at=expires_at,
            is_active=True
        )
        db.add(token)
        db.commit()
        
        print(f'Token created successfully!')
        print(f'Token: {token_data[\"access_token\"]}')
        print(f'Expires: {expires_at}')
        print(f'Name: {token_name}')
        
    except Exception as e:
        print(f'Error creating token: {e}')
        db.rollback()
    finally:
        db.close()

create_api_token('$username', '$token_name')
"
    
    print_success "Token creation completed!"
}

# Function to run database migrations
migrate() {
    print_status "Running database migrations..."
    
    check_docker
    cd "$PROJECT_ROOT"
    
    # Check if backend is running
    if ! docker-compose ps backend | grep -q "Up"; then
        print_error "Backend service is not running. Please start the services first."
        exit 1
    fi
    
    print_status "Running migrations..."
    docker-compose exec backend alembic upgrade head
    
    print_success "Migrations completed successfully!"
}

# Function to backup database
backup() {
    local backup_dir=${1:-"$PROJECT_ROOT/backups"}
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/guildroster_backup_$timestamp.sql"
    
    print_status "Creating database backup..."
    
    check_docker
    cd "$PROJECT_ROOT"
    
    # Create backup directory if it doesn't exist
    mkdir -p "$backup_dir"
    
    # Check if database is running
    if ! docker-compose ps db | grep -q "Up"; then
        print_error "Database service is not running. Please start the services first."
        exit 1
    fi
    
    print_status "Backing up to: $backup_file"
    docker-compose exec -T db pg_dump -U guildroster guildroster > "$backup_file"
    
    if [ $? -eq 0 ]; then
        print_success "Backup created successfully!"
        print_status "Backup file: $backup_file"
    else
        print_error "Backup failed!"
        exit 1
    fi
}

# Function to restore database
restore() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        print_error "Please provide a backup file path"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_status "Restoring database from: $backup_file"
    
    check_docker
    cd "$PROJECT_ROOT"
    
    # Check if database is running
    if ! docker-compose ps db | grep -q "Up"; then
        print_error "Database service is not running. Please start the services first."
        exit 1
    fi
    
    print_warning "This will overwrite the current database. Are you sure? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Restore cancelled."
        exit 0
    fi
    
    print_status "Restoring database..."
    docker-compose exec -T db psql -U guildroster guildroster < "$backup_file"
    
    if [ $? -eq 0 ]; then
        print_success "Database restored successfully!"
    else
        print_error "Database restore failed!"
        exit 1
    fi
}

# Function to show status
status() {
    check_docker
    cd "$PROJECT_ROOT"
    
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_status "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Function to show help
show_help() {
    echo "GuildRoster Production Deployment Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  deploy                    Deploy the application (build and start containers)"
    echo "  restart                   Restart all services"
    echo "  stop                      Stop all services"
    echo "  logs [service]            Show logs (all services or specific service)"
    echo "  status                    Show service status and resource usage"
    echo "  migrate                   Run database migrations"
    echo "  create-superuser          Create a superuser account"
    echo "  create-token [user] [name] Create API token for user (default: admin, production-token)"
    echo "  backup [directory]        Create database backup (default: ./backups)"
    echo "  restore <file>            Restore database from backup file"
    echo "  help                      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 logs backend"
    echo "  $0 create-superuser"
    echo "  $0 create-token admin my-token"
    echo "  $0 backup /path/to/backups"
    echo "  $0 restore ./backups/guildroster_backup_20231201_120000.sql"
}

# Main script logic
case "${1:-help}" in
    deploy)
        deploy
        ;;
    restart)
        restart
        ;;
    stop)
        stop
        ;;
    logs)
        logs "$2"
        ;;
    status)
        status
        ;;
    migrate)
        migrate
        ;;
    create-superuser)
        create_superuser
        ;;
    create-token)
        create_token "$2" "$3"
        ;;
    backup)
        backup "$2"
        ;;
    restore)
        restore "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 