from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from decouple import config
import os

# Database URL - use your miniuber-user database
DATABASE_URL = config("DATABASE_URL", default="postgresql://postgres:yourpassword@localhost:5432/miniuber-user")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# ------------------------------
# Database Models
# ------------------------------

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    ride_requests = relationship("RideRequest", back_populates="user")

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    vehicle_type = Column(String(50))
    vehicle_number = Column(String(20))
    license_number = Column(String(50))
    rating = Column(Float, default=4.5)
    status = Column(String(20), default="offline")  # online, offline, busy
    current_lat = Column(Float)
    current_lng = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    ride_requests = relationship("RideRequest", back_populates="driver")

class RideRequest(Base):
    __tablename__ = "ride_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    driver_id = Column(String(50), ForeignKey("drivers.driver_id"), nullable=True)
    
    # Location details
    pickup_location = Column(String(255), nullable=False)
    destination_location = Column(String(255), nullable=False)
    pickup_lat = Column(Float)
    pickup_lng = Column(Float)
    destination_lat = Column(Float)
    destination_lng = Column(Float)
    
    # Ride details
    status = Column(String(20), default="pending")  # pending, accepted, in_progress, completed, cancelled, rejected
    estimated_fare = Column(Float)
    actual_fare = Column(Float)
    distance_km = Column(Float)
    estimated_duration_minutes = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    accepted_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="ride_requests")
    driver = relationship("Driver", back_populates="ride_requests")

# ------------------------------
# Create all tables
# ------------------------------
def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

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
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# ------------------------------
# Initialize sample data
# ------------------------------
def initialize_sample_data():
    """Initialize with sample users and drivers"""
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Sample data already exists, skipping initialization.")
            return
        
        # Sample users
        sample_users = [
            User(user_id="user001", name="John Smith", phone="+91-9876543210", email="john@example.com"),
            User(user_id="user002", name="Sarah Wilson", phone="+91-9876543211", email="sarah@example.com"),
            User(user_id="user003", name="Mike Johnson", phone="+91-9876543212", email="mike@example.com"),
        ]
        
        # Sample drivers
        sample_drivers = [
            Driver(
                driver_id="driver001",
                name="Rajesh Kumar",
                phone="+91-9876543220",
                email="rajesh@example.com",
                vehicle_type="Sedan",
                vehicle_number="DL-01-AB-1234",
                license_number="DL123456789",
                rating=4.8,
                status="online",
                current_lat=28.6139,
                current_lng=77.2090
            ),
            Driver(
                driver_id="driver002",
                name="Amit Singh",
                phone="+91-9876543221",
                email="amit@example.com",
                vehicle_type="Hatchback",
                vehicle_number="DL-02-CD-5678",
                license_number="DL987654321",
                rating=4.6,
                status="online",
                current_lat=28.6200,
                current_lng=77.2100
            ),
            Driver(
                driver_id="driver003",
                name="Priya Sharma",
                phone="+91-9876543222",
                email="priya@example.com",
                vehicle_type="SUV",
                vehicle_number="DL-03-EF-9012",
                license_number="DL456789123",
                rating=4.9,
                status="online",
                current_lat=28.6100,
                current_lng=77.2050
            ),
        ]
        
        # Add to database
        for user in sample_users:
            db.add(user)
        for driver in sample_drivers:
            db.add(driver)
        
        db.commit()
        print("✅ Sample data initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing database connection...")
    if test_connection():
        print("Creating tables...")
        create_tables()
        print("Initializing sample data...")
        initialize_sample_data()
        print("✅ Database setup complete!")
    else:
        print("❌ Database setup failed!")