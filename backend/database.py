"""
Database Configuration and Session Management
SQLAlchemy setup for PostgreSQL and SQLite
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./analytics_dashboard.db"  # Default to SQLite for development
)

# For PostgreSQL in production:
# DATABASE_URL = "postgresql://user:password@localhost/analytics_dashboard"

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Set to True for SQL debugging
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    Used with FastAPI's Depends()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        from models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def drop_tables():
    """Drop all database tables (use with caution!)"""
    try:
        from models import Base
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise

def init_database():
    """Initialize database with default data"""
    try:
        create_tables()
        
        # Create default admin user if it doesn't exist
        db = SessionLocal()
        try:
            from models import User
            from auth import get_password_hash
            
            admin_user = db.query(User).filter(User.username == "admin").first()
            if not admin_user:
                admin_user = User(
                    username="admin",
                    email="admin@analytics-dashboard.com",
                    hashed_password=get_password_hash("admin123"),
                    full_name="System Administrator",
                    role="admin",
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                db.commit()
                logger.info("Default admin user created")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def get_connection_info():
        """Get database connection information"""
        return {
            "database_url": DATABASE_URL,
            "engine_info": str(engine.url),
            "pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else None,
            "checked_out": engine.pool.checkedout() if hasattr(engine.pool, 'checkedout') else None
        }
    
    @staticmethod
    def health_check():
        """Check database connectivity"""
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    def get_table_info():
        """Get information about database tables"""
        try:
            from models import Base
            metadata = Base.metadata
            
            tables_info = {}
            for table_name, table in metadata.tables.items():
                tables_info[table_name] = {
                    "columns": [col.name for col in table.columns],
                    "primary_keys": [col.name for col in table.primary_key.columns],
                    "foreign_keys": [
                        {
                            "column": fk.parent.name,
                            "references": f"{fk.column.table.name}.{fk.column.name}"
                        }
                        for fk in table.foreign_keys
                    ]
                }
            
            return tables_info
            
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return {}
    
    @staticmethod
    def backup_database(backup_path: str = None):
        """Create database backup (SQLite only)"""
        if not DATABASE_URL.startswith("sqlite"):
            raise NotImplementedError("Backup only supported for SQLite databases")
        
        import shutil
        from datetime import datetime
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_analytics_dashboard_{timestamp}.db"
        
        try:
            db_path = DATABASE_URL.replace("sqlite:///", "")
            shutil.copy2(db_path, backup_path)
            logger.info(f"Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            raise
    
    @staticmethod
    def restore_database(backup_path: str):
        """Restore database from backup (SQLite only)"""
        if not DATABASE_URL.startswith("sqlite"):
            raise NotImplementedError("Restore only supported for SQLite databases")
        
        import shutil
        
        try:
            db_path = DATABASE_URL.replace("sqlite:///", "")
            shutil.copy2(backup_path, db_path)
            logger.info(f"Database restored from: {backup_path}")
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            raise

# Repository pattern for data access
class BaseRepository:
    """Base repository class with common CRUD operations"""
    
    def __init__(self, db: Session, model_class):
        self.db = db
        self.model_class = model_class
    
    def create(self, obj_data: dict):
        """Create new record"""
        db_obj = self.model_class(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get(self, obj_id: str):
        """Get record by ID"""
        return self.db.query(self.model_class).filter(self.model_class.id == obj_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        """Get all records with pagination"""
        return self.db.query(self.model_class).offset(skip).limit(limit).all()
    
    def update(self, obj_id: str, obj_data: dict):
        """Update record"""
        db_obj = self.get(obj_id)
        if db_obj:
            for key, value in obj_data.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, obj_id: str):
        """Delete record"""
        db_obj = self.get(obj_id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
        return db_obj
    
    def count(self):
        """Count total records"""
        return self.db.query(self.model_class).count()

class DatasetRepository(BaseRepository):
    """Repository for Dataset operations"""
    
    def __init__(self, db: Session):
        from models import Dataset
        super().__init__(db, Dataset)
    
    def get_by_user(self, user_id: str, skip: int = 0, limit: int = 100):
        """Get datasets by user ID"""
        return (self.db.query(self.model_class)
                .filter(self.model_class.user_id == user_id)
                .offset(skip)
                .limit(limit)
                .all())
    
    def get_processed(self, skip: int = 0, limit: int = 100):
        """Get processed datasets"""
        return (self.db.query(self.model_class)
                .filter(self.model_class.is_processed == True)
                .offset(skip)
                .limit(limit)
                .all())

class VisualizationRepository(BaseRepository):
    """Repository for Visualization operations"""
    
    def __init__(self, db: Session):
        from models import Visualization
        super().__init__(db, Visualization)
    
    def get_by_dataset(self, dataset_id: str):
        """Get visualizations by dataset ID"""
        return (self.db.query(self.model_class)
                .filter(self.model_class.dataset_id == dataset_id)
                .all())
    
    def get_by_type(self, viz_type: str, skip: int = 0, limit: int = 100):
        """Get visualizations by type"""
        return (self.db.query(self.model_class)
                .filter(self.model_class.viz_type == viz_type)
                .offset(skip)
                .limit(limit)
                .all())

# Initialize database on import
if __name__ == "__main__":
    init_database()
    print("Database initialized successfully")