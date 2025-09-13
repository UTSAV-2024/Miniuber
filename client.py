import requests
import json
import sys

class MiniUberClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def ping_server(self):
        """Send ping to server and expect pong response"""
        url = f"{self.base_url}/ping"
        payload = {"data": "ping"}  # Fixed: Now uses correct "ping" value
        
        try:
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Ping successful: {result}")
                return result
            else:
                error_detail = response.json() if response.content else {"detail": "Unknown error"}
                print(f"❌ Ping failed: {response.status_code} - {error_detail}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def submit_ride_request(self, source_location: str, dest_location: str, user_id: str):
        """Submit a ride request"""
        url = f"{self.base_url}/api/ride-request"
        payload = {
            "user_id": user_id,
            "source_location": source_location,
            "dest_location": dest_location
        }
        
        print(f"🚗 Submitting ride request: {payload}")
        
        try:
            response = self.session.post(url, json=payload)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Ride request submitted successfully!")
                print(f"Response: {json.dumps(result, indent=2)}")
                return result
            else:
                error_detail = response.json() if response.content else {"detail": "Unknown error"}
                print(f"❌ Ride request failed: {response.status_code} - {error_detail}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_all_ride_requests(self):
        """Get all ride requests"""
        url = f"{self.base_url}/api/ride-requests"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                result = response.json()
                print(f"📋 Retrieved {result.get('count', 0)} ride requests")
                print(f"Response: {json.dumps(result, indent=2)}")
                return result
            else:
                error_detail = response.json() if response.content else {"detail": "Unknown error"}
                print(f"❌ Failed to get requests: {response.status_code} - {error_detail}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_ride_request(self, request_id: int):
        """Get specific ride request"""
        url = f"{self.base_url}/api/ride-requests/{request_id}"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                result = response.json()
                print(f"🔍 Retrieved ride request {request_id}")
                print(f"Response: {json.dumps(result, indent=2)}")
                return result
            else:
                error_detail = response.json() if response.content else {"detail": "Unknown error"}
                print(f"❌ Failed to get request: {response.status_code} - {error_detail}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def update_ride_request_status(self, request_id: int, status: str):
        """Update ride request status"""
        url = f"{self.base_url}/api/ride-requests/{request_id}"
        payload = {"status": status}
        
        try:
            response = self.session.patch(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Updated ride request {request_id} to status: {status}")
                print(f"Response: {json.dumps(result, indent=2)}")
                return result
            else:
                error_detail = response.json() if response.content else {"detail": "Unknown error"}
                print(f"❌ Update failed: {response.status_code} - {error_detail}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def check_health(self):
        """Check server health"""
        url = f"{self.base_url}/health"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                result = response.json()
                print(f"💚 Health check successful: {result}")
                return result
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Health check failed: {e}")
            return None

def main():
    client = MiniUberClient()
    
    if len(sys.argv) < 2:
        print("🚀 Mini Uber Client Usage:")
        print("python client.py ping")
        print("python client.py health")
        print("python client.py submit <source> <destination> <user_id>")
        print("python client.py list")
        print("python client.py get <id>")
        print("python client.py update <id> <status>")
        return
    
    command = sys.argv[1]
    
    if command == "ping":
        client.ping_server()
    elif command == "health":
        client.check_health()
    elif command == "submit":
        if len(sys.argv) != 5:
            print("Usage: python client.py submit <source> <destination> <user_id>")
            return
        client.submit_ride_request(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == "list":
        client.get_all_ride_requests()
    elif command == "get":
        if len(sys.argv) != 3:
            print("Usage: python client.py get <id>")
            return
        client.get_ride_request(int(sys.argv[2]))
    elif command == "update":
        if len(sys.argv) != 4:
            print("Usage: python client.py update <id> <status>")
            return
        client.update_ride_request_status(int(sys.argv[2]), sys.argv[3])
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
