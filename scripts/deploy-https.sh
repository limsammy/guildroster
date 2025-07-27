#!/bin/bash

# Script to deploy GuildRoster with HTTPS support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying GuildRoster with HTTPS support...${NC}"

# Check if SSL certificates exist
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo -e "${YELLOW}SSL certificates not found. Generating self-signed certificates for testing...${NC}"
    chmod +x scripts/generate-ssl-certs.sh
    ./scripts/generate-ssl-certs.sh
fi

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down || true

# Build and start containers with HTTPS configuration
echo -e "${YELLOW}Building and starting containers with HTTPS...${NC}"
docker-compose -f docker-compose.https.yml up -d --build

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check if services are running
echo -e "${YELLOW}Checking service status...${NC}"
docker-compose -f docker-compose.https.yml ps

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${YELLOW}Your application should now be available at:${NC}"
echo -e "${GREEN}  - Frontend: https://159.223.132.130${NC}"
echo -e "${GREEN}  - API Docs: https://159.223.132.130/docs${NC}"
echo -e "${GREEN}  - Health Check: https://159.223.132.130/health${NC}"

# Check if certificates are self-signed
if openssl x509 -in ssl/cert.pem -text -noout | grep -q "Issuer: C=US"; then
    echo -e "${RED}Note: Using self-signed certificates. Browsers will show security warnings.${NC}"
    echo -e "${YELLOW}For production, run: ./scripts/setup-letsencrypt.sh${NC}"
fi 