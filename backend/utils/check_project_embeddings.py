import pymongo
from bson import ObjectId
from tabulate import tabulate
import numpy as np
import traceback

# MongoDB connection details
MONGODB_URL = "mongodb+srv://lamma:1234567890@cluster0.eetq9gm.mongodb.net/"
DATABASE_NAME = "job_recommender"
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

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    
    # Avoid division by zero
    if norm_a == 0 or norm_b == 0:
        return 0
        
    return dot_product / (norm_a * norm_b)

def check_project_embeddings():
    try:
    client = pymongo.MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    collection = db[PROJECTS_COLLECTION]
    
    print_section("PROJECT COLLECTION STATISTICS")
    total_count = collection.count_documents({})
    with_embedding_count = collection.count_documents({"embedding": {"$exists": True}})
    without_embedding_count = collection.count_documents({"embedding": {"$exists": False}})
    
    print(f"Total projects: {total_count}")
    print(f"Projects with embeddings: {with_embedding_count}")
    print(f"Projects without embeddings: {without_embedding_count}")
    
    if with_embedding_count == 0:
        print("\n❌ No projects have embeddings! This is the main issue.")
        print("   The embedding generation during project creation might not be working.")
        client.close()
        return
    
    print_section("EXAMINING EMBEDDINGS")
    
    # Get a sample project with embedding
    sample_project = collection.find_one({"embedding": {"$exists": True}})
    
    if sample_project:
        print(f"Sample project title: {sample_project.get('title', 'Unknown title')}")
        print(f"Project ID: {sample_project.get('id', 'No ID')}")
        print(f"Project Type: {sample_project.get('project_type', 'Unknown type')}")
        
        embedding = sample_project.get('embedding')
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
        print("\n❌ Could not find any projects with embeddings")
    
    print_section("CHECKING MONGODB INDEXES")
    indexes = list(collection.list_indexes())
        
        # Expected index name
        expected_index_name = "projects_vector_index"
    
    vector_index_exists = False
    for idx in indexes:
            if idx.get("name") == expected_index_name:
            vector_index_exists = True
                print(f"✅ Vector index found in projects collection with name '{expected_index_name}'")
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
        print("❌ No vector index found in projects collection")
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
        
        # Test vector search functionality
        print_section("TESTING VECTOR SEARCH")
        
        if with_embedding_count > 1:
            # Get the embedding from our sample project
            query_embedding = sample_project.get('embedding')
            
            if query_embedding and isinstance(query_embedding, list):
                print(f"Embedding dimension: {len(query_embedding)}")
                
                # Try Atlas vector search
                print("\nAttempting MongoDB Atlas vector search...")
                results = None
                
                # Try different query formats
                query_formats = [
                    # Format 1: Using vectorSearch
                    {
                        "$search": {
                            "index": expected_index_name,
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
                            "index": expected_index_name,
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
                                    "title": 1,
                                    "score": {"$meta": "searchScore"}
                                }
                            }
                        ]
                        
                        results = list(collection.aggregate(pipeline))
                        
                        if results:
                            print(f"✅ Vector search is working with format {i+1}!")
                            print(f"Found {len(results)} similar projects")
                            break
                        else:
                            print(f"❌ No results returned from query format {i+1}")
                    except Exception as e:
                        print(f"❌ Error with format {i+1}: {str(e)}")
                
                if not results:
                    print("\n❌ All vector search formats failed")
                    print("This likely means the vector index is not set up correctly or has a different name")
                    
                    # Try manual approach
                    print("\nTrying manual similarity calculation (fallback method)...")
                    
                    # Get all projects with embeddings except the query project
                    all_projects = list(collection.find(
                        {"embedding": {"$exists": True}, "_id": {"$ne": sample_project["_id"]}}
                    ).limit(5))
                    
                    if all_projects:
                        print(f"Found {len(all_projects)} other projects with embeddings for manual calculation")
                        
                        # Calculate similarity manually for one project as a test
                        test_project = all_projects[0]
                        test_embedding = test_project.get('embedding')
                        if test_embedding and isinstance(test_embedding, list):
                            similarity = cosine_similarity(query_embedding, test_embedding)
                            print(f"Manual similarity calculation result: {similarity}")
                            print("✅ Manual similarity calculation is working")
                            print("   You can use utils/manual_vector_search.py as a fallback solution")
                    else:
                        print("❌ Could not find any other projects with embeddings for manual calculation")
    
    # Show some projects that don't have embeddings (if any)
    if without_embedding_count > 0:
        print_section("PROJECTS MISSING EMBEDDINGS")
        projects_without_embedding = collection.find(
            {"embedding": {"$exists": False}}
        ).limit(5)  # Show at most 5 examples
        
        for i, project in enumerate(projects_without_embedding):
            print(f"\nProject {i+1}:")
            print(f"  Title: {project.get('title', 'Unknown')}")
            print(f"  ID: {project.get('id', 'Unknown')}")
            print(f"  Type: {project.get('project_type', 'Unknown')}")
            print(f"  Created at: {project.get('created_at', 'Unknown')}")
    
        # Summary and recommendations
        print_section("SUMMARY AND RECOMMENDATIONS")
        
        if with_embedding_count > 0:
            print("✅ Projects have embeddings with correct dimensions (3072)")
        else:
            print("❌ No projects have embeddings")
            print("   Check the embedding generation process during project creation")
        
        if vector_index_exists:
            print("✅ Vector index exists for projects collection")
        else:
            print("❌ No vector index found in projects collection")
            print(f"   Create a vector index named '{expected_index_name}' in MongoDB Atlas")
            print("   Use the configuration shown above")
        
        if not vector_index_exists:
            print("\nIn the meantime, you can use the manual_vector_search.py utility:")
            print("   python utils/manual_vector_search.py --collection projects --limit 5")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
    finally:
    client.close()

if __name__ == "__main__":
    check_project_embeddings() 