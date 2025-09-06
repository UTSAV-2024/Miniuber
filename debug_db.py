from decouple import config
import os

print("=== Debugging Database URL ===")
print("Current working directory:", os.getcwd())
print("Files in directory:", os.listdir('.'))

# Check if .env exists
if os.path.exists('.env'):
    print("✅ .env file found")
    with open('.env', 'r') as f:
        print("Contents of .env:")
        print(f.read())
else:
    print("❌ .env file NOT found")

# See what config is reading
database_url = config("DATABASE_URL", default="sqlite:///./ride_requests.db")
print(f"DATABASE_URL being used: {database_url}")