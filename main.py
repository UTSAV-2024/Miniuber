from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uvicorn
from datetime import datetime
from typing import List, Optional
import math

from database import get_db, create_tables, test_connection, RideRequest, User, Driver, initialize_sample_data

app = FastAPI(title="Mini Uber Real-time API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
create_tables()
db_available = test_connection()
if db_available:
    initialize_sample_data()

# Pydantic models
class UserCreate(BaseModel):
    user_id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None

class DriverCreate(BaseModel):
    driver_id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_number: Optional[str] = None
    license_number: Optional[str] = None

class RideRequestCreate(BaseModel):
    user_id: str
    pickup_location: str
    destination_location: str
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None

class RideStatusUpdate(BaseModel):
    status: str
    driver_id: Optional[str] = None

class DriverLocationUpdate(BaseModel):
    driver_id: str
    lat: float
    lng: float

class DriverStatusUpdate(BaseModel):
    driver_id: str
    status: str  # online, offline, busy

@app.get("/")
async def root():
    return {"message": "Welcome to Mini Uber Real-time API v2.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if db_available else "disconnected",
        "version": "2.0.0"
    }

# ------------------------------
# USER ENDPOINTS
# ------------------------------

@app.post("/api/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.user_id == user.user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        db_user = User(
            user_id=user.user_id,
            name=user.name,
            phone=user.phone,
            email=user.email
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {"success": True, "message": "User created successfully", "user": db_user}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ride-request")
async def create_ride_request(ride_request: RideRequestCreate, db: Session = Depends(get_db)):
    """User creates a ride request"""
    try:
        # Verify user exists
        user = db.query(User).filter(User.user_id == ride_request.user_id).first()
        if not user:
            # Create user if doesn't exist
            user = User(user_id=ride_request.user_id, name=f"User {ride_request.user_id}")
            db.add(user)
            db.commit()
        
        # Calculate estimated fare (basic calculation)
        estimated_fare = 50.0  # Base fare
        if ride_request.pickup_lat and ride_request.destination_lat:
            distance = calculate_distance(
                ride_request.pickup_lat, ride_request.pickup_lng,
                ride_request.destination_lat, ride_request.destination_lng
            )
            estimated_fare += distance * 12  # ₹12 per km
        
        db_ride_request = RideRequest(
            user_id=ride_request.user_id,
            pickup_location=ride_request.pickup_location,
            destination_location=ride_request.destination_location,
            pickup_lat=ride_request.pickup_lat,
            pickup_lng=ride_request.pickup_lng,
            destination_lat=ride_request.destination_lat,
            destination_lng=ride_request.destination_lng,
            estimated_fare=estimated_fare,
            status="pending"
        )
        
        db.add(db_ride_request)
        db.commit()
        db.refresh(db_ride_request)
        
        return {
            "success": True,
            "message": "Ride request created successfully",
            "ride_request": {
                "id": db_ride_request.id,
                "user_id": db_ride_request.user_id,
                "pickup_location": db_ride_request.pickup_location,
                "destination_location": db_ride_request.destination_location,
                "status": db_ride_request.status,
                "estimated_fare": db_ride_request.estimated_fare,
                "created_at": db_ride_request.created_at.isoformat()
            }
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{user_id}/rides")
async def get_user_rides(user_id: str, db: Session = Depends(get_db)):
    """Get all rides for a specific user"""
    try:
        rides = db.query(RideRequest).filter(RideRequest.user_id == user_id).order_by(RideRequest.created_at.desc()).all()
        
        rides_data = []
        for ride in rides:
            ride_data = {
                "id": ride.id,
                "pickup_location": ride.pickup_location,
                "destination_location": ride.destination_location,
                "status": ride.status,
                "estimated_fare": ride.estimated_fare,
                "actual_fare": ride.actual_fare,
                "created_at": ride.created_at.isoformat(),
                "driver_name": ride.driver.name if ride.driver else None,
                "driver_phone": ride.driver.phone if ride.driver else None,
                "vehicle_number": ride.driver.vehicle_number if ride.driver else None
            }
            rides_data.append(ride_data)
        
        return {
            "success": True,
            "count": len(rides_data),
            "rides": rides_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------
# DRIVER ENDPOINTS
# ------------------------------

@app.post("/api/drivers")
async def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    """Create a new driver"""
    try:
        # Check if driver already exists
        existing_driver = db.query(Driver).filter(Driver.driver_id == driver.driver_id).first()
        if existing_driver:
            raise HTTPException(status_code=400, detail="Driver already exists")
        
        db_driver = Driver(
            driver_id=driver.driver_id,
            name=driver.name,
            phone=driver.phone,
            email=driver.email,
            vehicle_type=driver.vehicle_type,
            vehicle_number=driver.vehicle_number,
            license_number=driver.license_number,
            status="offline"
        )
        
        db.add(db_driver)
        db.commit()
        db.refresh(db_driver)
        
        return {"success": True, "message": "Driver created successfully", "driver": db_driver}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/drivers/available-rides")
async def get_available_rides(db: Session = Depends(get_db)):
    """Get all pending ride requests for drivers to see"""
    try:
        rides = db.query(RideRequest).filter(
            RideRequest.status.in_(["pending", "accepted"])
        ).order_by(RideRequest.created_at.desc()).all()
        
        rides_data = []
        for ride in rides:
            ride_data = {
                "id": ride.id,
                "user_name": ride.user.name if ride.user else "Unknown User",
                "pickup_location": ride.pickup_location,
                "destination_location": ride.destination_location,
                "status": ride.status,
                "estimated_fare": ride.estimated_fare,
                "pickup_lat": ride.pickup_lat,
                "pickup_lng": ride.pickup_lng,
                "created_at": ride.created_at.isoformat(),
                "driver_name": ride.driver.name if ride.driver else None
            }
            rides_data.append(ride_data)
        
        return {
            "success": True,
            "count": len(rides_data),
            "rides": rides_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/rides/{ride_id}/status")
async def update_ride_status(ride_id: int, status_update: RideStatusUpdate, db: Session = Depends(get_db)):
    """Update ride status (accept/reject/complete etc.)"""
    try:
        ride = db.query(RideRequest).filter(RideRequest.id == ride_id).first()
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
        
        valid_statuses = ["pending", "accepted", "in_progress", "completed", "cancelled", "rejected"]
        if status_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        # Update ride status
        old_status = ride.status
        ride.status = status_update.status
        
        # If accepting a ride, assign driver
        if status_update.status == "accepted" and status_update.driver_id:
            ride.driver_id = status_update.driver_id
            ride.accepted_at = datetime.utcnow()
            
            # Update driver status to busy
            driver = db.query(Driver).filter(Driver.driver_id == status_update.driver_id).first()
            if driver:
                driver.status = "busy"
        
        # If completing a ride, free up the driver
        elif status_update.status == "completed":
            ride.completed_at = datetime.utcnow()
            if ride.driver_id:
                driver = db.query(Driver).filter(Driver.driver_id == ride.driver_id).first()
                if driver:
                    driver.status = "online"
        
        # If starting a ride
        elif status_update.status == "in_progress":
            ride.started_at = datetime.utcnow()
        
        ride.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ride)
        
        return {
            "success": True,
            "message": f"Ride status updated from {old_status} to {status_update.status}",
            "ride": {
                "id": ride.id,
                "status": ride.status,
                "driver_id": ride.driver_id,
                "updated_at": ride.updated_at.isoformat()
            }
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/drivers/location")
async def update_driver_location(location_update: DriverLocationUpdate, db: Session = Depends(get_db)):
    """Update driver's current location"""
    try:
        driver = db.query(Driver).filter(Driver.driver_id == location_update.driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        driver.current_lat = location_update.lat
        driver.current_lng = location_update.lng
        driver.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Driver location updated successfully",
            "driver_id": driver.driver_id,
            "location": {"lat": driver.current_lat, "lng": driver.current_lng}
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/drivers/status")
async def update_driver_status(status_update: DriverStatusUpdate, db: Session = Depends(get_db)):
    """Update driver's availability status"""
    try:
        driver = db.query(Driver).filter(Driver.driver_id == status_update.driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        valid_statuses = ["online", "offline", "busy"]
        if status_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        driver.status = status_update.status
        driver.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Driver status updated to {status_update.status}",
            "driver_id": driver.driver_id,
            "status": driver.status
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------
# ADMIN/MONITORING ENDPOINTS
# ------------------------------

@app.get("/api/rides/all")
async def get_all_rides(db: Session = Depends(get_db)):
    """Get all rides for admin monitoring"""
    try:
        rides = db.query(RideRequest).order_by(RideRequest.created_at.desc()).all()
        
        rides_data = []
        for ride in rides:
            ride_data = {
                "id": ride.id,
                "user_name": ride.user.name if ride.user else "Unknown",
                "driver_name": ride.driver.name if ride.driver else None,
                "pickup_location": ride.pickup_location,
                "destination_location": ride.destination_location,
                "status": ride.status,
                "estimated_fare": ride.estimated_fare,
                "actual_fare": ride.actual_fare,
                "created_at": ride.created_at.isoformat(),
                "pickup_lat": ride.pickup_lat,
                "pickup_lng": ride.pickup_lng
            }
            rides_data.append(ride_data)
        
        return {
            "success": True,
            "count": len(rides_data),
            "rides": rides_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/drivers/all")
async def get_all_drivers(db: Session = Depends(get_db)):
    """Get all drivers for admin monitoring"""
    try:
        drivers = db.query(Driver).all()
        
        drivers_data = []
        for driver in drivers:
            driver_data = {
                "id": driver.id,
                "driver_id": driver.driver_id,
                "name": driver.name,
                "phone": driver.phone,
                "vehicle_type": driver.vehicle_type,
                "vehicle_number": driver.vehicle_number,
                "rating": driver.rating,
                "status": driver.status,
                "current_lat": driver.current_lat,
                "current_lng": driver.current_lng,
                "updated_at": driver.updated_at.isoformat() if driver.updated_at else None
            }
            drivers_data.append(driver_data)
        
        return {
            "success": True,
            "count": len(drivers_data),
            "drivers": drivers_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------
# UTILITY FUNCTIONS
# ------------------------------

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    if not all([lat1, lng1, lat2, lng2]):
        return 0.0
    
    R = 6371  # Earth's radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) * math.sin(dlng / 2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)