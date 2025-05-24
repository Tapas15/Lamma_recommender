#!/usr/bin/env python
"""
Test script to verify if vector search is working with MongoDB Atlas.
This script will:
1. Connect to MongoDB
2. Get a sample embedding from a candidate
3. Try to find similar candidates using vector search
"""

import pymongo
import numpy as np
from bson import ObjectId
from tabulate import tabulate
import json

# MongoDB connection details
MONGODB_URL = "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/"
DATABASE_NAME = "job_recommender"
CANDIDATES_COLLECTION = "candidates"

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

def test_vector_search():
    """Test vector search functionality"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        collection = db[CANDIDATES_COLLECTION]
        
        print_section("TESTING VECTOR SEARCH")
        
        # Get a sample candidate with embedding
        sample_candidate = collection.find_one({"embedding": {"$exists": True}})
        
        if not sample_candidate:
            print("❌ Could not find any candidates with embeddings")
            client.close()
            return
            
        print(f"Using candidate '{sample_candidate.get('full_name')}' as query sample")
        
        # Get the embedding
        query_embedding = sample_candidate.get('embedding')
        
        if not query_embedding or not isinstance(query_embedding, list):
            print("❌ Invalid embedding found in the sample candidate")
            client.close()
            return
            
        print(f"Embedding dimension: {len(query_embedding)}")
        
        # Try Atlas vector search
        print_section("ATTEMPTING ATLAS VECTOR SEARCH")
        results = None
        
        # Try different query formats
        query_formats = [
            # Format 1: Using vectorSearch
                {
                    "$search": {
                    "index": "candidates_vector_index",
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
                    "index": "candidates_vector_index",
                    "knnVector": {
                        "vector": query_embedding,
                        "path": "embedding",
                        "k": 5
                    }
                }
            },
            
            # Format 3: Using vector
            {
                "$search": {
                    "index": "candidates_vector_index",
                    "vector": {
                        "vector": query_embedding,
                        "path": "embedding",
                        "k": 5
                    }
                }
            },
            
            # Format 4: Using the default index name
            {
                "$search": {
                    "vectorSearch": {
                        "queryVector": query_embedding,
                        "path": "embedding",
                        "numCandidates": 10,
                        "limit": 5
                    }
                }
            }
        ]
        
        for i, query_format in enumerate(query_formats):
            try:
                print(f"\nTrying query format {i+1}...")
                pipeline = [
                    query_format,
                    {
                        "$project": {
                            "_id": 1,
                            "full_name": 1,
                            "email": 1,
                            "score": {"$meta": "searchScore"}
                        }
                    }
                ]
                
                results = list(collection.aggregate(pipeline))
                
                if results:
                    print(f"✅ Vector search is working with format {i+1}!")
                    print(f"Found {len(results)} similar candidates:")
                    
                    # Display results in a table
                    table_data = []
                    for j, result in enumerate(results):
                        table_data.append([
                            j + 1,
                            result.get('full_name', 'Unknown'),
                            result.get('email', 'No email'),
                            result.get('score', 0)
                        ])
                    
                    print(tabulate(table_data, headers=["#", "Name", "Email", "Similarity Score"], tablefmt="grid"))
                    break  # Exit the loop if successful
                else:
                    print("❌ No results returned from this query format")
            except Exception as e:
                print(f"❌ Error with format {i+1}: {str(e)}")
        
        # If all query formats failed, try manual approach
        if not results:
            print("\n❌ All vector search formats failed")
            print("This likely means the vector index is not set up correctly or has a different name")
            
            # Try a manual approach as fallback
            print_section("FALLBACK: MANUAL VECTOR SIMILARITY")
            print("Trying manual similarity calculation (this is slower but works without vector index)")
            
            # Get all candidates
            all_candidates = list(collection.find(
                {"embedding": {"$exists": True}, "_id": {"$ne": sample_candidate["_id"]}}
            ).limit(10))
            
            if not all_candidates:
                print("❌ Could not find any other candidates with embeddings")
                client.close()
                return
                
            print(f"Found {len(all_candidates)} candidates with embeddings")
            
            # Calculate similarity manually
            similarities = []
            for candidate in all_candidates:
                embedding = candidate.get('embedding')
                if embedding and isinstance(embedding, list):
                    similarity = cosine_similarity(query_embedding, embedding)
                    similarities.append({
                        "candidate": candidate,
                        "similarity": similarity
                    })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Display results
            if similarities:
                print("Results from manual similarity calculation:")
                table_data = []
                for i, item in enumerate(similarities[:5]):  # Show top 5
                    candidate = item["candidate"]
                    table_data.append([
                        i + 1,
                        candidate.get('full_name', 'Unknown'),
                        candidate.get('email', 'No email'),
                        item["similarity"]
                    ])
                
                print(tabulate(table_data, headers=["#", "Name", "Email", "Similarity Score"], tablefmt="grid"))
                
                # Verify if manual calculation is working
                print("\n✅ Manual similarity calculation is working correctly")
                print("This confirms that your embeddings are valid and can be used for similarity search")
            else:
                print("❌ Could not calculate similarities")
        
        print_section("RECOMMENDATIONS")
        if results:
            print("✅ Vector search is working correctly!")
            print("Your MongoDB Atlas vector index is set up and functioning.")
        else:
            print("❌ Vector search is not working correctly.")
            print("Please check your MongoDB Atlas vector index setup:")
            print("1. Go to MongoDB Atlas")
            print("2. Navigate to your cluster")
            print("3. Go to the Search tab")
            print("4. Verify that your index is active")
            print("5. Check the actual name of your vector index (it might not be 'candidates_vector_index')")
            print("6. Ensure the index configuration matches:")
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
            print("\nIn the meantime, you can use the manual similarity calculation method")
            print("which is working correctly as shown above.")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    test_vector_search() 