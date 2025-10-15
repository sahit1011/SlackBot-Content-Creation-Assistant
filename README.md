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
│   ├── services/            # Core business logic
│   │   ├── pipeline.py      # Main processing pipeline
│   │   ├── keyword_cleaner.py
│   │   ├── keyword_parser.py
│   │   ├── keyword_clusterer.py
│   │   ├── embedding_generator.py
│   │   ├── content_scraper.py
│   │   ├── web_search.py
│   │   ├── idea_generator.py
│   │   ├── outline_generator.py
│   │   ├── report_generator.py
│   │   ├── database.py
│   │   ├── cache.py
│   │   └── email_service.py
│   └── utils/
│       └── slack_formatters.py
├── migrations/              # Database migrations
├── Epics/                   # Project documentation
├── Dockerfile               # Container configuration
├── .dockerignore           # Docker ignore rules
├── requirements.txt        # Python dependencies
├── DEPLOYMENT.md           # Deployment guide
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

- `/process_keywords` - Start keyword processing workflow
- `/history` - View past processing batches
- `/set_email` - Set email for PDF reports

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