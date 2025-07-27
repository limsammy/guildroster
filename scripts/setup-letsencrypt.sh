#!/bin/bash

# Script to set up Let's Encrypt SSL certificates for production
# This script uses certbot to obtain free SSL certificates

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

DOMAIN=${1:-"guildroster.io"}
EMAIL=${2:-"admin@guildroster.io"}

echo -e "${GREEN}Setting up Let's Encrypt SSL certificates for ${DOMAIN}...${NC}"

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo -e "${RED}Certbot is not installed. Installing...${NC}"
    sudo apt update
    sudo apt install -y certbot
fi

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Stop nginx temporarily to free up port 80
echo -e "${YELLOW}Stopping nginx temporarily...${NC}"
sudo systemctl stop nginx || true

# Obtain certificate using standalone mode
echo -e "${YELLOW}Obtaining SSL certificate from Let's Encrypt...${NC}"
sudo certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Copy certificates to our ssl directory
echo -e "${YELLOW}Copying certificates to ssl directory...${NC}"
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/key.pem

# Set proper permissions
sudo chown $USER:$USER ssl/cert.pem ssl/key.pem
chmod 644 ssl/cert.pem
chmod 600 ssl/key.pem

# Create renewal script
cat > scripts/renew-ssl.sh << EOF
#!/bin/bash
# Script to renew Let's Encrypt certificates

sudo certbot renew --quiet
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/cert.pem ssl/key.pem
chmod 644 ssl/cert.pem
chmod 600 ssl/key.pem

# Reload nginx to pick up new certificates
docker-compose -f docker-compose.https.yml restart nginx
EOF

chmod +x scripts/renew-ssl.sh

# Set up automatic renewal (add to crontab)
echo -e "${YELLOW}Setting up automatic certificate renewal...${NC}"
(crontab -l 2>/dev/null; echo "0 12 * * * $(pwd)/scripts/renew-ssl.sh") | crontab -

echo -e "${GREEN}SSL certificates set up successfully!${NC}"
echo -e "${YELLOW}Certificate location: ssl/cert.pem${NC}"
echo -e "${YELLOW}Private key location: ssl/key.pem${NC}"
echo -e "${YELLOW}Renewal script: scripts/renew-ssl.sh${NC}"
echo -e "${GREEN}Certificates will be automatically renewed daily at 12:00 PM${NC}" 