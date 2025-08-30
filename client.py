import requests
import json

class MiniUberClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def ping_server(self):
        """Send ping to server and expect pong response"""
        url = f"{self.base_url}/ping"
        
        # BUG: Hardcoded data instead of using "ping" as specified
        payload = {"data": "hello"}  # Should be "ping"
        
        try:
            response = self.session.post(url, json=payload)
            
            # BUG: Not checking response status code before accessing JSON
            # This will fail if server returns an error
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def check_health(self):
        """Check server health"""
        url = f"{self.base_url}/health"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            return None

def main():
    client = MiniUberClient()
    
    # Test health endpoint
    print("Checking server health...")
    health = client.check_health()
    print(f"Health: {health}")
    
    # Test ping endpoint
    print("\nSending ping to server...")
    result = client.ping_server()
    print(f"Response: {result}")

if __name__ == "__main__":
    main()