from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_url="sqlite:///fitness_plans.db"):
        self.engine = create_engine(db_url)
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.SessionFactory)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()

    def init_db(self):
        """Initialize database tables"""
        from database.models import Base
        Base.metadata.create_all(self.engine)

db_manager = DatabaseManager()
