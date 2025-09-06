from database import test_connection, create_tables

if __name__ == "__main__":
    print("Testing database connection...")
    if test_connection():
        print("✅ Connection successful!")
        print("Creating tables...")
        create_tables()
        print("✅ Tables created!")
    else:
        print("❌ Connection failed")