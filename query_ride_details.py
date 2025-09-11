#!/usr/bin/env python3
"""
    The script allows users to query ride details from a PostgreSQL database for a Mini Uber
    application.
"""
"""
Script to query ride details from PostgreSQL database
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from decouple import config
from datetime import datetime, timedelta

# Database connection
DATABASE_URL = config("DATABASE_URL", default="postgresql://username:password@localhost:5432/miniuber_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_all_ride_requests():
    """Get all ride requests"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, user_id, source_location, dest_location, status, 
                   created_at, updated_at 
            FROM ride_requests 
            ORDER BY created_at DESC
        """))
        
        print("\n=== RIDE REQUESTS ===")
        print(f"{'ID':<5} {'User ID':<15} {'Source':<25} {'Destination':<25} {'Status':<12} {'Created':<20}")
        print("-" * 120)
        
        for row in result:
            print(f"{row.id:<5} {row.user_id:<15} {row.source_location[:24]:<25} {row.dest_location[:24]:<25} {row.status:<12} {row.created_at.strftime('%Y-%m-%d %H:%M'):<20}")

def get_ride_history():
    """Get completed ride history"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, driver_id, rider_id, pickup_location, destination, 
                   distance, fare, ride_start_time, ride_end_time, status
            FROM ride_history 
            ORDER BY ride_end_time DESC
        """))
        
        print("\n=== RIDE HISTORY ===")
        print(f"{'ID':<5} {'Driver':<8} {'Rider':<12} {'Pickup':<20} {'Destination':<20} {'Fare':<8} {'Duration':<10} {'Status':<10}")
        print("-" * 120)
        
        for row in result:
            duration = row.ride_end_time - row.ride_start_time if row.ride_end_time and row.ride_start_time else None
            duration_str = f"{duration.total_seconds()/60:.0f}m" if duration else "N/A"
            
            print(f"{row.id:<5} {row.driver_id:<8} {row.rider_id:<12} {row.pickup_location[:19]:<20} {row.destination[:19]:<20} ₹{row.fare:<7} {duration_str:<10} {row.status:<10}")

def get_driver_locations():
    """Get recent driver locations"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT driver_id, lat, lng, timestamp, is_active
            FROM driver_locations 
            WHERE timestamp > NOW() - INTERVAL '1 day'
            ORDER BY timestamp DESC
            LIMIT 20
        """))
        
        print("\n=== RECENT DRIVER LOCATIONS ===")
        print(f"{'Driver ID':<10} {'Latitude':<12} {'Longitude':<12} {'Timestamp':<20} {'Active':<8}")
        print("-" * 70)
        
        for row in result:
            print(f"{row.driver_id:<10} {row.lat:<12.6f} {row.lng:<12.6f} {row.timestamp.strftime('%Y-%m-%d %H:%M'):<20} {'Yes' if row.is_active else 'No':<8}")

def get_ride_statistics():
    """Get ride statistics"""
    with engine.connect() as conn:
        # Total rides
        total_requests = conn.execute(text("SELECT COUNT(*) FROM ride_requests")).scalar()
        completed_rides = conn.execute(text("SELECT COUNT(*) FROM ride_history")).scalar()
        
        # Today's statistics
        today_requests = conn.execute(text("""
            SELECT COUNT(*) FROM ride_requests 
            WHERE DATE(created_at) = CURRENT_DATE
        """)).scalar()
        
        today_revenue = conn.execute(text("""
            SELECT COALESCE(SUM(fare), 0) FROM ride_history 
            WHERE DATE(ride_end_time) = CURRENT_DATE
        """)).scalar()
        
        # Status breakdown
        status_breakdown = conn.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM ride_requests 
            GROUP BY status 
            ORDER BY count DESC
        """)).fetchall()
        
        print("\n=== RIDE STATISTICS ===")
        print(f"Total Ride Requests: {total_requests}")
        print(f"Completed Rides: {completed_rides}")
        print(f"Today's Requests: {today_requests}")
        print(f"Today's Revenue: ₹{today_revenue}")
        
        print("\nStatus Breakdown:")
        for status, count in status_breakdown:
            print(f"  {status.title()}: {count}")

def search_rides_by_user(user_id):
    """Search rides for a specific user"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT r.id, r.source_location, r.dest_location, r.status, r.created_at,
                   h.driver_id, h.fare, h.ride_start_time, h.ride_end_time
            FROM ride_requests r
            LEFT JOIN ride_history h ON r.user_id = h.rider_id
            WHERE r.user_id = :user_id
            ORDER BY r.created_at DESC
        """), {"user_id": user_id})
        
        print(f"\n=== RIDES FOR USER: {user_id} ===")
        print(f"{'Req ID':<8} {'Source':<20} {'Destination':<20} {'Status':<12} {'Fare':<8} {'Created':<20}")
        print("-" * 100)
        
        for row in result:
            fare_str = f"₹{row.fare}" if row.fare else "N/A"
            print(f"{row.id:<8} {row.source_location[:19]:<20} {row.dest_location[:19]:<20} {row.status:<12} {fare_str:<8} {row.created_at.strftime('%Y-%m-%d %H:%M'):<20}")

def search_rides_by_driver(driver_id):
    """Search rides for a specific driver"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT h.id, h.rider_id, h.pickup_location, h.destination, 
                   h.fare, h.ride_start_time, h.ride_end_time, h.status
            FROM ride_history h
            WHERE h.driver_id = :driver_id
            ORDER BY h.ride_end_time DESC
        """), {"driver_id": driver_id})
        
        print(f"\n=== RIDES FOR DRIVER: {driver_id} ===")
        print(f"{'ID':<5} {'Rider':<12} {'Pickup':<20} {'Destination':<20} {'Fare':<8} {'Date':<12}")
        print("-" * 85)
        
        total_earnings = 0
        for row in result:
            total_earnings += row.fare
            date_str = row.ride_end_time.strftime('%Y-%m-%d') if row.ride_end_time else "N/A"
            print(f"{row.id:<5} {row.rider_id:<12} {row.pickup_location[:19]:<20} {row.destination[:19]:<20} ₹{row.fare:<7} {date_str:<12}")
        
        print(f"\nTotal Earnings: ₹{total_earnings}")

def main():
    """Main function with interactive menu"""
    while True:
        print("\n" + "="*60)
        print("MINI UBER - DATABASE QUERY TOOL")
        print("="*60)
        print("1. View All Ride Requests")
        print("2. View Ride History")
        print("3. View Driver Locations")
        print("4. View Statistics")
        print("5. Search by User ID")
        print("6. Search by Driver ID")
        print("7. Exit")
        print("-"*60)
        
        choice = input("Enter your choice (1-7): ").strip()
        
        try:
            if choice == '1':
                get_all_ride_requests()
            elif choice == '2':
                get_ride_history()
            elif choice == '3':
                get_driver_locations()
            elif choice == '4':
                get_ride_statistics()
            elif choice == '5':
                user_id = input("Enter User ID: ").strip()
                search_rides_by_user(user_id)
            elif choice == '6':
                driver_id = int(input("Enter Driver ID: ").strip())
                search_rides_by_driver(driver_id)
            elif choice == '7':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
                
        except Exception as e:
            print(f"Error: {e}")
            
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        # Test database connection first
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        main()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. Database exists")
        print("3. Credentials in .env are correct")
        print("4. DATABASE_URL is set properly")