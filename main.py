<<<<<<< HEAD
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
=======
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uvicorn
from datetime import datetime
<<<<<<< HEAD
from typing import List, Optional, Dict
import math
import json
import asyncio

from database import get_db, create_tables, test_connection, RideRequest, User, Driver, initialize_sample_data

app = FastAPI(title="Mini Uber Real-time API with End Ride", version="2.2.0")
=======
from typing import List, Optional
import math

from database import get_db, create_tables, test_connection, RideRequest, User, Driver, initialize_sample_data

app = FastAPI(title="Mini Uber Real-time API", version="2.0.0")
>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "user": [],
            "driver": [], 
            "admin": []
        }

    async def connect(self, websocket: WebSocket, client_type: str):
        await websocket.accept()
        self.active_connections[client_type].append(websocket)
        print(f"New {client_type} connection established")

    def disconnect(self, websocket: WebSocket, client_type: str):
        if websocket in self.active_connections[client_type]:
            self.active_connections[client_type].remove(websocket)
            print(f"{client_type} connection closed")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_type(self, message: dict, client_type: str):
        """Broadcast message to all clients of a specific type"""
        connections = self.active_connections[client_type].copy()
        for connection in connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # Remove dead connections
                self.active_connections[client_type].remove(connection)

    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected clients"""
        for client_type in self.active_connections:
            await self.broadcast_to_type(message, client_type)

manager = ConnectionManager()

=======
>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
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

<<<<<<< HEAD
class RideEndRequest(BaseModel):
    ended_by: str  # 'user' or 'driver'
    reason: Optional[str] = None
    final_fare: Optional[float] = None

=======
>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
class DriverLocationUpdate(BaseModel):
    driver_id: str
    lat: float
    lng: float

class DriverStatusUpdate(BaseModel):
    driver_id: str
<<<<<<< HEAD
    status: str

# WebSocket endpoints
@app.websocket("/ws/user")
async def websocket_user(websocket: WebSocket):
    await manager.connect(websocket, "user")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "user")

@app.websocket("/ws/driver")
async def websocket_driver(websocket: WebSocket):
    await manager.connect(websocket, "driver")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "driver")

@app.websocket("/ws/admin")
async def websocket_admin(websocket: WebSocket):
    await manager.connect(websocket, "admin")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "admin")

# Helper functions
async def broadcast_ride_update(ride_data: dict, event_type: str):
    message = {
        "type": event_type,
        "data": ride_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_all(message)

async def broadcast_driver_update(driver_data: dict, event_type: str):
    message = {
        "type": event_type, 
        "data": driver_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_all(message)

# API endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Mini Uber API with End Ride functionality v2.2"}
=======
    status: str  # online, offline, busy

@app.get("/")
async def root():
    return {"message": "Welcome to Mini Uber Real-time API v2.0"}
>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if db_available else "disconnected",
<<<<<<< HEAD
        "version": "2.2.0",
        "websocket_connections": {
            "users": len(manager.active_connections["user"]),
            "drivers": len(manager.active_connections["driver"]),
            "admins": len(manager.active_connections["admin"])
        }
    }

=======
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

>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
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
        
<<<<<<< HEAD
        # Calculate estimated fare
        estimated_fare = 50.0
=======
        # Calculate estimated fare (basic calculation)
        estimated_fare = 50.0  # Base fare
>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
        if ride_request.pickup_lat and ride_request.destination_lat:
            distance = calculate_distance(
                ride_request.pickup_lat, ride_request.pickup_lng,
                ride_request.destination_lat, ride_request.destination_lng
            )
<<<<<<< HEAD
            estimated_fare += distance * 12
=======
            estimated_fare += distance * 12  # ₹12 per km
>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
        
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
        
<<<<<<< HEAD
        # Prepare ride data for broadcast
        ride_data = {
            "id": db_ride_request.id,
            "user_id": db_ride_request.user_id,
            "user_name": user.name,
            "pickup_location": db_ride_request.pickup_location,
            "destination_location": db_ride_request.destination_location,
            "status": db_ride_request.status,
            "estimated_fare": db_ride_request.estimated_fare,
            "created_at": db_ride_request.created_at.isoformat()
        }
        
        # Broadcast new ride request
        await broadcast_ride_update(ride_data, "new_ride_request")
        
        return {
            "success": True,
            "message": "Ride request created successfully",
            "ride_request": ride_data
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/rides/{ride_id}/status")
async def update_ride_status(ride_id: int, status_update: RideStatusUpdate, db: Session = Depends(get_db)):
    """Update ride status"""
    try:
        ride = db.query(RideRequest).filter(RideRequest.id == ride_id).first()
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
        
        valid_statuses = ["pending", "accepted", "in_progress", "completed", "cancelled", "rejected"]
        if status_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        old_status = ride.status
        ride.status = status_update.status
        
        # Handle driver assignment and status updates
        driver = None
        if status_update.status == "accepted" and status_update.driver_id:
            ride.driver_id = status_update.driver_id
            ride.accepted_at = datetime.utcnow()
            
            driver = db.query(Driver).filter(Driver.driver_id == status_update.driver_id).first()
            if driver:
                driver.status = "busy"
        
        elif status_update.status == "in_progress":
            ride.started_at = datetime.utcnow()
            
        elif status_update.status == "completed":
            ride.completed_at = datetime.utcnow()
            if ride.driver_id:
                driver = db.query(Driver).filter(Driver.driver_id == ride.driver_id).first()
                if driver:
                    driver.status = "online"
        
        ride.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ride)
        
        # Prepare updated ride data
        ride_data = {
            "id": ride.id,
            "user_id": ride.user_id,
            "user_name": ride.user.name if ride.user else "Unknown",
            "driver_id": ride.driver_id,
            "driver_name": ride.driver.name if ride.driver else None,
            "pickup_location": ride.pickup_location,
            "destination_location": ride.destination_location,
            "status": ride.status,
            "estimated_fare": ride.estimated_fare,
            "actual_fare": ride.actual_fare,
            "updated_at": ride.updated_at.isoformat()
        }
        
        # Broadcast ride status update
        await broadcast_ride_update(ride_data, "ride_status_updated")
        
        # If driver status changed, broadcast driver update
        if driver:
            driver_data = {
                "driver_id": driver.driver_id,
                "name": driver.name,
                "status": driver.status,
                "updated_at": driver.updated_at.isoformat()
            }
            await broadcast_driver_update(driver_data, "driver_status_updated")
        
        return {
            "success": True,
            "message": f"Ride status updated from {old_status} to {status_update.status}",
            "ride": ride_data
=======
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
>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

<<<<<<< HEAD
@app.post("/api/rides/{ride_id}/end")
async def end_ride(ride_id: int, end_request: RideEndRequest, db: Session = Depends(get_db)):
    """End/finish a ride - can be called by user or driver"""
    try:
        ride = db.query(RideRequest).filter(RideRequest.id == ride_id).first()
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
        
        # Validate that ride can be ended
        if ride.status not in ["accepted", "in_progress"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot end ride with status '{ride.status}'. Only accepted or in-progress rides can be ended."
            )
        
        # Validate who can end the ride
        if end_request.ended_by not in ["user", "driver"]:
            raise HTTPException(status_code=400, detail="ended_by must be 'user' or 'driver'")
        
        # Additional validation based on who is ending the ride
        if end_request.ended_by == "driver" and not ride.driver_id:
            raise HTTPException(status_code=400, detail="No driver assigned to this ride")
        
        # Update ride status to completed
        old_status = ride.status
        ride.status = "completed"
        ride.completed_at = datetime.utcnow()
        
        # Set final fare if provided, otherwise use estimated fare
        if end_request.final_fare and end_request.final_fare > 0:
            ride.actual_fare = end_request.final_fare
        else:
            ride.actual_fare = ride.estimated_fare
        
        # Free up the driver
        driver = None
        if ride.driver_id:
            driver = db.query(Driver).filter(Driver.driver_id == ride.driver_id).first()
            if driver:
                driver.status = "online"
                driver.updated_at = datetime.utcnow()
        
        ride.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ride)
        
        # Prepare ride completion data
        ride_data = {
            "id": ride.id,
            "user_id": ride.user_id,
            "user_name": ride.user.name if ride.user else "Unknown",
            "driver_id": ride.driver_id,
            "driver_name": ride.driver.name if ride.driver else None,
            "pickup_location": ride.pickup_location,
            "destination_location": ride.destination_location,
            "status": ride.status,
            "estimated_fare": ride.estimated_fare,
            "actual_fare": ride.actual_fare,
            "ended_by": end_request.ended_by,
            "reason": end_request.reason,
            "completed_at": ride.completed_at.isoformat(),
            "updated_at": ride.updated_at.isoformat()
        }
        
        # Broadcast ride completion
        await broadcast_ride_update(ride_data, "ride_ended")
        
        # Broadcast driver status update if applicable
        if driver:
            driver_data = {
                "driver_id": driver.driver_id,
                "name": driver.name,
                "status": driver.status,
                "updated_at": driver.updated_at.isoformat()
            }
            await broadcast_driver_update(driver_data, "driver_status_updated")
        
        return {
            "success": True,
            "message": f"Ride ended by {end_request.ended_by}",
            "ride": ride_data,
            "final_fare": ride.actual_fare
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
        
        # Broadcast driver status update
        driver_data = {
            "driver_id": driver.driver_id,
            "name": driver.name,
            "status": driver.status,
            "updated_at": driver.updated_at.isoformat()
        }
        await broadcast_driver_update(driver_data, "driver_status_updated")
        
        return {
            "success": True,
            "message": f"Driver status updated to {status_update.status}",
            "driver_id": driver.driver_id,
            "status": driver.status
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Other endpoints (user rides, available rides, all rides, all drivers) remain the same...

=======
>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
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

<<<<<<< HEAD
=======
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

>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
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

<<<<<<< HEAD
=======
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

>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
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

<<<<<<< HEAD
=======
# ------------------------------
# UTILITY FUNCTIONS
# ------------------------------

>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
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
<<<<<<< HEAD
    uvicorn.run(app, host="0.0.0.0", port=8000)
=======
    uvicorn.run(app, host="0.0.0.0", port=8000)
>>>>>>> a5309df6750f879511ff530e42aa95c0b257064e
