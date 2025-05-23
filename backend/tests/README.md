# Search and Recommendation System Tests

This directory contains test scripts for verifying the functionality of the search and recommendation system in the job platform.

## Available Tests

1. **test_search_recommender.py** - Comprehensive test for both search and recommendation functionality
2. **test_recommendation_system.py** - Focused tests for the recommendation system
3. **check_all_embeddings.py** - Utility to check vector embeddings across all collections

## Setup

Before running the tests, make sure you have:

1. MongoDB Atlas properly configured with vector search indexes
2. The backend API running locally or deployed
3. Ollama running for embedding generation
4. Test user accounts created (both candidate and employer)

## Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```
API_BASE_URL=http://localhost:8000
TEST_CANDIDATE_EMAIL=your_test_candidate@example.com
TEST_CANDIDATE_PASSWORD=your_password
TEST_EMPLOYER_EMAIL=your_test_employer@example.com
TEST_EMPLOYER_PASSWORD=your_password
MONGODB_URL=your_mongodb_connection_string
DATABASE_NAME=job_recommender
```

## Running the Tests

### Check Embeddings

To verify that vector embeddings are properly generated and indexed:

```bash
cd backend
python tests/check_all_embeddings.py
```

This will:
- Check if documents in each collection have embeddings
- Analyze the embedding vectors
- Verify that vector indexes exist
- Provide recommendations for fixing any issues

### Test Search and Recommendation

To test the complete search and recommendation functionality:

```bash
cd backend
python tests/test_search_recommender.py
```

This will:
- Test embedding generation
- Test semantic search for jobs, projects, and candidates
- Test recommendation functionality
- Test fallback search mechanisms

### Test Recommendation System Only

To focus on testing just the recommendation system:

```bash
cd backend
python tests/test_recommendation_system.py
```

This will:
- Test job recommendations for candidates
- Test candidate recommendations for jobs
- Test project recommendations for candidates
- Test skill gap analysis
- Test learning recommendations

## Troubleshooting

If the tests fail, check the following:

1. **Embedding Generation Issues**:
   - Make sure Ollama is running and accessible
   - Check the embedding model configuration
   - Verify that documents are being saved with embeddings

2. **Vector Index Issues**:
   - Verify that MongoDB Atlas vector indexes are created
   - Check the index configuration (dimensions, similarity metric)
   - Run `python utils/create_vector_indexes.py` to set up indexes

3. **API Connection Issues**:
   - Verify the API is running at the specified URL
   - Check that test user credentials are correct
   - Ensure the API endpoints are implemented correctly

4. **Data Issues**:
   - Ensure there is sufficient test data in the database
   - Verify that test users have complete profiles
   - Check that jobs and projects have proper descriptions 