#!/bin/bash

# GuildRoster Docker Setup Script
# This script helps set up the Docker environment for GuildRoster

set -e

echo "🐳 GuildRoster Docker Setup"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Docker daemon is running
check_docker_daemon() {
    print_status "Checking Docker daemon..."
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker daemon is running"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment file..."
    
    if [ ! -f .env ]; then
        if [ -f env.docker.example ]; then
            cp env.docker.example .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your configuration before starting containers"
        else
            print_error "env.docker.example not found"
            exit 1
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Build and start containers
start_containers() {
    local mode=${1:-production}
    
    print_status "Starting containers in $mode mode..."
    
    if [ "$mode" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml up -d --build
    else
        docker-compose up -d --build
    fi
    
    print_success "Containers started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for database..."
    timeout=60
    while ! docker-compose exec -T db pg_isready -U guildroster &> /dev/null; do
        if [ $timeout -le 0 ]; then
            print_error "Database failed to start within 60 seconds"
            exit 1
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    print_success "Database is ready"
    
    # Wait for backend
    print_status "Waiting for backend..."
    timeout=60
    while ! curl -f http://localhost:8000/ &> /dev/null; do
        if [ $timeout -le 0 ]; then
            print_error "Backend failed to start within 60 seconds"
            exit 1
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    print_success "Backend is ready"
    
    # Wait for frontend
    print_status "Waiting for frontend..."
    timeout=60
    while ! curl -f http://localhost:3000/ &> /dev/null; do
        if [ $timeout -le 0 ]; then
            print_error "Frontend failed to start within 60 seconds"
            exit 1
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    print_success "Frontend is ready"
}

# Create superuser
create_superuser() {
    print_status "Creating superuser..."
    
    if docker-compose exec -T backend python scripts/create_superuser.py; then
        print_success "Superuser created successfully"
    else
        print_warning "Failed to create superuser. You can create one manually later."
    fi
}

# Show status
show_status() {
    print_status "Container status:"
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Database: localhost:5432"
}

# Main function
main() {
    local mode=${1:-production}
    
    case $mode in
        "dev"|"development")
            mode="dev"
            ;;
        "prod"|"production")
            mode="production"
            ;;
        *)
            print_error "Invalid mode. Use 'dev' or 'prod'"
            exit 1
            ;;
    esac
    
    check_docker
    check_docker_daemon
    setup_env
    start_containers $mode
    wait_for_services
    create_superuser
    show_status
    
    echo ""
    print_success "GuildRoster is now running!"
    echo ""
    print_status "Next steps:"
    echo "  1. Visit http://localhost:3000 to access the application"
    echo "  2. Visit http://localhost:8000/docs to view API documentation"
    echo "  3. Use 'docker-compose logs -f' to view logs"
    echo "  4. Use 'docker-compose down' to stop the application"
}

# Handle command line arguments
case "${1:-}" in
    "dev"|"development")
        main "dev"
        ;;
    "prod"|"production")
        main "prod"
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [dev|prod]"
        echo ""
        echo "Options:"
        echo "  dev, development  Start in development mode with hot reloading"
        echo "  prod, production  Start in production mode (default)"
        echo "  help, -h, --help  Show this help message"
        ;;
    *)
        main "production"
        ;;
esac 