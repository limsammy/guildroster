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
```

### 2.3 Make Scripts Executable
```bash
chmod +x scripts/*.sh
```

## Step 3: Choose Deployment Method

### Option A: Cloudflare Proxy (Recommended)

#### 3A.1 Deploy with Cloudflare Configuration
```bash
./scripts/deploy-cloudflare.sh
```

#### 3A.2 Configure Cloudflare
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

#### 3B.1 Set Up SSL Certificates
```bash
# For testing with self-signed certificates
./scripts/generate-ssl-certs.sh

# OR for production with Let's Encrypt
./scripts/setup-letsencrypt.sh yourdomain.com your-email@example.com
```

#### 3B.2 Deploy with HTTPS Configuration
```bash
./scripts/deploy-https.sh
```

#### 3B.3 Configure Cloudflare (if using)
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
- Check nginx configuration
- Verify CORS settings in `app/main.py`
- Check browser console for specific errors

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

## Step 7: Security Considerations

### 7.1 Environment Variables
- Use strong, unique passwords
- Rotate secrets regularly
- Never commit `.env` files to version control

### 7.2 Firewall
- Only open necessary ports (22, 80, 443)
- Consider using fail2ban for SSH protection

### 7.3 Updates
- Keep system packages updated
- Regularly update Docker images
- Monitor for security advisories

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify configuration files
3. Test individual services
4. Check firewall and network settings

## URLs After Deployment

- **Frontend**: `https://yourdomain.com` (or `http://159.223.132.130`)
- **API Documentation**: `https://yourdomain.com/docs`
- **Health Check**: `https://yourdomain.com/health`
- **API Endpoints**: `https://yourdomain.com/api/` 