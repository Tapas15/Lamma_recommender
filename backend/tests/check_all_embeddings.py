#!/usr/bin/env python
"""
Script to check embeddings for all collections (jobs, projects, and candidates) in one run.
This helps verify that all vector embeddings are properly generated and indexed.

Usage:
    python check_all_embeddings.py
"""

import sys
import os
import pymongo
from bson import ObjectId
from tabulate import tabulate
import numpy as np
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# MongoDB connection details
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "job_recommender")

# Collections
JOBS_COLLECTION = "jobs"
CANDIDATES_COLLECTION = "candidates"
PROJECTS_COLLECTION = "projects"

def print_section(title):
    """Print a section title for better readability"""
    print("\n")
    print("=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

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

def check_collection_embeddings(client, collection_name, expected_index_name=None):
    """Check embeddings for a specific collection"""
    print_section(f"CHECKING {collection_name.upper()} EMBEDDINGS")
    
    db = client[DATABASE_NAME]
    collection = db[collection_name]
    
    # Collection statistics
    total_count = collection.count_documents({})
    with_embedding_count = collection.count_documents({"embedding": {"$exists": True}})
    without_embedding_count = collection.count_documents({"embedding": {"$exists": False}})
    
    print(f"Total documents: {total_count}")
    print(f"Documents with embeddings: {with_embedding_count}")
    print(f"Documents without embeddings: {without_embedding_count}")
    
    embedding_coverage = (with_embedding_count / total_count * 100) if total_count > 0 else 0
    print(f"Embedding coverage: {embedding_coverage:.1f}%")
    
    # Check if any embeddings exist
    if with_embedding_count == 0:
        print("\n❌ No documents have embeddings! This is a critical issue.")
        print(f"   The embedding generation for {collection_name} might not be working.")
        return {
            "total": total_count,
            "with_embedding": with_embedding_count,
            "without_embedding": without_embedding_count,
            "coverage": embedding_coverage,
            "has_embeddings": False,
            "correct_dimensions": False,
            "has_vector_index": False
        }
    
    # Get a sample document with embedding
    sample = collection.find_one({"embedding": {"$exists": True}})
    
    has_embeddings = False
    correct_dimensions = False
    
    if sample:
        # Get identifying info based on collection type
        if collection_name == JOBS_COLLECTION:
            print(f"Sample job title: {sample.get('title', 'Unknown title')}")
            print(f"Job ID: {sample.get('id', 'No ID')}")
        elif collection_name == CANDIDATES_COLLECTION:
            print(f"Sample candidate name: {sample.get('full_name', 'Unknown name')}")
            print(f"Candidate ID: {sample.get('id', 'No ID')}")
        elif collection_name == PROJECTS_COLLECTION:
            print(f"Sample project title: {sample.get('title', 'Unknown title')}")
            print(f"Project ID: {sample.get('id', 'No ID')}")
        
        embedding = sample.get('embedding')
        if embedding:
            has_embeddings = True
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
                
                if analysis["dimension"] == 3072:
                    correct_dimensions = True
                    print("\n✅ Embedding has the expected dimension of 3072")
                else:
                    print(f"\n⚠️ Warning: Expected embedding dimension 3072, but found {analysis['dimension']}")
                    print("   This may cause issues with vector search")
            else:
                print(f"\n❌ Embedding is not a list! Type: {type(embedding)}")
                print("   This will prevent vector search from working")
        else:
            print("\n❌ Embedding is None or empty!")
    else:
        print("\n❌ Could not find any documents with embeddings")
    
    # Check for vector index
    print_section(f"CHECKING {collection_name.upper()} VECTOR INDEX")
    indexes = list(collection.list_indexes())
    
    vector_index_exists = False
    expected_index_name = expected_index_name or f"{collection_name}_vector_index"
    
    for idx in indexes:
        if idx.get("name") == expected_index_name:
            vector_index_exists = True
            print(f"✅ Vector index '{expected_index_name}' found in {collection_name} collection")
            break
    
    if not vector_index_exists:
        print(f"❌ No vector index '{expected_index_name}' found in {collection_name} collection")
        print("   Run 'python create_vector_indexes.py' to create the required indexes")
    
    # Return summary data
    return {
        "total": total_count,
        "with_embedding": with_embedding_count,
        "without_embedding": without_embedding_count,
        "coverage": embedding_coverage,
        "has_embeddings": has_embeddings,
        "correct_dimensions": correct_dimensions,
        "has_vector_index": vector_index_exists
    }

def check_all_embeddings():
    """Check embeddings for all collections"""
    try:
        client = pymongo.MongoClient(MONGODB_URL)
        
        print_section("VECTOR EMBEDDING CHECK")
        print(f"MongoDB URL: {MONGODB_URL}")
        print(f"Database: {DATABASE_NAME}")
        
        # Check each collection
        jobs_result = check_collection_embeddings(client, JOBS_COLLECTION, "jobs_vector_index")
        candidates_result = check_collection_embeddings(client, CANDIDATES_COLLECTION, "candidates_vector_index")
        projects_result = check_collection_embeddings(client, PROJECTS_COLLECTION, "projects_vector_index")
        
        # Summary table
        print_section("SUMMARY")
        
        summary_data = [
            ["Jobs", 
             f"{jobs_result['with_embedding']}/{jobs_result['total']}", 
             f"{jobs_result['coverage']:.1f}%",
             "✅" if jobs_result['has_embeddings'] else "❌",
             "✅" if jobs_result['correct_dimensions'] else "❌",
             "✅" if jobs_result['has_vector_index'] else "❌"],
            ["Candidates", 
             f"{candidates_result['with_embedding']}/{candidates_result['total']}", 
             f"{candidates_result['coverage']:.1f}%",
             "✅" if candidates_result['has_embeddings'] else "❌",
             "✅" if candidates_result['correct_dimensions'] else "❌",
             "✅" if candidates_result['has_vector_index'] else "❌"],
            ["Projects", 
             f"{projects_result['with_embedding']}/{projects_result['total']}", 
             f"{projects_result['coverage']:.1f}%",
             "✅" if projects_result['has_embeddings'] else "❌",
             "✅" if projects_result['correct_dimensions'] else "❌",
             "✅" if projects_result['has_vector_index'] else "❌"]
        ]
        
        print(tabulate(summary_data, 
                      headers=["Collection", "Embeddings", "Coverage", "Has Embeddings", "Correct Dimensions", "Has Vector Index"], 
                      tablefmt="grid"))
        
        # Overall assessment
        all_have_embeddings = all([
            jobs_result['has_embeddings'],
            candidates_result['has_embeddings'],
            projects_result['has_embeddings']
        ])
        
        all_correct_dimensions = all([
            jobs_result['correct_dimensions'],
            candidates_result['correct_dimensions'],
            projects_result['correct_dimensions']
        ])
        
        all_have_indexes = all([
            jobs_result['has_vector_index'],
            candidates_result['has_vector_index'],
            projects_result['has_vector_index']
        ])
        
        if all_have_embeddings and all_correct_dimensions and all_have_indexes:
            print("\n✅ All collections have proper embeddings and vector indexes!")
            print("   The semantic search and recommender system should be working correctly.")
        else:
            print("\n⚠️ There are issues with embeddings or vector indexes that need to be addressed.")
            
            if not all_have_embeddings:
                print("\nRecommendation: Check embedding generation during document creation/update.")
                print("Ensure Ollama is running and accessible for embedding generation.")
            
            if not all_correct_dimensions:
                print("\nRecommendation: Check the embedding model configuration.")
                print("The system expects 3072-dimensional vectors from the Ollama model.")
            
            if not all_have_indexes:
                print("\nRecommendation: Create the required vector indexes in MongoDB Atlas.")
                print("Run 'python create_vector_indexes.py' and follow the instructions.")
    
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    check_all_embeddings() 