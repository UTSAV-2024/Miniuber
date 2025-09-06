from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from decouple import config

# Use SQLite only - no PostgreSQL dependency needed
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./ride_requests.db")# Create engine (compatible with SQLAlchemy 1.4)
engine = create_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# ------------------------------
# Database Models
# ------------------------------
class RideRequest(Base):
    __tablename__ = "ride_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False)
    source_location = Column(String(255), nullable=False)
    dest_location = Column(String(255), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ------------------------------
# Create tables
# ------------------------------
def create_tables():
    Base.metadata.create_all(bind=engine)


# ------------------------------
# Dependency for FastAPI routes
# ------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------
# Test database connection
# ------------------------------
def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Will use fallback mode")
        return False