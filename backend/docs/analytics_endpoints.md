# Analytics API Endpoints Documentation

## Overview

The analytics API endpoints provide insights into recommendation system performance, usage metrics, and impact analysis. These endpoints help users understand how recommendations are performing and how the system is being utilized.

## Endpoints

### 1. Recommendation Impact Metrics

```
GET /analytics/recommendations/impact
```

This endpoint provides metrics about the effectiveness of recommendations, including view rates, application rates, and conversion rates.

#### Query Parameters

- `period` (string, default: "last_30_days"): Time period for the metrics
  - Options: "last_7_days", "last_30_days", "last_90_days", "all_time"
- `recommendation_type` (string, default: "all"): Type of recommendations to analyze
  - Options: "jobs", "candidates", "projects", "all"

#### Response

The response varies based on the user type (employer or candidate) and the recommendation type requested.

##### Employer Response Example

```json
{
  "summary": {
    "total_recommendations_shown": 450,
    "total_recommendations_viewed": 210,
    "total_actions_taken": 75,
    "conversion_rate": 0.167
  },
  "trends": {
    "interval": "daily",
    "dates": ["2023-10-01", "2023-10-02", "..."],
    "views": [12, 15, "..."],
    "actions": [3, 5, "..."],
    "match_scores": [75.2, 78.6, "..."]
  },
  "candidates": {
    "total_candidates_recommended": 350,
    "candidates_viewed": 180,
    "candidates_contacted": 60,
    "candidates_interviewed": 25,
    "candidates_hired": 5,
    "contact_rate": 0.333,
    "interview_rate": 0.139,
    "hire_rate": 0.028,
    "average_match_score": 75.5
  },
  "top_performing": [
    {
      "type": "job",
      "id": "job_1",
      "title": "Top Performing Job 1",
      "metrics": {
        "candidates_recommended": 45,
        "candidates_viewed": 28,
        "candidates_contacted": 12,
        "contact_rate": 0.429,
        "average_match_score": 82.5
      }
    }
  ],
  "period": {
    "name": "last_30_days",
    "start_date": "2023-09-15",
    "end_date": "2023-10-15",
    "days": 30
  },
  "recommendation_type": "all"
}
```

##### Candidate Response Example

```json
{
  "summary": {
    "total_recommendations_shown": 320,
    "total_recommendations_viewed": 180,
    "total_actions_taken": 45,
    "conversion_rate": 0.25
  },
  "trends": {
    "interval": "daily",
    "dates": ["2023-10-01", "2023-10-02", "..."],
    "views": [10, 12, "..."],
    "actions": [2, 4, "..."],
    "match_scores": [72.5, 76.8, "..."]
  },
  "jobs": {
    "total_jobs_recommended": 280,
    "jobs_viewed": 160,
    "jobs_saved": 50,
    "jobs_applied": 30,
    "interviews_received": 8,
    "view_rate": 0.571,
    "application_rate": 0.188,
    "interview_rate": 0.267,
    "average_match_score": 76.2
  },
  "top_performing": [
    {
      "type": "job_category",
      "name": "Software Development",
      "metrics": {
        "jobs_recommended": 45,
        "jobs_viewed": 28,
        "jobs_applied": 10,
        "application_rate": 0.357,
        "average_match_score": 82.5
      }
    }
  ],
  "period": {
    "name": "last_30_days",
    "start_date": "2023-09-15",
    "end_date": "2023-10-15",
    "days": 30
  },
  "recommendation_type": "all"
}
```

### 2. Recommendation Algorithm Performance

```
GET /analytics/recommendations/performance
```

This endpoint provides analytics data on how the recommendation algorithm is performing, including accuracy, precision, recall, and other relevant metrics.

#### Query Parameters

- `algorithm_version` (string, default: "latest"): Version of the algorithm to analyze
  - Options: "latest", "v1", "v2", "v3"

#### Response Example

```json
{
  "algorithm_version": "v3",
  "last_updated": "2023-09-20",
  "overall_accuracy": 0.75,
  "precision": 0.72,
  "recall": 0.68,
  "f1_score": 0.7,
  "average_match_score": 75,
  "recommendation_types": {
    "jobs": {
      "accuracy": 0.78,
      "precision": 0.75,
      "recall": 0.72,
      "f1_score": 0.73,
      "average_match_score": 78
    },
    "candidates": {
      "accuracy": 0.72,
      "precision": 0.7,
      "recall": 0.65,
      "f1_score": 0.67,
      "average_match_score": 72
    },
    "projects": {
      "accuracy": 0.7,
      "precision": 0.68,
      "recall": 0.62,
      "f1_score": 0.65,
      "average_match_score": 70
    }
  },
  "embedding_metrics": {
    "dimension": 3072,
    "average_l2_norm": 1.023,
    "average_cosine_similarity": 0.65,
    "clustering_coefficient": 0.55
  },
  "version_comparison": [
    {
      "version": "v1",
      "accuracy": 0.525,
      "improvement": "-30%"
    },
    {
      "version": "v2",
      "accuracy": 0.637,
      "improvement": "-15%"
    },
    {
      "version": "v3",
      "accuracy": 0.75,
      "improvement": "current"
    }
  ]
}
```

## Authentication

All analytics endpoints require authentication with a valid JWT token.

## Error Handling

### Common Errors

- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Server-side processing error

## Usage Notes

1. For the most accurate metrics, use the default "last_30_days" period which provides a good balance of data volume and recency.
2. The "all" recommendation type provides a comprehensive overview of system performance across all recommendation types.
3. Algorithm performance metrics are most useful for understanding how different versions of the recommendation algorithm compare.

## Example Usage

```python
import requests

url = "https://api.example.com/analytics/recommendations/impact"
headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}
params = {
    "period": "last_30_days",
    "recommendation_type": "all"
}

response = requests.get(url, params=params, headers=headers)
metrics = response.json() 