# drivers.py - Driver management system
import random
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import math

router = APIRouter()

class Driver(BaseModel):
    id: int
    name: str
    rating: float
    vehicle: str
    lat: float
    lng: float
    status: str = "available"  # available, busy, offline
    phone: str = ""
    license_plate: str = ""

class LocationUpdate(BaseModel):
    driver_id: int
    lat: float
    lng: float

class MatchRequest(BaseModel):
    user_lat: float
    user_lng: float
    destination: str
    user_id: str

class MatchResult(BaseModel):
    driver: Driver
    distance: float
    eta: int
    price: float
    match_score: float

# In-memory driver storage (in production, use database)
drivers_db: Dict[int, Driver] = {}

# Initialize with some sample drivers
def initialize_drivers():
    sample_drivers = [
        {"id": 1, "name": "John Smith", "rating": 4.9, "vehicle": "Honda Civic", "lat": 28.6139, "lng": 77.2090, "phone": "+91-9876543210", "license_plate": "DL-01-AB-1234"},
        {"id": 2, "name": "Sarah Johnson", "rating": 4.8, "vehicle": "Toyota Camry", "lat": 28.6200, "lng": 77.2100, "phone": "+91-9876543211", "license_plate": "DL-02-CD-5678"},
        {"id": 3, "name": "Mike Wilson", "rating": 4.7, "vehicle": "Hyundai Elantra", "lat": 28.6100, "lng": 77.2050, "phone": "+91-9876543212", "license_plate": "DL-03-EF-9012"},
        {"id": 4, "name": "Emily Davis", "rating": 4.9, "vehicle": "Nissan Altima", "lat": 28.6180, "lng": 77.2120, "phone": "+91-9876543213", "license_plate": "DL-04-GH-3456"},
        {"id": 5, "name": "Alex Brown", "rating": 4.6, "vehicle": "Ford Focus", "lat": 28.6160, "lng": 77.2080, "phone": "+91-9876543214", "license_plate": "DL-05-IJ-7890"},
    ]
    
    for driver_data in sample_drivers:
        # Add some random offset to make locations more realistic
        driver_data["lat"] += (random.random() - 0.5) * 0.02
        driver_data["lng"] += (random.random() - 0.5) * 0.02
        driver = Driver(**driver_data)
        drivers_db[driver.id] = driver

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) * math.sin(dlng / 2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_match_score(driver: Driver, user_lat: float, user_lng: float) -> tuple:
    """Calculate match score based on distance, rating, and availability"""
    distance = calculate_distance(user_lat, user_lng, driver.lat, driver.lng)
    
    # Calculate ETA (assuming 30 km/h average speed in traffic)
    eta = max(1, round(distance / 0.5))  # 30km/h = 0.5km/min
    
    # Calculate price (base fare + distance)
    base_fare = 50  # Base fare in INR
    price_per_km = 12
    price = base_fare + (distance * price_per_km)
    
    # Scoring algorithm: 40% distance, 30% rating, 20% ETA, 10% price
    distance_score = max(0, 1 - (distance / 10))  # Closer is better
    rating_score = driver.rating / 5.0  # Normalize rating
    eta_score = max(0, 1 - (eta / 30))  # Faster is better
    price_score = max(0, 1 - (price / 500))  # Cheaper is better
    
    match_score = (distance_score * 0.4 + 
                  rating_score * 0.3 + 
                  eta_score * 0.2 + 
                  price_score * 0.1)
    
    return distance, eta, price, match_score

@router.get("/drivers/nearby")
async def get_nearby_drivers(lat: float, lng: float, radius: float = 5.0):
    """Get all nearby drivers within specified radius (km)"""
    if not drivers_db:
        initialize_drivers()
    
    nearby = []
    for driver in drivers_db.values():
        if driver.status != "available":
            continue
            
        distance = calculate_distance(lat, lng, driver.lat, driver.lng)
        if distance <= radius:
            distance_km, eta, price, match_score = calculate_match_score(driver, lat, lng)
            nearby.append({
                "driver": driver.dict(),
                "distance": round(distance_km, 2),
                "eta": eta,
                "price": round(price, 2),
                "match_score": round(match_score, 3)
            })
    
    # Sort by match score (best first)
    nearby.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "success": True,
        "count": len(nearby),
        "drivers": nearby
    }

@router.post("/drivers/match")
async def find_best_match(request: MatchRequest):
    """Find the best driver match for a ride request"""
    if not drivers_db:
        initialize_drivers()
    
    # Get nearby drivers
    nearby_response = await get_nearby_drivers(request.user_lat, request.user_lng)
    
    if not nearby_response["drivers"]:
        raise HTTPException(status_code=404, detail="No drivers available in your area")
    
    # Best match is the first one (highest score)
    best_match = nearby_response["drivers"][0]
    
    return {
        "success": True,
        "best_match": best_match,
        "all_drivers": nearby_response["drivers"][:5],  # Return top 5
        "message": f"Found perfect match: {best_match['driver']['name']} - {best_match['eta']} min away"
    }

@router.patch("/drivers/{driver_id}/location")
async def update_driver_location(driver_id: int, location: LocationUpdate):
    """Update driver's real-time location"""
    if driver_id not in drivers_db:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    drivers_db[driver_id].lat = location.lat
    drivers_db[driver_id].lng = location.lng
    
    return {
        "success": True,
        "message": f"Location updated for driver {driver_id}",
        "driver": drivers_db[driver_id].dict()
    }

@router.patch("/drivers/{driver_id}/status")
async def update_driver_status(driver_id: int, status: str):
    """Update driver's availability status"""
    if driver_id not in drivers_db:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    valid_statuses = ["available", "busy", "offline"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    drivers_db[driver_id].status = status
    
    return {
        "success": True,
        "message": f"Status updated to {status} for driver {driver_id}",
        "driver": drivers_db[driver_id].dict()
    }

# Initialize drivers when module loads
initialize_drivers()