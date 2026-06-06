# 🚀 Deployment Guide - Data Analytics Dashboard

## 📋 Deployment Options

### 🎯 **Quick Start (Recommended)**
```bash
# Make deployment script executable
chmod +x deploy.sh

# Full automated deployment
./deploy.sh deploy

# Access your dashboard
open http://localhost:8501
```

### 🐳 **Docker Compose Deployment**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 💻 **Local Development**
```bash
# Terminal 1: Start Frontend
python run_dashboard.py

# Terminal 2: Start Backend
cd backend
python run_server.py

# Terminal 3: Generate Sample Data
python sample_data_generator.py
```

## 🔧 Environment Setup

### **Prerequisites**
- Python 3.8+ 
- Docker & Docker Compose
- 4GB+ RAM
- 2GB+ disk space

### **System Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip docker.io docker-compose

# macOS
brew install python docker docker-compose

# Windows
# Install Docker Desktop
# Install Python from python.org
```

## 🌐 Production Deployment

### **Environment Variables**
```bash
# Create .env file
cat > .env << EOF
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@localhost/analytics_dashboard
SECRET_KEY=your-super-secret-key-change-this
BACKEND_URL=http://backend:8000
MAX_FILE_SIZE_MB=200
RATE_LIMIT_PER_HOUR=1000
EOF
```

### **SSL Configuration**
```bash
# Generate SSL certificates
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/nginx.key \
  -out nginx/ssl/nginx.crt
```

### **Database Setup**
```bash
# PostgreSQL production setup
docker run -d \
  --name analytics-postgres \
  -e POSTGRES_DB=analytics_dashboard \
  -e POSTGRES_USER=analytics \
  -e POSTGRES_PASSWORD=secure_password \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15-alpine
```

## ☁️ Cloud Deployment

### **AWS Deployment**
```bash
# Using AWS ECS
aws ecs create-cluster --cluster-name analytics-dashboard

# Deploy with CloudFormation
aws cloudformation deploy \
  --template-file aws-template.yml \
  --stack-name analytics-dashboard \
  --capabilities CAPABILITY_IAM
```

### **Google Cloud Deployment**
```bash
# Using Cloud Run
gcloud run deploy analytics-dashboard \
  --image gcr.io/PROJECT_ID/analytics-dashboard \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### **Azure Deployment**
```bash
# Using Container Instances
az container create \
  --resource-group analytics-rg \
  --name analytics-dashboard \
  --image analytics-dashboard:latest \
  --ports 80 443 \
  --dns-name-label analytics-dashboard
```

## 🔍 Health Checks & Monitoring

### **Service Health**
```bash
# Check all services
curl http://localhost:8000/health
curl http://localhost:8501/_stcore/health

# Database connectivity
docker-compose exec postgres pg_isready

# Redis connectivity  
docker-compose exec redis redis-cli ping
```

### **Monitoring Setup**
```bash
# Add Prometheus monitoring
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Add Grafana dashboards
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

## 🔒 Security Configuration

### **Firewall Rules**
```bash
# Allow only necessary ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw deny 8000/tcp  # Block direct backend access
ufw deny 5432/tcp  # Block direct database access
```

### **Authentication Setup**
```bash
# Create admin user
docker-compose exec backend python -c "
from database import SessionLocal
from models import User
from auth import get_password_hash

db = SessionLocal()
admin = User(
    username='admin',
    email='admin@yourcompany.com',
    hashed_password=get_password_hash('secure_admin_password'),
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
print('Admin user created')
"
```

## 📊 Performance Optimization

### **Database Optimization**
```sql
-- Add indexes for better performance
CREATE INDEX idx_datasets_user_id ON datasets(user_id);
CREATE INDEX idx_datasets_created_at ON datasets(created_at);
CREATE INDEX idx_visualizations_dataset_id ON visualizations(dataset_id);
```

### **Caching Configuration**
```bash
# Redis caching setup
docker run -d \
  --name redis-cache \
  -p 6379:6379 \
  --memory=1g \
  redis:7-alpine redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

### **Load Balancing**
```nginx
# nginx.conf for multiple backend instances
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

## 🧪 Testing Deployment

### **Automated Testing**
```bash
# Run full test suite
./deploy.sh test

# Test individual components
python test_dashboard.py
python backend/test_api.py

# Load testing
pip install locust
locust -f load_test.py --host=http://localhost:8000
```

### **Manual Testing Checklist**
- [ ] Dashboard loads at http://localhost:8501
- [ ] API responds at http://localhost:8000/health
- [ ] File upload works (test with sample CSV)
- [ ] Data processing completes successfully
- [ ] All 6 visualization types render
- [ ] Export functionality works
- [ ] User authentication functions
- [ ] Database persistence verified

## 🔧 Troubleshooting

### **Common Issues**

**Port Already in Use**
```bash
# Find and kill process using port
lsof -ti:8501 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

**Database Connection Failed**
```bash
# Check database status
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

**Memory Issues**
```bash
# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory > 4GB+

# Check container memory usage
docker stats
```

**Permission Errors**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x deploy.sh
chmod +x backend/run_server.py
```

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=debug
./deploy.sh deploy

# Check detailed logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📈 Scaling & Performance

### **Horizontal Scaling**
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
  
  frontend:
    deploy:
      replicas: 2
```

### **Database Scaling**
```bash
# PostgreSQL read replicas
docker run -d \
  --name postgres-replica \
  -e PGUSER=replicator \
  -e POSTGRES_MASTER_SERVICE=postgres \
  postgres:15-alpine
```

### **CDN Integration**
```bash
# CloudFlare setup for static assets
# Configure DNS to point to your server
# Enable CloudFlare proxy for performance
```

## 🔄 Backup & Recovery

### **Database Backup**
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U analytics analytics_dashboard > backup_${DATE}.sql
aws s3 cp backup_${DATE}.sql s3://your-backup-bucket/
```

### **Application Backup**
```bash
# Backup uploads and exports
tar -czf app_data_${DATE}.tar.gz uploads/ exports/ sample_data/
aws s3 cp app_data_${DATE}.tar.gz s3://your-backup-bucket/
```

### **Recovery Process**
```bash
# Restore database
docker-compose exec -T postgres psql -U analytics -d analytics_dashboard < backup_20241201_120000.sql

# Restore application data
tar -xzf app_data_20241201_120000.tar.gz
```

## 📋 Maintenance

### **Regular Updates**
```bash
# Update Docker images
docker-compose pull
docker-compose up -d

# Update Python dependencies
pip install -r requirements.txt --upgrade
cd backend && pip install -r requirements.txt --upgrade
```

### **Log Rotation**
```bash
# Setup logrotate
cat > /etc/logrotate.d/analytics-dashboard << EOF
/var/log/analytics-dashboard/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
```

### **Health Monitoring**
```bash
# Setup monitoring cron job
cat > monitor.sh << EOF
#!/bin/bash
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Service down, restarting..."
    docker-compose restart
    # Send alert email/Slack notification
fi
EOF

# Add to crontab
echo "*/5 * * * * /path/to/monitor.sh" | crontab -
```

## 🎯 Success Checklist

After deployment, verify:

- [ ] **Frontend Access**: Dashboard loads at configured URL
- [ ] **Backend API**: All endpoints respond correctly
- [ ] **Database**: Data persists across restarts
- [ ] **File Upload**: CSV/Excel files process successfully
- [ ] **Visualizations**: All 6 chart types render
- [ ] **Authentication**: User registration/login works
- [ ] **Export**: Data export generates files
- [ ] **Performance**: Response times under 2 seconds
- [ ] **Security**: HTTPS enabled, ports secured
- [ ] **Monitoring**: Health checks operational
- [ ] **Backups**: Automated backup system active

---

## 🎉 **Deployment Complete!**

Your Data Analytics Dashboard is now live and ready to transform data analysis workflows from 4 hours to 5 minutes!

**Next Steps:**
1. Create your first admin user
2. Upload sample data to test
3. Generate your first automated report
4. Share access with stakeholders
5. Monitor performance and usage

**Support:** Check the troubleshooting section or create an issue for any deployment problems.