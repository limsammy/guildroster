# GuildRoster Production Deployment Guide

## Prerequisites

- Ubuntu/Debian server with Docker and Docker Compose installed
- Domain name (optional, but recommended)
- Cloudflare account (optional, but recommended for SSL)

## Step 1: Server Setup

### 1.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Install Docker (if not already installed)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for group changes to take effect
exit
# SSH back into your server
```

### 1.3 Configure Firewall
```bash
# Allow SSH, HTTP, and HTTPS
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Step 2: Application Setup

### 2.1 Clone/Upload Code
```bash
# If using git
git clone <your-repo-url>
cd guildroster

# Or upload your code to the server
```

### 2.2 Set Environment Variables
Create a `.env` file in the root directory:

**Option A: Copy from example file (Recommended)**
```bash
cp env.docker.example .env
# Edit the file with your specific values
nano .env
```

**Option B: Create manually**
```bash
# Database
DB_NAME=guildroster
DB_USER=guildroster
DB_PASSWORD=your_secure_password_here

# Application
SECRET_KEY=your_very_secure_secret_key_here
ENV=production

# WarcraftLogs (optional)
WARCRAFTLOGS_CLIENT_ID=your_client_id
WARCRAFTLOGS_CLIENT_SECRET=your_client_secret

# CORS Configuration
# Comma-separated list of allowed origins (domains/IPs that can access the API)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,http://yourdomain.com,https://yourdomain.com

# CORS Security Settings
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
```

### 2.3 Configure CORS Settings
Use the interactive CORS configuration helper to set up CORS for your domain:

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run CORS configuration helper
./scripts/configure-cors.sh
```

This script will help you:
- Set up CORS for your specific domain
- Generate proper CORS origins for different deployment methods
- Configure security settings
- Test your configuration

### 2.4 Make Scripts Executable
```bash
chmod +x scripts/*.sh
```

## Step 3: Choose Deployment Method

### Option A: Cloudflare Proxy (Recommended)

#### 3A.1 Configure CORS for Cloudflare
```bash
# Run the CORS configuration helper
./scripts/configure-cors.sh

# Choose option 4: "Set up CORS for Cloudflare deployment"
# Enter your domain when prompted
```

#### 3A.2 Deploy with Cloudflare Configuration
```bash
./scripts/deploy-cloudflare.sh
```

#### 3A.3 Configure Cloudflare
1. **Add Domain to Cloudflare**:
   - Go to [cloudflare.com](https://cloudflare.com)
   - Add your domain
   - Update nameservers at your domain registrar

2. **Configure DNS Records**:
   - Type: `A`
   - Name: `@` (or your domain root)
   - Content: `159.223.132.130`
   - Proxy status: **Orange cloud** (proxied)

   - Type: `A`
   - Name: `www`
   - Content: `159.223.132.130`
   - Proxy status: **Orange cloud** (proxied)

3. **Configure SSL/TLS**:
   - Go to SSL/TLS settings
   - Mode: `Full`
   - Edge Certificates: Enable "Always Use HTTPS"

4. **Test Your Site**:
   - Wait for DNS propagation (5-10 minutes)
   - Visit `https://yourdomain.com`

### Option B: Let's Encrypt (Direct SSL)

#### 3B.1 Configure CORS for Let's Encrypt
```bash
# Run the CORS configuration helper
./scripts/configure-cors.sh

# Choose option 5: "Set up CORS for Let's Encrypt deployment"
# Enter your domain when prompted
```

#### 3B.2 Set Up SSL Certificates
```bash
# For testing with self-signed certificates
./scripts/generate-ssl-certs.sh

# OR for production with Let's Encrypt
./scripts/setup-letsencrypt.sh yourdomain.com your-email@example.com
```

#### 3B.3 Deploy with HTTPS Configuration
```bash
./scripts/deploy-https.sh
```

#### 3B.4 Configure Cloudflare (if using)
1. **DNS Records** (Gray cloud - DNS only):
   - Type: `A`
   - Name: `@`
   - Content: `159.223.132.130`
   - Proxy status: **Gray cloud** (DNS only)

2. **SSL/TLS Settings**:
   - Mode: `Full (strict)` or `Off`

## Step 4: Verify Deployment

### 4.1 Check Service Status
```bash
# Check all containers are running
docker-compose -f docker-compose.cloudflare.yml ps
# OR
docker-compose -f docker-compose.https.yml ps

# Check logs
docker-compose -f docker-compose.cloudflare.yml logs -f
```

### 4.2 Test Endpoints
```bash
# Health check
curl http://159.223.132.130/health

# API docs
curl http://159.223.132.130/docs

# Frontend
curl http://159.223.132.130/
```

### 4.3 Check Database
```bash
# Connect to database container
docker exec -it guildroster-db psql -U guildroster -d guildroster

# Check tables
\dt

# Exit
\q
```

## Step 5: Monitoring and Maintenance

### 5.1 Set Up Log Rotation
```bash
# Create log directory
mkdir -p logs/nginx

# Add to crontab for log rotation
(crontab -l 2>/dev/null; echo "0 2 * * * find /path/to/logs -name '*.log' -mtime +7 -delete") | crontab -
```

### 5.2 Set Up SSL Certificate Renewal (Let's Encrypt only)
```bash
# Certificate renewal is already set up in setup-letsencrypt.sh
# Check renewal status
sudo certbot certificates
```

### 5.3 Backup Database
```bash
# Create backup script
cat > scripts/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec guildroster-db pg_dump -U guildroster guildroster > "$BACKUP_DIR/guildroster_$DATE.sql"
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
EOF

chmod +x scripts/backup-db.sh

# Add to crontab (daily backup at 3 AM)
(crontab -l 2>/dev/null; echo "0 3 * * * /path/to/guildroster/scripts/backup-db.sh") | crontab -
```

## Step 6: Troubleshooting

### 6.1 Common Issues

**CORS Errors**:
1. **Check CORS configuration**:
   ```bash
   # Verify your domain is in CORS_ORIGINS
   grep CORS_ORIGINS .env
   
   # Use the CORS configuration helper
   ./scripts/configure-cors.sh
   ```

2. **Check application logs**:
   ```bash
   # View CORS origins being used
   docker-compose logs backend | grep "CORS Origins"
   
   # Check for CORS-related errors
   docker-compose logs backend | grep -i cors
   ```

3. **Verify environment variables**:
   - Ensure `CORS_ORIGINS` includes your domain
   - Include both HTTP and HTTPS versions
   - Include www and non-www versions if needed
   - Format: `http://domain1.com,https://domain2.com`

4. **Check deployment method**:
   - For Cloudflare: Ensure DNS records use orange cloud (proxied)
   - For Let's Encrypt: Verify SSL certificates are valid
   - For development: Check browser console for API URL being used

**Database Connection Issues**:
```bash
# Check database container
docker logs guildroster-db

# Check backend logs
docker logs guildroster-backend
```

**SSL Certificate Issues**:
```bash
# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect yourdomain.com:443
```

### 6.2 Useful Commands

```bash
# View all logs
docker-compose -f docker-compose.cloudflare.yml logs

# Restart specific service
docker-compose -f docker-compose.cloudflare.yml restart backend

# Update application
git pull
docker-compose -f docker-compose.cloudflare.yml up -d --build

# Check resource usage
docker stats

# Clean up unused images
docker image prune -f
```

## Step 7: CORS Configuration Best Practices

### 7.1 CORS Security Guidelines

**Production CORS Settings**:
- Only include domains you actually use
- Include both HTTP and HTTPS versions
- Include www and non-www versions if needed
- Remove localhost origins in production

**Example Production CORS_ORIGINS**:
```bash
# For a single domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# For multiple domains
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://api.yourdomain.com
```

**Development CORS Settings**:
```bash
# For local development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000
```

### 7.2 CORS Configuration Scripts

**Quick CORS Setup**:
```bash
# For Cloudflare deployment
./scripts/configure-cors.sh
# Choose option 4 and enter your domain

# For Let's Encrypt deployment
./scripts/configure-cors.sh
# Choose option 5 and enter your domain

# For development
./scripts/configure-cors.sh
# Choose option 6
```

**Manual CORS Configuration**:
```bash
# Show current CORS settings
./scripts/configure-cors.sh
# Choose option 1

# Add a specific domain
./scripts/configure-cors.sh
# Choose option 2 and enter domain
```

### 7.3 CORS Troubleshooting

**Common CORS Issues**:
1. **Domain not in CORS_ORIGINS**: Add your domain to the environment variable
2. **Protocol mismatch**: Include both HTTP and HTTPS versions
3. **Subdomain issues**: Include www and non-www versions
4. **Port issues**: Include specific ports if using non-standard ports

**Debugging CORS**:
```bash
# Check what CORS origins are being used
docker-compose logs backend | grep "CORS Origins"

# Test CORS from command line
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://yourdomain.com/api/
```

## Step 8: Security Considerations

### 8.1 Environment Variables
- Use strong, unique passwords
- Rotate secrets regularly
- Never commit `.env` files to version control
- Keep CORS_ORIGINS minimal and specific

### 8.2 Firewall
- Only open necessary ports (22, 80, 443)
- Consider using fail2ban for SSH protection

### 8.3 Updates
- Keep system packages updated
- Regularly update Docker images
- Monitor for security advisories

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify configuration files
3. Test individual services
4. Check firewall and network settings

## Quick Reference

### URLs After Deployment
- **Frontend**: `https://yourdomain.com` (or `http://159.223.132.130`)
- **API Documentation**: `https://yourdomain.com/docs`
- **Health Check**: `https://yourdomain.com/health`
- **API Endpoints**: `https://yourdomain.com/api/`

### Common Commands
```bash
# Check CORS configuration
grep CORS_ORIGINS .env

# View CORS origins being used
docker-compose logs backend | grep "CORS Origins"

# Configure CORS for your domain
./scripts/configure-cors.sh

# Deploy with Cloudflare
./scripts/deploy-cloudflare.sh

# Deploy with Let's Encrypt
./scripts/setup-letsencrypt.sh yourdomain.com your-email@example.com
./scripts/deploy-https.sh

# Check service status
docker-compose -f docker-compose.cloudflare.yml ps

# View logs
docker-compose -f docker-compose.cloudflare.yml logs -f
```

### Environment Variables Reference
```bash
# Required
DB_NAME=guildroster
DB_USER=guildroster
DB_PASSWORD=your_secure_password
SECRET_KEY=your_very_secure_secret_key
ENV=production

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://yourdomain.com,https://yourdomain.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Optional
WARCRAFTLOGS_CLIENT_ID=your_client_id
WARCRAFTLOGS_CLIENT_SECRET=your_client_secret
``` 