#!/usr/bin/env python
"""
Vector Index Creation Utility

This script creates vector indexes in MongoDB Atlas for all collections
in the job recommender system. It's designed to automate the process of
setting up vector search capabilities.

Usage:
    python create_vector_indexes.py [--collection COLLECTION]

Examples:
    # Create vector indexes for all collections
    python create_vector_indexes.py
    
    # Create vector index for a specific collection
    python create_vector_indexes.py --collection candidates
"""

import pymongo
import argparse
import json
import time
import sys

# MongoDB connection details
MONGODB_URL = "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/"
DATABASE_NAME = "job_recommender"
COLLECTIONS = ["candidates", "jobs", "projects"]

# Vector index configuration
VECTOR_INDEX_CONFIG = {
    "fields": [
        {
            "numDimensions": 3072,
            "path": "embedding",
                    "similarity": "cosine",
                    "type": "vector"
                  }
    ]
}

def print_section(title):
    """Print a section title for better readability"""
    print("\n")
    print("=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def create_vector_index(collection_name):
    """Create a vector index for a specific collection"""
    client = pymongo.MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    collection = db[collection_name]
    
    print_section(f"CREATING VECTOR INDEX FOR {collection_name.upper()}")
    
    # Check if the collection exists and has documents
    doc_count = collection.count_documents({})
    if doc_count == 0:
        print(f"❌ Collection '{collection_name}' is empty. Skipping index creation.")
        return False
    
    # Check if documents have embeddings
    with_embedding_count = collection.count_documents({"embedding": {"$exists": True}})
    if with_embedding_count == 0:
        print(f"❌ No documents in '{collection_name}' have embeddings. Skipping index creation.")
        return False
    
    print(f"Found {with_embedding_count} documents with embeddings in '{collection_name}'")
    
    # Check if index already exists
    index_name = f"{collection_name}_vector_index"
    indexes = list(collection.list_indexes())
    
    for idx in indexes:
        if idx.get("name") == index_name:
            print(f"⚠️ Vector index '{index_name}' already exists. Skipping creation.")
            return True
    
    # Create the vector index using the command interface
    # Note: This requires MongoDB Atlas with vector search capability
    try:
        # Method 1: Using createSearchIndex command (MongoDB Atlas 6.0+)
        print(f"Creating vector index '{index_name}' using createSearchIndex command...")
        
        command = {
            "createSearchIndex": collection_name,
            "name": index_name,
            "definition": VECTOR_INDEX_CONFIG
        }
        
        result = db.command(command)
        
        if result.get("ok") == 1:
            print(f"✅ Successfully initiated vector index creation for '{collection_name}'")
            print("   Note: Index creation runs asynchronously and may take a few minutes to complete")
            return True
        else:
            print(f"❌ Failed to create vector index: {result}")
            return False
            
        except Exception as e:
        print(f"❌ Error creating vector index: {str(e)}")
        
        # Method 2: Using create_index (may not work for vector indexes in all MongoDB versions)
        try:
            print("Trying alternative method using create_index...")
            
            # This is a simplified approach and may not work for vector indexes in MongoDB Atlas
            # It's included as a fallback option
            collection.create_index(
                [("embedding", pymongo.TEXT)],
                name=index_name,
                weights={"embedding": 1}
            )
            
            print("⚠️ Created a text index instead of a vector index")
            print("   This will not enable vector search functionality")
            print("   Please create a vector index manually in the MongoDB Atlas UI")
            
            return False
        except Exception as e2:
            print(f"❌ Alternative method also failed: {str(e2)}")
            return False
    finally:
        client.close()

def check_index_status(collection_name):
    """Check if the vector index is ready"""
    client = pymongo.MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Use the listSearchIndexes command to check index status
        command = {
            "listSearchIndexes": collection_name
        }
        
        result = db.command(command)
        
        if "indexes" in result:
            index_name = f"{collection_name}_vector_index"
            for index in result["indexes"]:
                if index.get("name") == index_name:
                    status = index.get("status", "unknown")
                    print(f"Index '{index_name}' status: {status}")
                    return status == "ready"
        
        return False
    except Exception as e:
        print(f"❌ Error checking index status: {str(e)}")
        return False
    finally:
        client.close()

def wait_for_index_ready(collection_name, timeout_seconds=300):
    """Wait for the vector index to become ready"""
    print(f"Waiting for vector index to become ready (timeout: {timeout_seconds} seconds)...")
    
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        if check_index_status(collection_name):
            print(f"✅ Vector index for '{collection_name}' is now ready")
            return True
        
        # Wait before checking again
        time.sleep(10)
        elapsed = time.time() - start_time
        print(f"Still waiting... ({int(elapsed)}s elapsed)")
    
    print(f"⚠️ Timeout reached. Index may still be building in the background.")
    return False

def create_all_vector_indexes(collection_name=None):
    """Create vector indexes for all collections or a specific one"""
    print_section("VECTOR INDEX CREATION UTILITY")
    print("This utility creates vector indexes in MongoDB Atlas for the job recommender system")
    
    collections_to_process = [collection_name] if collection_name else COLLECTIONS
    
    for coll in collections_to_process:
        if coll not in COLLECTIONS:
            print(f"❌ Unknown collection: {coll}")
            continue
            
        success = create_vector_index(coll)
        
        if success:
            print(f"Vector index creation initiated for '{coll}'")
            
            # Optionally wait for the index to be ready
            # Uncomment the next line if you want to wait for each index
            # wait_for_index_ready(coll)
    
    print_section("MANUAL VERIFICATION")
    print("To verify that indexes were created successfully:")
    print("1. Go to MongoDB Atlas")
    print("2. Navigate to your cluster")
    print("3. Go to the Search tab")
    print("4. Check that your indexes are listed and have status 'Active'")
    
    print("\nNote: Vector index creation is asynchronous and may take several minutes to complete")
    print("      You can run the check_all_embeddings.py script to verify the indexes")

def main():
    parser = argparse.ArgumentParser(description="Create vector indexes in MongoDB Atlas")
    parser.add_argument("--collection", type=str, choices=COLLECTIONS,
                        help="Create index only for this collection (default: all collections)")
    
    args = parser.parse_args()
    create_all_vector_indexes(args.collection)

if __name__ == "__main__":
    main() 