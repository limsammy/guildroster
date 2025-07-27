# Deployment Checklist

## Pre-Deployment
- [ ] Server has Docker and Docker Compose installed
- [ ] Firewall allows ports 80 and 443
- [ ] Code is uploaded to server
- [ ] `.env` file is created with production values
- [ ] Scripts are executable (`chmod +x scripts/*.sh`)
- [ ] CORS configuration is set up for your domain

## Choose Deployment Method

### Option A: Cloudflare Proxy (Recommended)
- [ ] Configure CORS: `./scripts/configure-cors.sh` (option 4)
- [ ] Run: `./scripts/deploy-cloudflare.sh`
- [ ] Add domain to Cloudflare
- [ ] Set DNS records with orange cloud (proxied)
- [ ] Configure SSL/TLS to "Full"
- [ ] Enable "Always Use HTTPS"

### Option B: Let's Encrypt (Direct SSL)
- [ ] Configure CORS: `./scripts/configure-cors.sh` (option 5)
- [ ] Run: `./scripts/setup-letsencrypt.sh domain.com email@example.com`
- [ ] Run: `./scripts/deploy-https.sh`
- [ ] Set DNS records with gray cloud (DNS only)

## Post-Deployment Verification
- [ ] All containers are running: `docker-compose ps`
- [ ] Health check passes: `curl http://159.223.132.130/health`
- [ ] Frontend loads: `curl http://159.223.132.130/`
- [ ] API docs accessible: `curl http://159.223.132.130/docs`
- [ ] Database connection works
- [ ] SSL certificate is valid (if using Let's Encrypt)
- [ ] Domain resolves correctly (if using domain)
- [ ] CORS origins are logged correctly: `docker-compose logs backend | grep "CORS Origins"`

## Security Checklist
- [ ] Strong database password in `.env`
- [ ] Secure SECRET_KEY in `.env`
- [ ] CORS_ORIGINS configured with minimal required domains
- [ ] Firewall configured properly
- [ ] No sensitive data in logs
- [ ] SSL/TLS configured correctly

## Monitoring Setup
- [ ] Log rotation configured
- [ ] Database backups scheduled
- [ ] SSL certificate renewal (if Let's Encrypt)
- [ ] Resource monitoring in place

## CORS Configuration Check
- [ ] CORS origins include your domain: `grep CORS_ORIGINS .env`
- [ ] Both HTTP and HTTPS versions included (if needed)
- [ ] www and non-www versions included (if needed)
- [ ] No unnecessary localhost origins in production
- [ ] CORS configuration logged on startup

## Final Test
- [ ] Visit your domain in browser
- [ ] Test login functionality
- [ ] Test API endpoints
- [ ] Check browser console for errors
- [ ] Verify HTTPS redirects work
- [ ] Test CORS from different origins (if applicable) 