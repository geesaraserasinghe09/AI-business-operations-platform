import logging
from app.core.database import engine, Base
import app.models  # Ensure all models are registered

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")


if __name__ == "__main__":
    init_db()
