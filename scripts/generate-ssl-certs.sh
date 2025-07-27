#!/bin/bash

# Script to generate self-signed SSL certificates for development/testing
# For production, you should use certificates from a trusted CA like Let's Encrypt

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Generating SSL certificates for GuildRoster...${NC}"

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Generate private key
echo -e "${YELLOW}Generating private key...${NC}"
openssl genrsa -out ssl/key.pem 2048

# Generate certificate signing request (CSR)
echo -e "${YELLOW}Generating certificate signing request...${NC}"
openssl req -new -key ssl/key.pem -out ssl/cert.csr -subj "/C=US/ST=State/L=City/O=GuildRoster/CN=159.223.132.130"

# Generate self-signed certificate
echo -e "${YELLOW}Generating self-signed certificate...${NC}"
openssl x509 -req -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem -days 365

# Set proper permissions
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

# Clean up CSR file
rm ssl/cert.csr

echo -e "${GREEN}SSL certificates generated successfully!${NC}"
echo -e "${YELLOW}Certificate location: ssl/cert.pem${NC}"
echo -e "${YELLOW}Private key location: ssl/key.pem${NC}"
echo -e "${RED}Note: These are self-signed certificates for testing only.${NC}"
echo -e "${RED}For production, use certificates from a trusted Certificate Authority.${NC}" 