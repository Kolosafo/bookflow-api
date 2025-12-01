from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class BooksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "books"

    def ready(self):
        """
        Initialize the background scheduler when Django starts.
        This scheduler handles one-off async tasks like book summary generation.
        """
        # Only start the scheduler if this is not a management command
        # and not during migrations
        import sys

        # Don't start scheduler during migrations, collectstatic, or the scheduler command itself
        if 'migrate' not in sys.argv and 'collectstatic' not in sys.argv and 'scheduler' not in sys.argv:
            try:
                from .scheduler import scheduler

                # Only start if not already running
                if not scheduler.running:
                    scheduler.start()
                    logger.info("Background scheduler started successfully for async tasks.")
            except Exception as e:
                logger.error(f"Failed to start background scheduler: {e}")
