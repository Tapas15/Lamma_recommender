#!/usr/bin/env python
"""
Test script to verify MongoDB connection functionality in setup.py
"""
import sys
import os

# Add the current directory to the path so we can import from setup.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mongodb_connection(mongodb_url, timeout_seconds=30):
    """Test MongoDB connection with specified timeout"""
    try:
        import pymongo
        print(f"Testing connection to: {mongodb_url}")
        print(f"Timeout: {timeout_seconds} seconds")
        
        client = pymongo.MongoClient(mongodb_url, serverSelectionTimeoutMS=timeout_seconds * 1000)
        # Test the connection
        client.server_info()
        
        # Test database access
        db_name = "connection_test"
        db = client[db_name]
        # Try to list collections (this will fail if no access)
        collections = db.list_collection_names()
        
        print("✓ MongoDB connection successful!")
        print(f"✓ Server is accessible")
        print(f"✓ Database access confirmed")
        return True, "Connection successful"
        
    except pymongo.errors.ServerSelectionTimeoutError:
        return False, f"Connection timeout after {timeout_seconds} seconds. Server may be unreachable."
    except pymongo.errors.ConfigurationError as e:
        return False, f"Configuration error: {str(e)}"
    except pymongo.errors.OperationFailure as e:
        return False, f"Authentication or permission error: {str(e)}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def main():
    """Test MongoDB connection functionality"""
    print("MongoDB Connection Test")
    print("=" * 50)
    
    # Test with default URL
    default_url = "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/"
    print(f"\nTesting default MongoDB URL...")
    success, message = test_mongodb_connection(default_url, 30)
    
    if success:
        print("✓ Default MongoDB connection works!")
    else:
        print(f"✗ Default MongoDB connection failed: {message}")
    
    # Allow user to test custom URL
    print("\nWould you like to test a custom MongoDB URL? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y':
        print("\nEnter your MongoDB URL:")
        print("Examples:")
        print("  - Local MongoDB: mongodb://localhost:27017")
        print("  - MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/")
        custom_url = input("MongoDB URL: ").strip()
        
        if custom_url:
            print(f"\nTesting custom MongoDB URL...")
            success, message = test_mongodb_connection(custom_url, 30)
            
            if success:
                print("✓ Custom MongoDB connection works!")
            else:
                print(f"✗ Custom MongoDB connection failed: {message}")
        else:
            print("No URL entered.")
    
    print("\nTest completed.")

if __name__ == "__main__":
    main() 