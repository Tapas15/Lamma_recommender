# Skill Clusters API Endpoint Documentation

## Overview

The skill clusters API endpoint provides an analysis of skill clusters, grouping related skills together based on their co-occurrence in job postings, candidate profiles, and industry data. This endpoint is useful for understanding skill relationships, identifying complementary skills, and developing learning paths.

## Endpoint

```
GET /ml/skills/clusters
```

This endpoint returns groups of related skills organized into clusters, with confidence scores and additional metadata.

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_confidence` | float | 0.7 | Minimum confidence score for skill relationships (0.0-1.0) |
| `max_clusters` | integer | 20 | Maximum number of clusters to return (1-50) |
| `include_details` | boolean | true | Whether to include detailed information about each cluster |

## Response

The response includes a list of skill clusters, each containing a set of related skills, along with metadata about the analysis.

### Example Response

```json
{
  "clusters": [
    {
      "name": "Frontend Development",
      "confidence": 0.92,
      "skills": ["JavaScript", "HTML", "CSS", "React", "Angular", "Vue.js", "TypeScript", "Redux", "Webpack", "UI/UX Design", "Responsive Design", "SASS/LESS", "Jest", "Cypress", "Storybook"],
      "details": {
        "core_skills": ["JavaScript", "HTML", "CSS", "React", "Angular", "Vue.js", "TypeScript", "Redux", "Webpack"],
        "related_skills": ["UI/UX Design", "Responsive Design", "SASS/LESS", "Jest", "Cypress", "Storybook"],
        "industry_relevance": ["Technology", "E-commerce", "Media", "Marketing"],
        "growth_rate": 0.15,
        "skill_count": 15,
        "market_demand": 0.78
      }
    },
    {
      "name": "Data Science",
      "confidence": 0.93,
      "skills": ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Data Visualization", "Statistical Analysis", "Machine Learning", "Big Data"],
      "details": {
        "core_skills": ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch"],
        "related_skills": ["Data Visualization", "Statistical Analysis", "Machine Learning", "Big Data"],
        "industry_relevance": ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"],
        "growth_rate": 0.28,
        "skill_count": 12,
        "market_demand": 0.85
      }
    }
  ],
  "metadata": {
    "min_confidence": 0.7,
    "max_clusters": 20,
    "total_clusters": 2,
    "total_skills_analyzed": 3254,
    "analysis_timestamp": "2023-10-15T14:32:17.123456"
  },
  "statistics": {
    "average_cluster_size": 13.5,
    "largest_cluster_size": 15,
    "smallest_cluster_size": 12,
    "average_confidence": 0.925,
    "skill_distribution": {
      "Technology": 0.85,
      "Finance": 0.65,
      "Healthcare": 0.55,
      "Retail": 0.45,
      "Manufacturing": 0.40,
      "Media": 0.35,
      "Education": 0.30
    },
    "industry_relevance": {
      "Technology": {
        "relevance_score": 0.92,
        "top_clusters": ["Frontend Development", "Data Science", "Cloud Computing"]
      },
      "Finance": {
        "relevance_score": 0.85,
        "top_clusters": ["Data Science", "Cybersecurity", "Blockchain"]
      }
    }
  }
}
```

## Response Fields

### Clusters

Each cluster in the `clusters` array contains:

- `name`: The name of the skill cluster
- `confidence`: A score from 0.0 to 1.0 indicating the confidence in the relationship between skills in this cluster
- `skills`: An array of skill names in this cluster
- `details`: (Optional, included when `include_details=true`)
  - `core_skills`: Primary skills in this cluster
  - `related_skills`: Secondary skills that complement the core skills
  - `industry_relevance`: Industries where this skill cluster is most relevant
  - `growth_rate`: Annual growth rate of demand for this skill cluster
  - `skill_count`: Total number of skills in this cluster
  - `market_demand`: Score from 0.0 to 1.0 indicating market demand for this skill cluster

### Metadata

- `min_confidence`: The minimum confidence threshold used for this analysis
- `max_clusters`: The maximum number of clusters requested
- `total_clusters`: The actual number of clusters returned
- `total_skills_analyzed`: The total number of skills analyzed to generate these clusters
- `analysis_timestamp`: When the analysis was performed

### Statistics (Optional)

Included when `include_details=true`:

- `average_cluster_size`: Average number of skills per cluster
- `largest_cluster_size`: Number of skills in the largest cluster
- `smallest_cluster_size`: Number of skills in the smallest cluster
- `average_confidence`: Average confidence score across all clusters
- `skill_distribution`: Distribution of skills across different domains
- `industry_relevance`: Relevance of skill clusters to different industries

## Authentication

This endpoint requires authentication with a valid JWT token.

## Error Handling

### Common Errors

- `400 Bad Request`: Invalid parameter values
  - Example: `min_confidence` outside the range 0.0-1.0, `max_clusters` outside the range 1-50
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Server-side processing error

## Example Usage

```python
import requests

url = "https://api.example.com/ml/skills/clusters"
headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}
params = {
    "min_confidence": 0.8,
    "max_clusters": 10,
    "include_details": True
}

response = requests.get(url, params=params, headers=headers)
clusters = response.json()
```

## Use Cases

1. **Career Path Planning**: Identify complementary skills to develop for career advancement
2. **Curriculum Development**: Create comprehensive learning paths for specific job roles
3. **Talent Acquisition**: Understand skill relationships to better evaluate candidate profiles
4. **Workforce Planning**: Identify skill gaps and training needs across teams
5. **Job Description Creation**: Generate comprehensive skill requirements for job postings

## Notes

- The confidence score represents the strength of relationship between skills in a cluster
- Higher confidence scores indicate skills that frequently appear together in job postings and candidate profiles
- The growth rate indicates the annual increase in demand for skills in a cluster
- Market demand is calculated based on current job postings, industry trends, and growth rates 