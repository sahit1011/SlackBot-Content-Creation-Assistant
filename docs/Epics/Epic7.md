# EPIC-007: Deployment & DevOps

**Priority:** P0 (Blocker for Launch)  
**Story Points:** 8  
**Duration:** 1 Day  
**Owner:** Developer  

---

## SLACK-024: Create Dockerfile

**Type:** DevOps  
**Priority:** Critical  
**Story Points:** 2  
**Estimated Time:** 1.5 hours  

**Description:**
Create production-ready Dockerfile for containerized deployment (single Dockerfile, no docker-compose).

**Acceptance Criteria:**
- [ ] Single Dockerfile builds successfully
- [ ] Optimized layers for faster builds
- [ ] Image size under 1GB
- [ ] Includes all dependencies
- [ ] Works on Render.com
- [ ] No security vulnerabilities

**Deliverables:**
- `Dockerfile`
- `.dockerignore`

**Dependencies:** All core features complete

**Code Implementation:**

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download sentence-transformers model (cache it in image)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /tmp/reports

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Run application
CMD ["python", "app/main.py"]
```

```dockerfile
# .dockerignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Project specific
*.pdf
*.csv
test_data/
logs/
*.log

# Documentation
README.md
*.md
docs/

# Tests
tests/
pytest.ini
.pytest_cache/

# Environment
.env
.env.local
```

**Testing:**
```bash
# Build image locally
docker build -t slackbot-content-assistant .

# Run container
docker run -p 3000:3000 --env-file .env slackbot-content-assistant

# Test health endpoint
curl http://localhost:3000/health

# Check logs
docker logs <container_id>

# Check image size
docker images | grep slackbot-content-assistant
```

---

## SLACK-025: Configure Environment for Production

**Type:** DevOps  
**Priority:** Critical  
**Story Points:** 1  
**Estimated Time:** 30 minutes  

**Description:**
Prepare environment configuration and add health check endpoint for production deployment.

**Acceptance Criteria:**
- [ ] Production environment variables documented
- [ ] Secrets management strategy defined
- [ ] Health check endpoint implemented
- [ ] Logging configured for production
- [ ] Environment-specific settings

**Deliverables:**
- Updated `app/config.py`
- `app/health.py`
- `.env.example`
- `DEPLOYMENT.md`

**Dependencies:** SLACK-024

**Code Implementation:**

```python
# app/config.py (updated)
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Slack
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
    
    # Database
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL')
    
    # APIs
    BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')
    
    # Application Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_KEYWORDS = int(os.getenv('MAX_KEYWORDS', '1000'))
    MAX_CLUSTERS = int(os.getenv('MAX_CLUSTERS', '10'))
    PROCESSING_TIMEOUT = int(os.getenv('PROCESSING_TIMEOUT', '600'))  # 10 minutes
    
    # Health Check
    HEALTH_CHECK_PORT = int(os.getenv('HEALTH_CHECK_PORT', '3000'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = [
            'SLACK_BOT_TOKEN',
            'SLACK_SIGNING_SECRET',
            'SUPABASE_URL',
            'SUPABASE_KEY'
        ]
        
        missing = [var for var in required if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
```

```python
# app/health.py
from flask import Flask, jsonify
import threading
from app.config import Config

app = Flask(__name__)

# Health status
health_status = {
    'status': 'healthy',
    'services': {
        'slack': 'unknown',
        'database': 'unknown',
        'redis': 'unknown'
    }
}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify(health_status), 200

@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check endpoint"""
    if health_status['status'] == 'healthy':
        return jsonify({'status': 'ready'}), 200
    return jsonify({'status': 'not ready'}), 503

def update_health_status(service: str, status: str):
    """Update health status for a service"""
    health_status['services'][service] = status
    
    # Update overall status
    if all(s != 'unhealthy' for s in health_status['services'].values()):
        health_status['status'] = 'healthy'
    else:
        health_status['status'] = 'unhealthy'

def start_health_server():
    """Start health check server"""
    app.run(host='0.0.0.0', port=Config.HEALTH_CHECK_PORT, debug=False)

def run_health_server_background():
    """Run health server in background thread"""
    thread = threading.Thread(target=start_health_server)
    thread.daemon = True
    thread.start()
```

```python
# Update app/main.py to include health server
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from app.config import Config
from app.health import run_health_server_background, update_health_status

# Validate config
Config.validate()

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Start health check server
run_health_server_background()

# Initialize Slack app
app = App(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET
)

from app.handlers import command_handlers, event_handlers

command_handlers.register(app)
event_handlers.register(app)

@app.event("app_mention")
def handle_app_mention(event, say):
    say(f"👋 Hi <@{event['user']}>! I'm ready to help with keyword processing.\n\n"
        f"Try:\n• `/process_keywords` - Start processing\n• `/history` - View past batches")
    update_health_status('slack', 'healthy')

def main():
    logger.info(f"Starting Slackbot Content Assistant in {Config.ENVIRONMENT} mode...")
    
    # Test database connection
    try:
        from app.services.database import DatabaseService
        db = DatabaseService()
        update_health_status('database', 'healthy')
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        update_health_status('database', 'unhealthy')
    
    # Test Redis connection
    try:
        from app.services.cache import CacheService
        cache = CacheService()
        if cache.client:
            update_health_status('redis', 'healthy')
            logger.info("Redis connection successful")
        else:
            update_health_status('redis', 'unavailable')
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        update_health_status('redis', 'unavailable')
    
    # Start Slack bot
    handler = SocketModeHandler(app, Config.SLACK_APP_TOKEN)
    handler.start()

if __name__ == "__main__":
    main()
```

```bash
# .env.example
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
SLACK_APP_TOKEN=xapp-your-app-token-here

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Redis Cache
REDIS_URL=redis://default:password@host:port

# Search API (choose one)
BRAVE_API_KEY=your-brave-api-key-here

# LLM
GROQ_API_KEY=your-groq-api-key-here

# Email (Optional)
SENDGRID_API_KEY=your-sendgrid-api-key-here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_KEYWORDS=1000
MAX_CLUSTERS=10
PROCESSING_TIMEOUT=600
HEALTH_CHECK_PORT=3000
DEBUG=False
```

**Testing:**
```bash
# Test config validation
python -c "from app.config import Config; Config.validate()"

# Test health endpoint
curl http://localhost:3000/health
```

---

## SLACK-026: Deploy to Render.com

**Type:** DevOps  
**Priority:** Critical  
**Story Points:** 3  
**Estimated Time:** 2 hours  

**Description:**
Deploy application to Render.com with Docker configuration.

**Acceptance Criteria:**
- [ ] Render.com project created and configured
- [ ] Connected to GitHub repository
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Application accessible and functional
- [ ] Auto-deploy on Git push configured

**Deliverables:**
- Live deployment URL
- `DEPLOYMENT.md` guide

**Dependencies:** SLACK-024, SLACK-025

**Code Implementation:**

```markdown
# DEPLOYMENT.md

# Deployment Guide for Render.com

## Prerequisites

1. GitHub account with project repository
2. Render.com account (free tier available)
3. All environment variables ready
4. Docker tested locally

## Step-by-Step Deployment

### 1. Prepare Repository

Ensure these files are in your repository:
- `Dockerfile`
- `.dockerignore`
- `requirements.txt`
- All application code

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Create Render.com Web Service

1. Go to https://render.com/
2. Sign up/Login
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Select your repository

### 3. Configure Web Service

**Basic Settings:**
- Name: `slackbot-content-assistant`
- Region: Choose closest to your users
- Branch: `main`
- Root Directory: Leave empty (unless code is in subdirectory)

**Build Settings:**
- Environment: `Docker`
- Dockerfile Path: `./Dockerfile`

**Plan:**
- Select "Free" tier (or paid if needed)

### 4. Add Environment Variables

Click "Advanced" → "Add Environment Variable"

Add all variables from `.env.example`:

```
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_APP_TOKEN=xapp-...
SUPABASE_URL=https://...
SUPABASE_KEY=...
REDIS_URL=redis://...
BRAVE_API_KEY=...
GROQ_API_KEY=...
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 5. Configure Health Check

- Health Check Path: `/health`
- Auto-Deploy: `Yes`

### 6. Deploy

1. Click "Create Web Service"
2. Wait for build to complete (5-10 minutes)
3. Check logs for any errors
4. Visit the provided URL

### 7. Verify Deployment

```bash
# Check health endpoint
curl https://your-app.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "slack": "healthy",
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### 8. Test in Slack

1. Go to your Slack workspace
2. Run `/process_keywords test keyword`
3. Verify bot responds

## Troubleshooting

### Build Fails

**Check Dockerfile syntax:**
```bash
docker build -t test .
```

**Check logs in Render dashboard**

### App Crashes on Startup

**Check environment variables:**
- Verify all required vars are set
- Check for typos in variable names

**Check logs:**
- Look for Python errors
- Verify dependencies installed

### Bot Not Responding

**Check Slack configuration:**
- Verify bot token is correct
- Check Socket Mode is enabled
- Verify bot is invited to channels

### Database Connection Issues

**Verify Supabase:**
- Check URL and key are correct
- Verify database tables exist
- Check network access (firewall)

## Updating Deployment

**Auto-deploy on push:**
```bash
git add .
git commit -m "Update feature"
git push origin main
# Render automatically deploys
```

**Manual deploy:**
1. Go to Render dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

## Monitoring

**View Logs:**
1. Go to Render dashboard
2. Click on your service
3. View "Logs" tab

**Set up Alerts:**
1. Render dashboard → Settings
2. Configure email notifications for:
   - Deploy failures
   - Service outages
   - High CPU/memory usage

## Keeping Service Alive (Free Tier)

Free tier services sleep after inactivity.

**Option 1: Use cron-job.org**
1. Go to https://cron-job.org
2. Create free account
3. Add new cron job:
   - URL: `https://your-app.onrender.com/health`
   - Schedule: Every 14 minutes

**Option 2: Use UptimeRobot**
1. Go to https://uptimerobot.com
2. Add new monitor
3. Monitor Type: HTTP(s)
4. URL: `https://your-app.onrender.com/health`
5. Interval: 5 minutes

## Backup Strategy

**Database Backups:**
- Supabase has automatic backups
- Export data periodically

**Code Backups:**
- Keep GitHub as source of truth
- Tag releases: `git tag v1.0.0`

## Scaling

**If you need more resources:**
1. Upgrade Render plan
2. Increase worker instances
3. Add Redis caching

**Performance optimization:**
- Enable Redis caching
- Optimize database queries
- Use CDN for static files

## Security

**Environment Variables:**
- Never commit `.env` to Git
- Rotate API keys periodically
- Use Render's secret storage

**Network Security:**
- Render provides HTTPS automatically
- No additional SSL config needed

## Cost Estimate

**Free Tier:**
- 750 hours/month free
- Sleeps after inactivity
- Limited resources

**Paid Tier ($7/month):**
- Always on
- More CPU/RAM
- Better performance

## Support

**Render Support:**
- Documentation: https://render.com/docs
- Community: https://community.render.com

**Project Issues:**
- GitHub Issues: [your-repo]/issues
```

**Testing:**
- Follow deployment guide step-by-step
- Verify each step works
- Test deployed application
- Check all features work in production

---

## SLACK-027: Set Up Monitoring & Logging

**Type:** DevOps  
**Priority:** High  
**Story Points:** 2  
**Estimated Time:** 1.5 hours  

**Description:**
Configure monitoring, logging, and alerting for production application.

**Acceptance Criteria:**
- [ ] Application logs centralized
- [ ] Error tracking configured
- [ ] Uptime monitoring active
- [ ] Performance metrics tracked
- [ ] Alerts configured for critical issues

**Deliverables:**
- Updated logging configuration
- Monitoring setup documentation

**Dependencies:** SLACK-026

**Code Implementation:**

```python
# app/utils/logger.py
import logging
import json
from datetime import datetime
from app.config import Config

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for production"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'batch_id'):
            log_data['batch_id'] = record.batch_id
        
        return json.dumps(log_data)

def setup_logging():
    """Configure logging for the application"""
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    if Config.ENVIRONMENT == 'production':
        # JSON format for production
        console_handler.setFormatter(JSONFormatter())
    else:
        # Human-readable format for development
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
    
    logger.addHandler(console_handler)
    
    return logger

# Usage in main.py
from app.utils.logger import setup_logging
logger = setup_logging()
```

```python
# app/utils/metrics.py
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def track_execution_time(func):
    """Decorator to track function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                f"Function {func.__name__} executed in {execution_time:.2f}s",
                extra={'execution_time': execution_time, 'function': func.__name__}
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed after {execution_time:.2f}s: {str(e)}",
                extra={'execution_time': execution_time, 'function': func.__name__, 'error': str(e)}
            )
            raise
    return wrapper

def log_event(event_type: str, **kwargs):
    """Log custom events for monitoring"""
    logger.info(
        f"Event: {event_type}",
        extra={'event_type': event_type, **kwargs}
    )

# Usage example in pipeline.py
from app.utils.metrics import track_execution_time, log_event

@track_execution_time
def _process_keywords(self, raw_keywords, source):
    log_event('processing_started', keyword_count=len(raw_keywords), source=source)
    # ... rest of processing
    log_event('processing_completed', keyword_count=len(cleaned_keywords))
```

```markdown
# MONITORING.md

# Monitoring & Alerting Setup

## Log Management

### Viewing Logs in Render

1. Go to Render dashboard
2. Select your service
3. Click "Logs" tab
4. Filter by log level or search text

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical issues

### Log Format (Production)

JSON format for easy parsing:
```json
{
  "timestamp": "2025-10-12T10:30:00Z",
  "level": "INFO",
  "logger": "app.services.pipeline",
  "message": "Processing started",
  "user_id": "U123456",
  "batch_id": "abc123"
}
```

## Uptime Monitoring

### Using UptimeRobot (Free)

1. Sign up at https://uptimerobot.com
2. Add New Monitor:
   - Monitor Type: HTTP(s)
   - Friendly Name: Slackbot Health Check
   - URL: https://your-app.onrender.com/health
   - Monitoring Interval: 5 minutes
3. Configure alerts:
   - Email notifications
   - SMS (paid feature)

### Using cron-job.org (Free)

1. Sign up at https://cron-job.org
2. Create New Cron Job:
   - Title: Keep Slackbot Alive
   - URL: https://your-app.onrender.com/health
   - Schedule: */14 * * * * (every 14 minutes)
3. Enable email notifications on failure

## Error Tracking

### Application Errors

Monitor these error patterns in logs:

**Database Errors:**
```
grep "Database connection failed" logs.txt
```

**API Errors:**
```
grep "API.*failed" logs.txt
```

**Processing Errors:**
```
grep "Pipeline error" logs.txt
```

### Setting Up Alerts

**Email Alerts via Render:**
1. Render Dashboard → Settings
2. Enable notifications for:
   - Deploy failures
   - Service crashes
   - High error rates

## Performance Metrics

### Key Metrics to Track

1. **Processing Time**
   - Average time per keyword
   - Total batch processing time
   - Search API response time

2. **Success Rate**
   - Successful batches / Total batches
   - Failed requests / Total requests

3. **Resource Usage**
   - CPU usage
   - Memory usage
   - Network bandwidth

### Monitoring in Render

1. Go to Metrics tab in Render dashboard
2. View:
   - CPU usage over time
   - Memory usage over time
   - HTTP requests
   - Response times

## Health Checks

### Endpoints

**Health Check:**
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "slack": "healthy",
    "database": "healthy",
    "redis": "healthy"
  }
}
```

**Readiness Check:**
```bash
curl https://your-app.onrender.com/ready
```

### Alert Conditions

Set up alerts for:
- Health check returns unhealthy status
- Response time > 5 seconds
- 5xx errors
- Service unavailable

## Dashboard (Optional)

For advanced monitoring, consider:

**Option 1: Grafana Cloud (Free Tier)**
- Visualize logs and metrics
- Create custom dashboards
- Set up advanced alerts

**Option 2: Datadog (Free Trial)**
- Full observability platform
- APM (Application Performance Monitoring)
- Log aggregation

**Option 3: New Relic (Free Tier)**
- Application monitoring
- Error tracking
- Performance insights

## Troubleshooting Guide

### High Memory Usage

**Symptoms:** App crashes, slow performance
**Solution:**
1. Check for memory leaks
2. Optimize embedding cache
3. Limit concurrent processing
4. Upgrade Render plan

### High Error Rate

**Symptoms:** Many failed requests
**Solution:**
1. Check API rate limits
2. Verify API keys valid
3. Check database connectivity
4. Review error logs

### Slow Processing

**Symptoms:** Timeouts, user complaints
**Solution:**
1. Enable Redis caching
2. Optimize database queries
3. Reduce search result count
4. Implement queue system

## Maintenance Tasks

### Daily
- Check error logs for anomalies
- Verify health check passing
- Monitor uptime

### Weekly
- Review performance metrics
- Check API usage against limits
- Verify backups working

### Monthly
- Rotate API keys
- Update dependencies
- Review and optimize costs
- Archive old data
```

**Testing:**
- Set up uptime monitoring
- Trigger test errors
- Verify alerts received
- Check log aggregation
- Test health endpoints

---

## Epic Completion Checklist

**All Tasks Complete:**
- [ ] SLACK-024: Dockerfile created
- [ ] SLACK-025: Production config ready
- [ ] SLACK-026: Deployed to Render.com
- [ ] SLACK-027: Monitoring configured

**Deployment Verification:**
- [ ] Application builds successfully
- [ ] Docker image size acceptable
- [ ] Health check endpoint working
- [ ] All environment variables set
- [ ] Application accessible via URL
- [ ] Bot responds in Slack
- [ ] Logs are readable
- [ ] Monitoring alerts configured

**Documentation:**
- [ ] DEPLOYMENT.md complete
- [ ] MONITORING.md complete
- [ ] Environment variables documented
- [ ] Troubleshooting guide written

**Ready for Production:**
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Security reviewed
- [ ] Backups configured
- [ ] Team has access to dashboards