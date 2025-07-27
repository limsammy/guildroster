#!/bin/bash

# Script to deploy GuildRoster with subdomain setup (frontend on main domain, backend on api subdomain)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying GuildRoster with subdomain setup...${NC}"
echo -e "${BLUE}Frontend: guildroster.io${NC}"
echo -e "${BLUE}Backend API: api.guildroster.io${NC}"
echo ""

# Check if CORS is configured for subdomain
if ! grep -q "api.guildroster.io" .env 2>/dev/null; then
    echo -e "${YELLOW}Warning: api.guildroster.io not found in CORS_ORIGINS${NC}"
    echo -e "${YELLOW}Run './scripts/configure-cors.sh' to add it${NC}"
    echo ""
fi

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down || true

# Build and start containers with subdomain configuration
echo -e "${YELLOW}Building and starting containers with subdomain setup...${NC}"
docker-compose -f docker-compose.subdomain.yml up -d --build

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check if services are running
echo -e "${YELLOW}Checking service status...${NC}"
docker-compose -f docker-compose.subdomain.yml ps

echo -e "${GREEN}Deployment completed!${NC}"
echo ""
echo -e "${YELLOW}Your application is now available at:${NC}"
echo -e "${GREEN}  - Frontend: http://guildroster.io${NC}"
echo -e "${GREEN}  - Backend API: http://api.guildroster.io${NC}"
echo -e "${GREEN}  - API Documentation: http://api.guildroster.io/docs${NC}"
echo -e "${GREEN}  - Health Check: http://guildroster.io/health${NC}"
echo ""
echo -e "${YELLOW}Next steps for Cloudflare setup:${NC}"
echo -e "${GREEN}1. Add your domain to Cloudflare${NC}"
echo -e "${GREEN}2. Set DNS records to point to your server IP${NC}"
echo -e "${GREEN}3. Enable Cloudflare proxy (orange cloud) for both domains${NC}"
echo -e "${GREEN}4. Set SSL/TLS mode to 'Full'${NC}"
echo -e "${GREEN}5. Enable 'Always Use HTTPS'${NC}"
echo ""
echo -e "${GREEN}After Cloudflare setup, your site will be available at:${NC}"
echo -e "${GREEN}  - Frontend: https://guildroster.io${NC}"
echo -e "${GREEN}  - Backend API: https://api.guildroster.io${NC}"
echo ""
echo -e "${YELLOW}DNS Records to add in Cloudflare:${NC}"
echo -e "${BLUE}  Type: A, Name: @, Content: YOUR_SERVER_IP, Proxy: Orange cloud${NC}"
echo -e "${BLUE}  Type: A, Name: www, Content: YOUR_SERVER_IP, Proxy: Orange cloud${NC}"
echo -e "${BLUE}  Type: A, Name: api, Content: YOUR_SERVER_IP, Proxy: Orange cloud${NC}" 