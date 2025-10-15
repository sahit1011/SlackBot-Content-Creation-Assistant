# Deployment Guide for Render.com

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