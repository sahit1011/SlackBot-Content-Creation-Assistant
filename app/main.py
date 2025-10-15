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