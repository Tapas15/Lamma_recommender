#!/usr/bin/env python
"""
Manual Vector Search Utility

This script provides a fallback method for vector similarity searches
when MongoDB Atlas vector search is not available or not working.
It retrieves embeddings from MongoDB and performs similarity calculations locally.

Usage:
    python manual_vector_search.py [--collection COLLECTION] [--id ID] [--limit LIMIT]

Examples:
    # Search for similar candidates to a specific candidate
    python manual_vector_search.py --collection candidates --id 6830b210d8cf4dbaafdfca20 --limit 5
    
    # Search for similar jobs to a specific job
    python manual_vector_search.py --collection jobs --id 12345 --limit 10
    
    # Search for similar projects to a specific project
    python manual_vector_search.py --collection projects --id 67890 --limit 3
"""

import pymongo
import numpy as np
from bson import ObjectId
from tabulate import tabulate
import argparse
import sys
import traceback

# MongoDB connection details
MONGODB_URL = "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/"
DATABASE_NAME = "job_recommender"

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

def get_item_details(item, collection_name):
    """Extract relevant details from an item based on collection type"""
    try:
        if collection_name == "candidates":
            # Safe handling for skills
            skills_text = "None"
            try:
                skills = item.get('skills', [])
                if skills and isinstance(skills, list):
                    # Take only first 3 skills if available
                    skills_subset = skills[:3] if len(skills) > 3 else skills
                    skills_text = ", ".join(skills_subset)
            except Exception as e:
                skills_text = f"Error: {str(e)}"
            
            return {
                "name": item.get("full_name", "Unknown"),
                "id": item.get("id", "Unknown"),
                "email": item.get("email", "Unknown"),
                "additional": f"Skills: {skills_text}..."
            }
        elif collection_name == "jobs":
            return {
                "name": item.get("title", "Unknown"),
                "id": item.get("id", "Unknown"),
                "email": item.get("company", "Unknown"),
                "additional": f"Location: {item.get('location', 'Unknown')}"
            }
        elif collection_name == "projects":
            return {
                "name": item.get("title", "Unknown"),
                "id": item.get("id", "Unknown"),
                "email": item.get("project_type", "Unknown"),
                "additional": f"Status: {item.get('status', 'Unknown')}"
            }
        else:
            return {
                "name": "Unknown",
                "id": "Unknown",
                "email": "Unknown",
                "additional": "Unknown"
            }
    except Exception as e:
        print(f"Error in get_item_details: {str(e)}")
        traceback.print_exc()
        return {
            "name": "Error",
            "id": "Error",
            "email": "Error",
            "additional": f"Error: {str(e)}"
        }

def manual_vector_search(collection_name, item_id=None, limit=5):
    """
    Perform manual vector similarity search
    
    Args:
        collection_name: Name of the MongoDB collection to search in
        item_id: ID of the item to use as query (if None, use a random item)
        limit: Maximum number of results to return
    """
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        collection = db[collection_name]
        
        print_section(f"MANUAL VECTOR SEARCH IN {collection_name.upper()}")
        
        # Get query item
        query_item = None
        if item_id:
            # Try to find by ID string
            query_item = collection.find_one({"id": item_id})
            # If not found, try as ObjectId
            if not query_item:
                try:
                    query_item = collection.find_one({"_id": ObjectId(item_id)})
                except:
                    pass
        
        # If no ID provided or item not found, get a random item with embedding
        if not query_item:
            query_item = collection.find_one({"embedding": {"$exists": True}})
        
        if not query_item:
            print("❌ Could not find any items with embeddings")
            client.close()
            return
        
        # Get details based on collection type
        item_details = get_item_details(query_item, collection_name)
        print(f"Using {collection_name[:-1]} '{item_details['name']}' as query")
        print(f"ID: {item_details['id']}")
        
        # Get the embedding
        query_embedding = query_item.get('embedding')
        
        if not query_embedding or not isinstance(query_embedding, list):
            print("❌ Invalid embedding found in the query item")
            client.close()
            return
            
        print(f"Embedding dimension: {len(query_embedding)}")
        
        # Get all items with embeddings except the query item
        all_items = list(collection.find(
            {"embedding": {"$exists": True}, "_id": {"$ne": query_item["_id"]}}
        ))
        
        if not all_items:
            print(f"❌ Could not find any other {collection_name} with embeddings")
            client.close()
            return
            
        print(f"Found {len(all_items)} {collection_name} with embeddings")
        
        # Calculate similarity manually
        similarities = []
        for item in all_items:
            embedding = item.get('embedding')
            if embedding and isinstance(embedding, list):
                similarity = cosine_similarity(query_embedding, embedding)
                similarities.append({
                    "item": item,
                    "similarity": similarity
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Display results
        if similarities:
            print(f"\nTop {min(limit, len(similarities))} most similar {collection_name}:")
            table_data = []
            
            for i, sim_item in enumerate(similarities[:limit]):
                item = sim_item["item"]
                details = get_item_details(item, collection_name)
                
                table_data.append([
                    i + 1,
                    details["name"],
                    details["email"],
                    details["additional"],
                    sim_item["similarity"]
                ])
            
            headers = ["#", "Name", "Email/Company/Type", "Additional Info", "Similarity"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            print("\n✅ Manual similarity calculation completed successfully")
        else:
            print(f"❌ Could not calculate similarities for {collection_name}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
    finally:
        client.close()

def main():
    parser = argparse.ArgumentParser(description="Manual vector similarity search tool")
    parser.add_argument("--collection", type=str, default="candidates", 
                        choices=["candidates", "jobs", "projects"],
                        help="Collection to search in (candidates, jobs, projects)")
    parser.add_argument("--id", type=str, default=None,
                        help="ID of the item to use as query (if omitted, uses a random item)")
    parser.add_argument("--limit", type=int, default=5,
                        help="Maximum number of results to return")
    
    args = parser.parse_args()
    manual_vector_search(args.collection, args.id, args.limit)

if __name__ == "__main__":
    main() 