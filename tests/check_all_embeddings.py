#!/usr/bin/env python
"""
Check if vector embeddings are properly generated and stored in MongoDB.
This script:
1. Connects to MongoDB
2. Checks if collections have embedding fields
3. Verifies if vector indexes are set up
4. Tests embedding generation with Ollama

Usage:
    python check_all_embeddings.py
"""

import sys
import os
import time
import json
import pymongo
from bson import ObjectId
import numpy as np
from dotenv import load_dotenv
from tabulate import tabulate

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.embedding import get_embedding
from utils.database import Database

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGODB_URL", "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/")
DB_NAME = os.getenv("DATABASE_NAME", "job_recommender")

# Collections to check
COLLECTIONS = ["jobs", "projects", "candidates"]

def print_section(title):
    """Print a section title for better readability"""
    print("\n")
    print("=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def connect_to_mongodb():
    """Connect to MongoDB and return client and database"""
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        print(f"✅ Successfully connected to MongoDB: {DB_NAME}")
        return client, db
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {str(e)}")
        return None, None

def check_embedding_fields(db):
    """Check if collections have embedding fields"""
    print_section("CHECKING EMBEDDING FIELDS")
    
    results = []
    success_count = 0
    
    for collection_name in COLLECTIONS:
        collection = db[collection_name]
        
        # Get a sample document
        sample = collection.find_one({})
        if not sample:
            status = "⚠️ No Data"
            details = "Collection exists but has no documents"
            results.append([collection_name, status, details])
            continue
        
        # Check for embedding field
        has_embedding = False
        for doc in collection.find().limit(5):
            if "embedding" in doc:
                has_embedding = True
                vector = doc["embedding"]
                
                if isinstance(vector, list) and len(vector) > 0:
                    status = "✅ Found"
                    details = f"Has embedding vectors of dimension {len(vector)}"
                    success_count += 1
                else:
                    status = "⚠️ Invalid"
                    details = f"Embedding field exists but format is invalid: {type(vector)}"
                break
        
        if not has_embedding:
            status = "❌ Missing"
            details = "No embedding field found in documents"
        
        results.append([collection_name, status, details])
    
    print(tabulate(results, headers=["Collection", "Status", "Details"], tablefmt="grid"))
    
    # Print overall success rate
    success_rate = (success_count / len(COLLECTIONS)) * 100 if COLLECTIONS else 0
    print(f"\nOverall success rate: {success_rate:.1f}% ({success_count}/{len(COLLECTIONS)})")
    
    return success_count == len(COLLECTIONS)

def check_vector_indexes(db):
    """Check if vector indexes are set up in MongoDB"""
    print_section("CHECKING VECTOR INDEXES")
    
    results = []
    success_count = 0
    
    for collection_name in COLLECTIONS:
        collection = db[collection_name]
        
        # Get indexes
        indexes = collection.index_information()
        vector_indexes = [idx for idx in indexes if "vector" in idx.lower()]
        
        if vector_indexes:
            status = "✅ Found"
            details = f"Vector index: {', '.join(vector_indexes)}"
            success_count += 1
        else:
            status = "❌ Missing"
            details = "No vector index found"
        
        results.append([collection_name, status, details])
    
    print(tabulate(results, headers=["Collection", "Status", "Details"], tablefmt="grid"))
    
    # Print overall success rate
    success_rate = (success_count / len(COLLECTIONS)) * 100 if COLLECTIONS else 0
    print(f"\nOverall success rate: {success_rate:.1f}% ({success_count}/{len(COLLECTIONS)})")
    
    return success_count == len(COLLECTIONS)

def test_embedding_generation():
    """Test if embedding generation is working"""
    print_section("TESTING EMBEDDING GENERATION")
    
    test_texts = [
        "Senior software engineer with React and Node.js experience",
        "Data scientist with machine learning expertise",
        "Mobile app development project using React Native"
    ]
    
    results = []
    
    for i, text in enumerate(test_texts):
        start_time = time.time()
        embedding = get_embedding(text)
        end_time = time.time()
        
        if embedding and isinstance(embedding, list):
            status = "✅ Success"
            details = f"Dimensions: {len(embedding)}, Time: {end_time - start_time:.2f}s"
        else:
            status = "❌ Failed"
            details = f"Result: {embedding}"
        
        results.append([i+1, text[:40] + "...", status, details])
    
    print(tabulate(results, headers=["#", "Text", "Status", "Details"], tablefmt="grid"))
    
    # Return overall success
    return all("✅ Success" in row[2] for row in results)

def calculate_vector_stats(db):
    """Calculate statistics about embedding vectors"""
    print_section("EMBEDDING VECTOR STATISTICS")
    
    results = []
    
    for collection_name in COLLECTIONS:
        collection = db[collection_name]
        
        # Count total documents
        total_docs = collection.count_documents({})
        
        # Count documents with embeddings
        docs_with_embeddings = collection.count_documents({"embedding": {"$exists": True}})
        
        # Calculate coverage percentage
        if total_docs > 0:
            coverage = (docs_with_embeddings / total_docs) * 100
        else:
            coverage = 0
        
        # Get a sample embedding to check dimensionality
        sample = collection.find_one({"embedding": {"$exists": True}})
        if sample and "embedding" in sample:
            dimensions = len(sample["embedding"])
        else:
            dimensions = "N/A"
        
        results.append([
            collection_name, 
            total_docs, 
            docs_with_embeddings, 
            f"{coverage:.1f}%", 
            dimensions
        ])
    
    print(tabulate(results, 
                  headers=["Collection", "Total Docs", "With Embeddings", "Coverage", "Dimensions"], 
                  tablefmt="grid"))

def run_all_checks():
    """Run all embedding checks"""
    print_section("VECTOR EMBEDDINGS CHECK SUITE")
    print(f"MongoDB URI: {MONGO_URI}")
    print(f"Database: {DB_NAME}")
    
    # Connect to MongoDB
    client, db = connect_to_mongodb()
    # Check if client/db connection failed explicitly instead of truth value testing
    if client is None or db is None:
        return
    
    try:
        # Track test results
        results = {}
        
        # Check embedding fields
        results["embedding_fields"] = check_embedding_fields(db)
        
        # Check vector indexes
        results["vector_indexes"] = check_vector_indexes(db)
        
        # Test embedding generation
        results["embedding_generation"] = test_embedding_generation()
        
        # Calculate vector statistics
        calculate_vector_stats(db)
        
        # Print summary
        print_section("CHECK RESULTS SUMMARY")
        
        summary = []
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            summary.append([test_name.replace("_", " ").title(), status])
        
        print(tabulate(summary, headers=["Check", "Status"], tablefmt="grid"))
        
        # Overall assessment
        passed_count = sum(1 for passed in results.values() if passed)
        total_count = len(results)
        success_rate = (passed_count / total_count) * 100
        
        print(f"\nOverall success rate: {success_rate:.1f}% ({passed_count}/{total_count})")
        
        if success_rate == 100:
            print("\n✅ All checks passed! The vector embedding system appears to be working correctly.")
        elif success_rate >= 70:
            print("\n⚠️ Some checks passed, but there are issues that need attention.")
        else:
            print("\n❌ Multiple checks failed. The vector embedding system needs significant fixes.")
        
        # Provide recommendations based on failures
        if not results["embedding_fields"]:
            print("\nRecommendation: Create or update documents with embedding fields.")
            print("Run the embedding generation script to add embeddings to documents.")
        
        if not results["vector_indexes"]:
            print("\nRecommendation: Set up MongoDB Atlas vector indexes.")
            print("Run the create_vector_indexes.py script to create the required indexes.")
        
        if not results["embedding_generation"]:
            print("\nRecommendation: Check if Ollama is running and accessible.")
            print("The embedding generation is critical for all search and recommendation features.")
    finally:
        client.close()

if __name__ == "__main__":
    run_all_checks() 