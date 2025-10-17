# SlackBot Content Creation Assistant

A sophisticated Slack bot that helps content creators process keywords, generate ideas, and create structured content outlines using AI-powered analysis and web research.


## 🚀 Features

- **Keyword Processing**: Clean, parse, and cluster keywords from various sources
- **Content Research**: Automated web scraping and search using Brave Search API
- **AI-Powered Analysis**: Generate content ideas and outlines using Groq LLM
- **Content Clustering**: Group related keywords using sentence transformers
- **Slack Integration**: Seamless integration with Slack workspaces
- **Database Storage**: Persistent storage using Supabase
- **Caching**: Redis-based caching for improved performance
- **Email Reports**: Send PDF reports via SendGrid
- **Health Monitoring**: Built-in health checks and monitoring
- **Docker Deployment**: Production-ready containerized deployment

## 🏗️ Architecture

```
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── health.py            # Health check endpoints
│   ├── handlers/            # Slack event/command handlers
│   ├── models/              # Data models
│   │   ├── batch.py         # Batch processing model
│   │   ├── user.py          # User model
│   │   └── cluster.py       # Keyword cluster model
│   ├── services/            # Core business logic (modularized)
│   │   ├── ai/              # AI-powered services
│   │   │   ├── embedding_generator.py
│   │   │   ├── idea_generator.py
│   │   │   └── outline_generator.py
│   │   ├── data/            # Data persistence services
│   │   │   ├── database.py
│   │   │   └── cache.py
│   │   ├── external/        # External API integrations
│   │   │   ├── web_search.py
│   │   │   └── email_service.py
│   │   └── processing/      # Core processing logic
│   │       ├── pipeline.py      # Main processing pipeline
│   │       ├── keyword_cleaner.py
│   │       ├── keyword_parser.py
│   │       ├── keyword_clusterer.py
│   │       ├── content_scraper.py
│   │       └── report_generator.py
│   └── utils/
│       └── slack_formatters.py
├── tests/                  # Test suite (moved from root)
├── migrations/             # Database migrations
├── docs/                   # Documentation
│   ├── Epics/              # Project epics and features
│   ├── assignment.md       # Assignment documentation
│   ├── DEPLOYMENT.md       # Deployment guide
│   ├── prd_doc.md          # Product requirements
│   └── task_manager.md     # Task management
├── Dockerfile              # Container configuration
├── .dockerignore           # Docker ignore rules
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

## 🛠️ Tech Stack

- **Backend**: Python 3.11, Flask
- **AI/ML**: Sentence Transformers, Groq API
- **Database**: Supabase (PostgreSQL)
- **Cache**: Redis (Upstash)
- **Search**: Brave Search API
- **Email**: SendGrid
- **Deployment**: Docker, Render.com
- **Monitoring**: Health checks, logging

## 📋 Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- Slack App with Bot Token
- Supabase account
- Redis instance (Upstash recommended)
- API Keys: Brave Search, Groq, SendGrid

## 🧪 Testing the SlackBot

### How to Test (Anyone Can Try!)

Since Slack bot tokens are workspace-specific, **you cannot use the hosted instance directly**. Instead, follow these steps to test the bot in your own Slack workspace:

#### Step 1: Create Your Slack App

1. **Go to [Slack API](https://api.slack.com/apps)**
2. **Click "Create New App" → "From scratch"**
3. **Enter App Name:** `Content Creation Assistant Test`
4. **Select your workspace**

#### Step 2: Configure Permissions

Go to "OAuth & Permissions" and add these **Bot Token Scopes**:
```
app_mentions:read
channels:history
channels:read
chat:write
chat:write.public
files:write
users:read
```

#### Step 3: Configure Events

Go to "Event Subscriptions":
- **Enable Events**
- **Request URL:** `https://your-deployment.onrender.com/slack/events`
- **Subscribe to bot events:**
  ```
  app_mention
  message.channels
  ```

#### Step 4: Install & Get Tokens

1. **Install to Workspace**
2. **Copy your Bot User OAuth Token** (starts with `xoxb-`)
3. **Copy your Signing Secret**

#### Step 5: Deploy Test Instance

**Option A: Quick Deploy (Recommended)**
1. **Fork this repository**
2. **Create new Render service** from your fork
3. **Set environment variables:**
   ```bash
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_SIGNING_SECRET=your-signing-secret
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   GROQ_API_KEY=your-groq-key
   SERP_API_KEY=your-serp-key
   BRAVE_API_KEY=your-brave-key
   SENDGRID_API_KEY=your-sendgrid-key
   SENDGRID_FROM_EMAIL=your-verified-email
   ```

**Option B: Use App Manifest (Even Faster)**
Use this JSON to recreate the exact app configuration:

```json
{
  "display_information": {
    "name": "Content Creation Assistant",
    "description": "AI-powered content strategy and keyword analysis bot",
    "background_color": "#4A154B"
  },
  "features": {
    "bot_user": {
      "display_name": "Content Assistant",
      "always_online": true
    }
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "channels:history",
        "channels:read",
        "chat:write",
        "chat:write.public",
        "files:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "message.channels"
      ]
    },
    "interactivity": {
      "is_enabled": true
    },
    "org_deploy_enabled": false,
    "socket_mode_enabled": false,
    "token_rotation_enabled": false
  }
}
```

#### Step 6: Test Commands

Once deployed, invite the bot and test:

```
/invite @Content Creation Assistant
/process_keywords running shoes, yoga mats, protein powder
/history
/regenerate abc12345
/set_email your@email.com
/export notion abc12345
```

### Demo Video/Screenshots

The bot will:
1. ✅ Process keywords and create semantic clusters
2. ✅ Research top content for each cluster
3. ✅ Generate AI-powered outlines and post ideas
4. ✅ Upload comprehensive PDF reports
5. ✅ Send reports via email (if configured)

---

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/sahit1011/SlackBot-Content-Creation-Assistant.git
   cd SlackBot-Content-Creation-Assistant
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run the application**
   ```bash
   python app/main.py
   ```

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t slackbot-content-assistant .
   ```

2. **Run the container**
   ```bash
   docker run -p 3000:3000 --env-file .env slackbot-content-assistant
   ```

3. **Test health endpoint**
   ```bash
   curl http://localhost:3000/health
   ```

## 📚 Usage

### Slack Commands

**Core Commands:**
- `/process_keywords` - Start keyword processing workflow
- `/history` - View past processing batches with action buttons
- `/set_email` - Set email for automatic PDF delivery

**Bonus Features:**
- `/regenerate [batch_id] [cluster_number]` - Regenerate outlines for existing batches
- `/export notion [batch_id]` - Export to Notion (requires setup)
- `/export sheets [batch_id]` - Export to Google Sheets (requires setup)

### Bot Features

1. **Keyword Processing Pipeline:**
   - Parse and clean keywords from text or CSV
   - Generate semantic embeddings
   - Cluster related keywords
   - Research top content for each cluster

2. **AI-Powered Content Generation:**
   - Generate structured outlines using Groq LLM
   - Create post ideas with target audiences
   - Produce comprehensive PDF reports

3. **Export Integrations:**
   - **Notion**: Structured pages with clusters, outlines, and ideas
   - **Google Sheets**: Multi-sheet spreadsheets with all data
   - **Email**: Automatic PDF delivery to configured addresses

### API Endpoints

- `GET /health` - Health check
- `GET /ready` - Readiness check
- `POST /slack/events` - Slack webhook endpoint

### API Endpoints

- `GET /health` - Health check
- `GET /ready` - Readiness check

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SLACK_BOT_TOKEN` | Slack bot token | Yes |
| `SLACK_SIGNING_SECRET` | Slack signing secret | Yes |
| `SLACK_APP_TOKEN` | Slack app token | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anon key | Yes |
| `REDIS_URL` | Redis connection URL | No |
| `BRAVE_API_KEY` | Brave Search API key | No |
| `GROQ_API_KEY` | Groq API key | No |
| `SENDGRID_API_KEY` | SendGrid API key | No |
| `SENDGRID_FROM_EMAIL` | Verified sender email | No |
| `NOTION_API_KEY` | Notion API key (for export) | No |
| `NOTION_DATABASE_ID` | Notion database ID (for export) | No |
| `GOOGLE_CREDENTIALS_FILE` | Google service account JSON path | No |
| `ENVIRONMENT` | Environment (development/production) | No |
| `LOG_LEVEL` | Logging level | No |
| `MAX_KEYWORDS` | Maximum keywords to process | No |
| `MAX_CLUSTERS` | Maximum clusters to generate | No |
| `PROCESSING_TIMEOUT` | Processing timeout in seconds | No |
| `HEALTH_CHECK_PORT` | Health check port | No |

## 🚀 Deployment

For production deployment to Render.com, see [DEPLOYMENT.md](DEPLOYMENT.md)

### Key Features

- **Auto-deployment** from GitHub
- **Health checks** for service monitoring
- **Environment-specific** configuration
- **Docker containerization**
- **Free tier** available

## 📊 Monitoring

### Health Checks

The application provides health check endpoints:
- `/health` - Overall health status
- `/ready` - Readiness for traffic

### Logging

- JSON format in production
- Structured logging with context
- Configurable log levels

### Metrics

- Processing time tracking
- Success/failure rates
- Resource usage monitoring

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Note: Tests have been moved to the `tests/` directory for better organization.

### Test Coverage

- Unit tests for all services
- Integration tests for pipeline
- API endpoint testing
- Slack command testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Slack Bolt](https://slack.dev/bolt-python/) for Slack integration
- [Sentence Transformers](https://www.sbert.net/) for embeddings
- [Groq](https://groq.com/) for LLM services
- [Supabase](https://supabase.com/) for database
- [Render](https://render.com/) for hosting

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the deployment guide
- Review the troubleshooting section

---

**Happy content creating! 🎉**
