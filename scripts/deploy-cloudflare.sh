#!/bin/bash

# Script to deploy GuildRoster with Cloudflare proxy (no SSL certificates needed on server)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying GuildRoster with Cloudflare proxy...${NC}"

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down || true

# Build and start containers with Cloudflare configuration
echo -e "${YELLOW}Building and starting containers with Cloudflare proxy...${NC}"
docker-compose up -d --build

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check if services are running
echo -e "${YELLOW}Checking service status...${NC}"
docker-compose ps

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${YELLOW}Your application should now be available at:${NC}"
echo -e "${GREEN}  - Frontend: http://159.223.132.130${NC}"
echo -e "${GREEN}  - API Docs: http://159.223.132.130/docs${NC}"
echo -e "${GREEN}  - Health Check: http://159.223.132.130/health${NC}"
echo -e ""
echo -e "${YELLOW}Next steps for Cloudflare setup:${NC}"
echo -e "${GREEN}1. Add your domain to Cloudflare${NC}"
echo -e "${GREEN}2. Set DNS records to point to 159.223.132.130${NC}"
echo -e "${GREEN}3. Enable Cloudflare proxy (orange cloud)${NC}"
echo -e "${GREEN}4. Set SSL/TLS mode to 'Full'${NC}"
echo -e "${GREEN}5. Enable 'Always Use HTTPS'${NC}"
echo -e ""
echo -e "${GREEN}After Cloudflare setup, your site will be available at:${NC}"
echo -e "${GREEN}  - https://yourdomain.com${NC}"   