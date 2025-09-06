from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime
from typing import List, Optional

from database import get_db, create_tables, test_connection, RideRequest

app = FastAPI(title="Mini Uber API", version="1.0.0")

# Initialize database
create_tables()
db_available = test_connection()

# Pydantic models
class PingRequest(BaseModel):
    data: str

class PongResponse(BaseModel):
    message: str
    status: str

class RideRequestCreate(BaseModel):
    user_id: str
    source_location: str
    dest_location: str

class RideRequestResponse(BaseModel):
    id: int
    user_id: str
    source_location: str
    dest_location: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RideRequestStatusUpdate(BaseModel):
    status: str

@app.get("/")
async def root():
    return {"message": "Welcome to Mini Uber API"}

@app.post("/ping", response_model=PongResponse)
async def ping_pong(request: PingRequest):
    if request.data == "ping":
        return PongResponse(message="pong", status="success")
    raise HTTPException(status_code=400, detail="Invalid ping data")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if db_available else "disconnected"
    }

@app.post("/api/ride-request", response_model=dict)
async def submit_ride_request(
    ride_request: RideRequestCreate, 
    db: Session = Depends(get_db)
):
    try:
        # Validation
        if not ride_request.user_id or not ride_request.source_location or not ride_request.dest_location:
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: user_id, source_location, dest_location"
            )
        
        if db_available:
            # Try to save to PostgreSQL
            try:
                db_ride_request = RideRequest(
                    user_id=ride_request.user_id,
                    source_location=ride_request.source_location,
                    dest_location=ride_request.dest_location
                )
                
                db.add(db_ride_request)
                db.commit()
                db.refresh(db_ride_request)
                
                # Log successful save
                print("Ride request stored in PostgreSQL:")
                print(f"ID: {db_ride_request.id}")
                print(f"User ID: {db_ride_request.user_id}")
                print(f"Source: {db_ride_request.source_location}")
                print(f"Destination: {db_ride_request.dest_location}")
                print(f"Status: {db_ride_request.status}")
                print(f"Created At: {db_ride_request.created_at}")
                
                return {
                    "success": True,
                    "message": "Ride request submitted successfully",
                    "data": {
                        "id": db_ride_request.id,
                        "user_id": db_ride_request.user_id,
                        "source_location": db_ride_request.source_location,
                        "dest_location": db_ride_request.dest_location,
                        "status": db_ride_request.status,
                        "created_at": db_ride_request.created_at.isoformat(),
                        "updated_at": db_ride_request.updated_at.isoformat()
                    }
                }
            
            except Exception as db_error:
                print(f"Database save failed: {str(db_error)}")
                # Fallback
                print("We will store this data in Postgres now")
                print(f"User ID: {ride_request.user_id}")
                print(f"Source Location: {ride_request.source_location}")
                print(f"Destination Location: {ride_request.dest_location}")
                print(f"Timestamp: {datetime.now()}")
                
                return {
                    "success": True,
                    "message": "Ride request received (Database unavailable)",
                    "data": {
                        "user_id": ride_request.user_id,
                        "source_location": ride_request.source_location,
                        "dest_location": ride_request.dest_location,
                        "status": "pending",
                        "created_at": datetime.now().isoformat()
                    }
                }
        else:
            # Database not available - use fallback
            print("We will store this data in Postgres now")
            print(f"User ID: {ride_request.user_id}")
            print(f"Source Location: {ride_request.source_location}")
            print(f"Destination Location: {ride_request.dest_location}")
            print(f"Timestamp: {datetime.now()}")
            
            return {
                "success": True,
                "message": "Ride request received (Database unavailable)",
                "data": {
                    "user_id": ride_request.user_id,
                    "source_location": ride_request.source_location,
                    "dest_location": ride_request.dest_location,
                    "status": "pending",
                    "created_at": datetime.now().isoformat()
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing ride request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process ride request")

@app.get("/api/ride-requests")
async def list_ride_requests(db: Session = Depends(get_db)):
    try:
        if not db_available:
            raise HTTPException(
                status_code=503, 
                detail="Database unavailable"
            )
        
        requests = db.query(RideRequest).order_by(RideRequest.created_at.desc()).all()
        return {
            "success": True,
            "count": len(requests),
            "data": [
                {
                    "id": req.id,
                    "user_id": req.user_id,
                    "source_location": req.source_location,
                    "dest_location": req.dest_location,
                    "status": req.status,
                    "created_at": req.created_at.isoformat(),
                    "updated_at": req.updated_at.isoformat()
                } for req in requests
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching ride requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch ride requests")

@app.get("/api/ride-requests/{request_id}")
async def get_ride_request(request_id: int, db: Session = Depends(get_db)):
    try:
        if not db_available:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        ride_request = db.query(RideRequest).filter(RideRequest.id == request_id).first()
        
        if not ride_request:
            raise HTTPException(status_code=404, detail="Ride request not found")
        
        return {
            "success": True,
            "data": {
                "id": ride_request.id,
                "user_id": ride_request.user_id,
                "source_location": ride_request.source_location,
                "dest_location": ride_request.dest_location,
                "status": ride_request.status,
                "created_at": ride_request.created_at.isoformat(),
                "updated_at": ride_request.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching ride request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch ride request")

@app.patch("/api/ride-requests/{request_id}")
async def update_ride_request(
    request_id: int, 
    update_data: RideRequestStatusUpdate, 
    db: Session = Depends(get_db)
):
    try:
        if not db_available:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        ride_request = db.query(RideRequest).filter(RideRequest.id == request_id).first()
        
        if not ride_request:
            raise HTTPException(status_code=404, detail="Ride request not found")
        
        # Valid statuses
        valid_statuses = ["pending", "accepted", "in_progress", "completed", "cancelled"]
        if update_data.status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        ride_request.status = update_data.status
        db.commit()
        db.refresh(ride_request)
        
        return {
            "success": True,
            "message": "Ride request updated successfully",
            "data": {
                "id": ride_request.id,
                "user_id": ride_request.user_id,
                "source_location": ride_request.source_location,
                "dest_location": ride_request.dest_location,
                "status": ride_request.status,
                "created_at": ride_request.created_at.isoformat(),
                "updated_at": ride_request.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating ride request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update ride request")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

    
from drivers import router as drivers_router
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drivers_router, prefix="/api", tags=["drivers"])    
