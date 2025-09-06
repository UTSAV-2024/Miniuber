<<<<<<< HEAD
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
=======
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, text
>>>>>>> 847e6db0f34e5219b43095e5fef90d575c7fb6af
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from decouple import config

<<<<<<< HEAD
# Use SQLite only - no PostgreSQL dependency needed
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./ride_requests.db")# Create engine (compatible with SQLAlchemy 1.4)
engine = create_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
=======
# Load database URL from .env file or fallback to SQLite
DATABASE_URL = config("postgresql+psycopg2://postgres:yourpassword@localhost:5432/postgres", default="sqlite:///./ride_requests.db")


# Create engine
engine = create_engine(DATABASE_URL, echo=True, future=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
>>>>>>> 847e6db0f34e5219b43095e5fef90d575c7fb6af

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
<<<<<<< HEAD
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
=======
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
>>>>>>> 847e6db0f34e5219b43095e5fef90d575c7fb6af


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
<<<<<<< HEAD
        return False
=======
        return False
>>>>>>> 847e6db0f34e5219b43095e5fef90d575c7fb6af
