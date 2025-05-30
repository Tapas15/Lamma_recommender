import pymongo
from bson import ObjectId
from tabulate import tabulate
import numpy as np

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

def check_candidate_embeddings():
    client = pymongo.MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    collection = db[CANDIDATES_COLLECTION]
    
    print_section("CANDIDATE COLLECTION STATISTICS")
    total_count = collection.count_documents({})
    with_embedding_count = collection.count_documents({"embedding": {"$exists": True}})
    without_embedding_count = collection.count_documents({"embedding": {"$exists": False}})
    
    print(f"Total candidates: {total_count}")
    print(f"Candidates with embeddings: {with_embedding_count}")
    print(f"Candidates without embeddings: {without_embedding_count}")
    
    if with_embedding_count == 0:
        print("\n❌ No candidates have embeddings! This is the main issue.")
        print("   The embedding generation during candidate registration or profile update might not be working.")
        client.close()
        return
    
    print_section("EXAMINING EMBEDDINGS")
    
    # Get a sample candidate with embedding
    sample_candidate = collection.find_one({"embedding": {"$exists": True}})
    
    if sample_candidate:
        print(f"Sample candidate name: {sample_candidate.get('full_name', 'Unknown name')}")
        print(f"Candidate ID: {sample_candidate.get('id', 'No ID')}")
        print(f"Email: {sample_candidate.get('email', 'No email')}")
        
        embedding = sample_candidate.get('embedding')
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
            else:
                print(f"\n❌ Embedding is not a list! Type: {type(embedding)}")
                print("   This will prevent vector search from working")
        else:
            print("\n❌ Embedding is None or empty!")
    else:
        print("\n❌ Could not find any candidates with embeddings")
    
    print_section("CHECKING MONGODB INDEXES")
    indexes = list(collection.list_indexes())
    
    vector_index_exists = False
    for idx in indexes:
        # Check for any index that might be a vector index, not just by name
        if idx.get("name") == "candidates_vector_index":
            vector_index_exists = True
            print("✅ Vector index found in candidates collection with name 'candidates_vector_index'")
            break
    
    # If we didn't find the exact name, check for any index that might be a vector index
    if not vector_index_exists:
        # Try to check Atlas Search indexes (requires admin privileges)
        try:
            # This is a simple attempt to detect if any index might be a vector index
            # MongoDB Atlas Search indexes might not be fully visible through the driver
            print("Checking for any vector indexes...")
            
            # In MongoDB Atlas, vector indexes are created as Atlas Search indexes
            # which may not be fully visible through the driver API
            # Let's check if there are any indexes that might be vector indexes
            for idx in indexes:
                idx_name = idx.get("name", "")
                if "vector" in idx_name.lower() or "search" in idx_name.lower():
                    vector_index_exists = True
                    print(f"✅ Potential vector index found with name: {idx_name}")
                    break
        except Exception as e:
            print(f"Error checking for vector indexes: {str(e)}")
    
    if not vector_index_exists:
        print("❌ No vector index found in candidates collection")
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
        print("   Name the index 'candidates_vector_index' for automatic detection")
    
    # Show some candidates that don't have embeddings (if any)
    if without_embedding_count > 0:
        print_section("CANDIDATES MISSING EMBEDDINGS")
        candidates_without_embedding = collection.find(
            {"embedding": {"$exists": False}}
        ).limit(5)  # Show at most 5 examples
        
        for i, candidate in enumerate(candidates_without_embedding):
            print(f"\nCandidate {i+1}:")
            print(f"  Name: {candidate.get('full_name', 'Unknown')}")
            print(f"  ID: {candidate.get('id', 'Unknown')}")
            print(f"  Email: {candidate.get('email', 'Unknown')}")
            print(f"  Created at: {candidate.get('created_at', 'Unknown')}")
    
    client.close()

if __name__ == "__main__":
    check_candidate_embeddings() 