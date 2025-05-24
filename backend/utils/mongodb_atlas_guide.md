# MongoDB Atlas Vector Index Setup Guide

This guide will walk you through setting up vector indexes in MongoDB Atlas for the job recommendation system. These indexes are required for efficient vector similarity searches.

## Prerequisites

- MongoDB Atlas account with access to your cluster
- Collections with embedding vectors (candidates, jobs, projects)

## Vector Index Configuration

For all collections, we'll use the same vector index configuration:

```json
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
```

## Step-by-Step Instructions

### 1. Log in to MongoDB Atlas

- Go to [MongoDB Atlas](https://cloud.mongodb.com)
- Log in with your credentials

### 2. Navigate to your cluster

- From the dashboard, select your cluster (e.g., "Cluster0")

### 3. Access the Search tab

- In the cluster view, click on the "Search" tab in the top navigation

### 4. Create vector indexes for each collection

For each collection (`candidates`, `jobs`, `projects`), follow these steps:

#### a. Create a new index

- Click the "Create Index" button
- Select "JSON Editor" mode (instead of Visual Editor)

#### b. Configure the index for "candidates" collection

- Enter the following configuration:

```json
{
  "name": "candidates_vector_index",
  "fields": [
    {
      "numDimensions": 3072,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    }
  ]
}
```

- Select "candidates" from the collection dropdown
- Click "Create Index"

#### c. Configure the index for "jobs" collection

- Click "Create Index" again
- Enter the following configuration:

```json
{
  "name": "jobs_vector_index",
  "fields": [
    {
      "numDimensions": 3072,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    }
  ]
}
```

- Select "jobs" from the collection dropdown
- Click "Create Index"

#### d. Configure the index for "projects" collection

- Click "Create Index" again
- Enter the following configuration:

```json
{
  "name": "projects_vector_index",
  "fields": [
    {
      "numDimensions": 3072,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    }
  ]
}
```

- Select "projects" from the collection dropdown
- Click "Create Index"

### 5. Wait for index creation to complete

- Index creation is asynchronous and may take a few minutes
- You can monitor the status in the Search tab
- Indexes will show "Active" status when ready

### 6. Verify indexes are working

After the indexes are created and active, run the verification scripts:

```bash
# Check all collections
python utils/check_all_embeddings.py

# Or check individual collections
python utils/check_project_embeddings.py
python utils/check_job_embeddings.py
```

## Troubleshooting

### Index not showing up

- Ensure you have the correct cluster selected
- Check that you've selected the correct database and collection
- Indexes may take several minutes to build, especially for large collections

### Vector search not working

- Verify that the index name matches exactly what the code expects:
  - `candidates_vector_index` for candidates collection
  - `jobs_vector_index` for jobs collection
  - `projects_vector_index` for projects collection
- Ensure the dimension (3072) matches your actual embedding vectors
- Check that the path ("embedding") matches the field name in your documents

### Fallback solution

If vector search is still not working after setting up the indexes, you can use the manual vector search utility:

```bash
python utils/manual_vector_search.py --collection candidates --limit 5
python utils/manual_vector_search.py --collection jobs --limit 5
python utils/manual_vector_search.py --collection projects --limit 5
```

This performs similarity calculations locally instead of using MongoDB Atlas vector search. 