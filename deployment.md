# Deployment Guide

## Production Environment

### Prerequisites
- AWS account with EC2 and RDS access
- Domain name with Cloudflare setup
- Docker and Docker Compose installed
- GitHub account with repository access

### Infrastructure Setup

1. EC2 Instance Setup
   - Ubuntu Server LTS
   - t2.micro (free tier)
   - 8GB root volume
   - Security group with ports 22, 80, 443

2. RDS Database
   - PostgreSQL 14+
   - db.t3.micro (free tier)
   - Enable automated backups

3. Cloudflare Configuration
   - SSL/TLS mode: Full (strict)
   - Enable WAF
   - Configure R2 bucket

### Initial Server Setup

1. Update system packages:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Install required packages:
```bash
sudo apt install -y nginx docker.io docker-compose python3-venv
```

3. Create application user:
```bash
sudo useradd -r -u 1002 -g www-data webapps
```

4. Set up directory structure:
```bash
sudo mkdir -p /opt/website/run
sudo mkdir -p /var/log/chesley_web/{nginx,django}
sudo chown -R webapps:www-data /opt/website /var/log/chesley_web
```

### SSL Certificate Setup

1. Install Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
```

2. Obtain certificate:
```bash
sudo certbot --nginx -d cchesley.com -d www.cchesley.com
```

### Nginx Configuration

1. Copy configuration files:
```bash
sudo cp nginx/chesley_web /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/chesley_web /etc/nginx/sites-enabled/
```

2. Remove default site:
```bash
sudo rm /etc/nginx/sites-enabled/default
```

3. Test configuration:
```bash
sudo nginx -t
```

### Application Deployment

1. Clone repository:
```bash
cd /opt/website
sudo -u webapps git clone [repository-url] .
```

2. Create environment file:
```bash
sudo -u webapps cp .env.prod-redacted .env.prod
# Edit .env.prod with actual values
```

3. Build and start containers:
```bash
sudo -u webapps docker-compose -f docker-compose.prod.yml up -d --build
```

4. Initialize database:
```bash
sudo -u webapps docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### GitHub Actions Setup

1. Add repository secrets:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - EC2_INSTANCE_ID
   - R2_ACCESS_KEY_ID
   - R2_SECRET_ACCESS_KEY
   - CLOUDFLARE_ACCOUNT_ID

2. Configure AWS Systems Manager:
   - Attach appropriate IAM role to EC2
   - Install SSM agent
   - Test connection

### Monitoring Setup

1. Configure logging:
   - Nginx logs in `/var/log/chesley_web/nginx/`
   - Django logs in `/var/log/chesley_web/django/`
   - Deployment logs in `/var/log/chesley_web/deployment.log`

2. Set up log rotation:
```bash
sudo cp logrotate/* /etc/logrotate.d/
```

### Post-Deployment Checks

1. Verify SSL setup:
   - Check SSL Labs rating
   - Verify HSTS configuration
   - Test SSL renewal

2. Security checks:
   - Verify WAF rules
   - Check rate limiting
   - Test backup system

3. Performance checks:
   - Test static file delivery
   - Verify caching headers
   - Check response times

## Maintenance

### Regular Tasks
1. Monitor logs daily
2. Check backup integrity weekly
3. Update dependencies monthly
4. Rotate SSL certificates (automated)
5. Review security configurations

### Troubleshooting
Common issues and solutions are documented in the main documentation.

### Emergency Contacts
- AWS Support
- Cloudflare Support
- System Administrator (you)
