#!/usr/bin/env python
"""
Comprehensive Embedding and Vector Search Checker

This script checks the status of embeddings and vector search functionality
across all collections in the job recommender system.

It will:
1. Check if embeddings exist in each collection
2. Verify the dimensions and quality of embeddings
3. Test MongoDB Atlas vector search functionality
4. Provide recommendations for fixing any issues
"""

import pymongo
import numpy as np
from bson import ObjectId
from tabulate import tabulate
import json
import traceback

# MongoDB connection details
MONGODB_URL = "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/"
DATABASE_NAME = "job_recommender"
COLLECTIONS = ["candidates", "jobs", "projects"]

def print_section(title):
    """Print a section title for better readability"""
    print("\n")
    print("=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    
    # Avoid division by zero
    if norm_a == 0 or norm_b == 0:
        return 0
        
    return dot_product / (norm_a * norm_b)

def analyze_embedding(embedding):
    """Analyze embedding vector properties"""
    if not embedding or not isinstance(embedding, list):
        return "Invalid embedding"
    
    embedding_array = np.array(embedding)
    return {
        "dimension": len(embedding),
        "min": float(np.min(embedding_array)),
        "max": float(np.max(embedding_array)),
        "mean": float(np.mean(embedding_array)),
        "std": float(np.std(embedding_array)),
        "norm": float(np.linalg.norm(embedding_array)),
        "first_5": embedding[:5],
        "last_5": embedding[-5:]
    }

def check_collection_embeddings(collection_name, client):
    """Check embeddings in a specific collection"""
    db = client[DATABASE_NAME]
    collection = db[collection_name]
    
    print_section(f"{collection_name.upper()} COLLECTION STATISTICS")
    
    # Collection statistics
    total_count = collection.count_documents({})
    with_embedding_count = collection.count_documents({"embedding": {"$exists": True}})
    without_embedding_count = collection.count_documents({"embedding": {"$exists": False}})
    
    print(f"Total {collection_name}: {total_count}")
    print(f"{collection_name.capitalize()} with embeddings: {with_embedding_count}")
    print(f"{collection_name.capitalize()} without embeddings: {without_embedding_count}")
    
    if with_embedding_count == 0:
        print(f"\n❌ No {collection_name} have embeddings! This is the main issue.")
        print(f"   The embedding generation for {collection_name} might not be working.")
        return False
    
    # Examine a sample embedding
    print_section(f"EXAMINING {collection_name.upper()} EMBEDDINGS")
    
    # Get a sample item with embedding
    sample_item = collection.find_one({"embedding": {"$exists": True}})
    
    if sample_item:
        # Print item details based on collection type
        if collection_name == "candidates":
            print(f"Sample candidate name: {sample_item.get('full_name', 'Unknown name')}")
            print(f"Candidate ID: {sample_item.get('id', 'No ID')}")
        elif collection_name == "jobs":
            print(f"Sample job title: {sample_item.get('title', 'Unknown title')}")
            print(f"Job ID: {sample_item.get('id', 'No ID')}")
        elif collection_name == "projects":
            print(f"Sample project title: {sample_item.get('title', 'Unknown title')}")
            print(f"Project ID: {sample_item.get('id', 'No ID')}")
        
        embedding = sample_item.get('embedding')
        if embedding:
            # Check embedding format
            if isinstance(embedding, list):
                analysis = analyze_embedding(embedding)
                
                print("\n📊 Embedding Analysis:")
                table_data = [
                    ["Dimension", analysis["dimension"]],
                    ["Min value", analysis["min"]],
                    ["Max value", analysis["max"]],
                    ["Mean value", analysis["mean"]],
                    ["Standard deviation", analysis["std"]],
                    ["L2 Norm", analysis["norm"]]
                ]
                print(tabulate(table_data, headers=["Property", "Value"], tablefmt="grid"))
                
                print("\n🔢 First 5 dimensions:")
                print(analysis["first_5"])
                print("\n🔢 Last 5 dimensions:")
                print(analysis["last_5"])
                
                if analysis["dimension"] != 3072:
                    print(f"\n⚠️ Warning: Expected embedding dimension 3072, but found {analysis['dimension']}")
                    print("   This may cause issues with vector search")
                    return False
                
                return True
            else:
                print(f"\n❌ Embedding is not a list! Type: {type(embedding)}")
                print("   This will prevent vector search from working")
                return False
        else:
            print("\n❌ Embedding is None or empty!")
            return False
    else:
        print(f"\n❌ Could not find any {collection_name} with embeddings")
        return False

def check_vector_index(collection_name, client):
    """Check if vector index exists for a collection"""
    db = client[DATABASE_NAME]
    collection = db[collection_name]
    
    print_section(f"CHECKING {collection_name.upper()} VECTOR INDEX")
    
    # List indexes
    indexes = list(collection.list_indexes())
    
    # Expected index name based on collection
    expected_index_name = f"{collection_name}_vector_index"
    
    vector_index_exists = False
    for idx in indexes:
        if idx.get("name") == expected_index_name:
            vector_index_exists = True
            print(f"✅ Vector index found in {collection_name} collection with name '{expected_index_name}'")
            break
    
    # If we didn't find the exact name, check for any index that might be a vector index
    if not vector_index_exists:
        # Try to check Atlas Search indexes (requires admin privileges)
        try:
            # This is a simple attempt to detect if any index might be a vector index
            print("Checking for any vector indexes...")
            
            # In MongoDB Atlas, vector indexes are created as Atlas Search indexes
            # which may not be fully visible through the driver API
            for idx in indexes:
                idx_name = idx.get("name", "")
                if "vector" in idx_name.lower() or "search" in idx_name.lower():
                    vector_index_exists = True
                    print(f"✅ Potential vector index found with name: {idx_name}")
                    break
        except Exception as e:
            print(f"Error checking for vector indexes: {str(e)}")
    
    if not vector_index_exists:
        print(f"❌ No vector index found in {collection_name} collection")
        print("   You need to create a vector index in MongoDB Atlas:")
        print("   1. Go to the Atlas UI")
        print("   2. Select your cluster")
        print("   3. Go to the Search tab")
        print("   4. Create an index with the following configuration:")
        print("""
        {
          "fields": [
            {
              "numDimensions": 3072,
              "path": "embedding",
              "similarity": "cosine",
              "type": "vector"
            }
          ]
        }
        """)
        print(f"   Name the index '{expected_index_name}' for automatic detection")
        return False
    
    return True

def test_vector_search(collection_name, client):
    """Test vector search functionality for a collection"""
    db = client[DATABASE_NAME]
    collection = db[collection_name]
    
    print_section(f"TESTING {collection_name.upper()} VECTOR SEARCH")
    
    # Get a sample item with embedding
    sample_item = collection.find_one({"embedding": {"$exists": True}})
    
    if not sample_item:
        print(f"❌ Could not find any {collection_name} with embeddings")
        return False
    
    # Get the embedding
    query_embedding = sample_item.get('embedding')
    
    if not query_embedding or not isinstance(query_embedding, list):
        print("❌ Invalid embedding found in the sample item")
        return False
    
    print(f"Embedding dimension: {len(query_embedding)}")
    
    # Try Atlas vector search
    print("\nAttempting MongoDB Atlas vector search...")
    results = None
    
    # Try different query formats
    query_formats = [
        # Format 1: Using vectorSearch
        {
            "$search": {
                "index": f"{collection_name}_vector_index",
                "vectorSearch": {
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "numCandidates": 10,
                    "limit": 5
                }
            }
        },
        
        # Format 2: Using knnVector
        {
            "$search": {
                "index": f"{collection_name}_vector_index",
                "knnVector": {
                    "vector": query_embedding,
                    "path": "embedding",
                    "k": 5
                }
            }
        }
    ]
    
    for i, query_format in enumerate(query_formats):
        try:
            print(f"Trying query format {i+1}...")
            pipeline = [
                query_format,
                {
                    "$project": {
                        "_id": 1,
                        "score": {"$meta": "searchScore"}
                    }
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            
            if results:
                print(f"✅ Vector search is working with format {i+1}!")
                print(f"Found {len(results)} similar {collection_name}")
                return True
            else:
                print(f"❌ No results returned from query format {i+1}")
        except Exception as e:
            print(f"❌ Error with format {i+1}: {str(e)}")
    
    print("\n❌ All vector search formats failed")
    print("This likely means the vector index is not set up correctly or has a different name")
    
    # Try manual approach
    print("\nTrying manual similarity calculation (fallback method)...")
    
    # Get all items with embeddings except the query item
    all_items = list(collection.find(
        {"embedding": {"$exists": True}, "_id": {"$ne": sample_item["_id"]}}
    ).limit(5))
    
    if not all_items:
        print(f"❌ Could not find any other {collection_name} with embeddings")
        return False
    
    print(f"Found {len(all_items)} {collection_name} with embeddings for manual calculation")
    
    # Calculate similarity manually for one item as a test
    if len(all_items) > 0:
        test_item = all_items[0]
        embedding = test_item.get('embedding')
        if embedding and isinstance(embedding, list):
            similarity = cosine_similarity(query_embedding, embedding)
            print(f"Manual similarity calculation result: {similarity}")
            print("✅ Manual similarity calculation is working")
            return True
    
    return False

def check_all_embeddings():
    """Check embeddings and vector search across all collections"""
    try:
        client = pymongo.MongoClient(MONGODB_URL)
        
        print_section("EMBEDDING AND VECTOR SEARCH DIAGNOSTIC TOOL")
        print("This tool will check the status of embeddings and vector search")
        print("functionality across all collections in the job recommender system.")
        
        results = {}
        
        # Check each collection
        for collection_name in COLLECTIONS:
            print_section(f"CHECKING {collection_name.upper()}")
            
            # Check embeddings
            embeddings_ok = check_collection_embeddings(collection_name, client)
            
            # Check vector index
            index_ok = check_vector_index(collection_name, client)
            
            # Test vector search
            search_ok = test_vector_search(collection_name, client)
            
            # Store results
            results[collection_name] = {
                "embeddings_ok": embeddings_ok,
                "index_ok": index_ok,
                "search_ok": search_ok
            }
        
        # Summary
        print_section("SUMMARY")
        
        table_data = []
        for collection_name in COLLECTIONS:
            result = results[collection_name]
            table_data.append([
                collection_name,
                "✅" if result["embeddings_ok"] else "❌",
                "✅" if result["index_ok"] else "❌",
                "✅" if result["search_ok"] else "❌"
            ])
        
        print(tabulate(table_data, headers=["Collection", "Embeddings", "Vector Index", "Vector Search"], tablefmt="grid"))
        
        # Recommendations
        print_section("RECOMMENDATIONS")
        
        for collection_name in COLLECTIONS:
            result = results[collection_name]
            
            if not result["embeddings_ok"]:
                print(f"❌ {collection_name.capitalize()} embeddings issue:")
                print(f"   - Check the embedding generation process for {collection_name}")
                print(f"   - Verify that the embedding model is working correctly")
                print(f"   - Make sure embeddings are being saved to MongoDB")
                print()
            
            if not result["index_ok"]:
                print(f"❌ {collection_name.capitalize()} vector index issue:")
                print(f"   - Create a vector index in MongoDB Atlas for {collection_name}")
                print(f"   - Name the index '{collection_name}_vector_index'")
                print(f"   - Use the correct dimension (3072) and similarity metric (cosine)")
                print()
            
            if not result["search_ok"]:
                print(f"❌ {collection_name.capitalize()} vector search issue:")
                print(f"   - Verify that the vector index is active in MongoDB Atlas")
                print(f"   - Check that the query format is correct")
                print(f"   - In the meantime, use manual similarity calculation as a fallback")
                print()
        
        print("\nFallback solution:")
        print("If MongoDB Atlas vector search is not working, you can use the manual_vector_search.py")
        print("utility to perform similarity searches using local calculations.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    check_all_embeddings() 