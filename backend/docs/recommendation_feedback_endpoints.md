# Recommendation Feedback API Endpoints Documentation

## Overview

The recommendation feedback API endpoints allow users to provide feedback on recommendations they receive and to view aggregate feedback statistics. This feedback helps improve the recommendation system's accuracy and relevance over time.

## Endpoints

### 1. Submit Recommendation Feedback

```
POST /recommendations/feedback
```

This endpoint allows users to submit feedback on a specific recommendation they received, including relevance scores, accuracy scores, and general feedback.

#### Request Body

```json
{
  "recommendation_id": "job_rec_12345",
  "recommendation_type": "job",
  "relevance_score": 4,
  "accuracy_score": 5,
  "is_helpful": true,
  "feedback_text": "This job recommendation matched my skills well, but the location wasn't ideal.",
  "action_taken": "viewed_details"
}
```

#### Required Fields

- `recommendation_id`: String ID of the recommendation being rated
- `recommendation_type`: Type of recommendation (job, candidate, project, skill, career_path)
- `relevance_score`: Integer from 1-5 indicating relevance (1=not relevant, 5=highly relevant)
- `accuracy_score`: Integer from 1-5 indicating accuracy (1=not accurate, 5=highly accurate)

#### Optional Fields

- `is_helpful`: Boolean indicating if the recommendation was helpful
- `feedback_text`: String containing detailed feedback
- `action_taken`: String indicating what action the user took on the recommendation (viewed_details, applied, saved, dismissed, etc.)

#### Response

```json
{
  "status": "success",
  "message": "Feedback submitted successfully",
  "feedback_id": "feedback_a1b2c3d4",
  "timestamp": "2023-10-15T14:32:17.123456"
}
```

### 2. Get Recommendation Feedback Summary

```
GET /recommendations/feedback/summary
```

This endpoint provides aggregate statistics on recommendation feedback, including average scores, common actions, and feedback trends.

#### Query Parameters

- `recommendation_type` (string, default: "all"): Type of recommendations to analyze
  - Options: "job", "candidate", "project", "skill", "career_path", "all"
- `period` (string, default: "last_30_days"): Time period for the metrics
  - Options: "last_7_days", "last_30_days", "last_90_days", "all_time"

#### Response

The response varies based on the user type (employer or candidate) and the recommendation type requested.

##### Employer Response Example

```json
{
  "total_feedback_count": 120,
  "average_scores": {
    "relevance": 4.2,
    "accuracy": 4.0,
    "overall": 4.1
  },
  "helpful_percentage": 0.85,
  "action_breakdown": {
    "viewed_details": 0.65,
    "contacted": 0.30,
    "saved": 0.25,
    "dismissed": 0.15
  },
  "common_feedback_themes": [
    {"theme": "Skill match", "percentage": 0.45},
    {"theme": "Experience level", "percentage": 0.35},
    {"theme": "Location", "percentage": 0.25},
    {"theme": "Availability", "percentage": 0.15}
  ],
  "trends": {
    "relevance_trend": [3.8, 3.9, 4.0, 4.1, 4.2],
    "accuracy_trend": [3.7, 3.8, 3.9, 4.0, 4.0],
    "helpful_trend": [0.75, 0.78, 0.80, 0.83, 0.85]
  },
  "candidate_recommendations": {
    "feedback_count": 85,
    "average_scores": {
      "relevance": 4.3,
      "accuracy": 4.1,
      "overall": 4.2
    },
    "helpful_percentage": 0.87,
    "top_feedback_categories": [
      {"category": "Skills match", "percentage": 0.48},
      {"category": "Experience level", "percentage": 0.32},
      {"category": "Location", "percentage": 0.25}
    ]
  },
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
  "total_feedback_count": 95,
  "average_scores": {
    "relevance": 4.1,
    "accuracy": 3.9,
    "overall": 4.0
  },
  "helpful_percentage": 0.82,
  "action_breakdown": {
    "viewed_details": 0.75,
    "applied": 0.22,
    "saved": 0.35,
    "dismissed": 0.18
  },
  "common_feedback_themes": [
    {"theme": "Job relevance", "percentage": 0.42},
    {"theme": "Skill match", "percentage": 0.38},
    {"theme": "Salary range", "percentage": 0.28},
    {"theme": "Location", "percentage": 0.22}
  ],
  "trends": {
    "relevance_trend": [3.7, 3.8, 3.9, 4.0, 4.1],
    "accuracy_trend": [3.6, 3.7, 3.8, 3.8, 3.9],
    "helpful_trend": [0.72, 0.75, 0.78, 0.80, 0.82]
  },
  "job_recommendations": {
    "feedback_count": 65,
    "average_scores": {
      "relevance": 4.2,
      "accuracy": 4.0,
      "overall": 4.1
    },
    "helpful_percentage": 0.84,
    "top_feedback_categories": [
      {"category": "Job title match", "percentage": 0.45},
      {"category": "Salary range", "percentage": 0.35},
      {"category": "Location", "percentage": 0.28}
    ]
  },
  "period": {
    "name": "last_30_days",
    "start_date": "2023-09-15",
    "end_date": "2023-10-15",
    "days": 30
  },
  "recommendation_type": "all"
}
```

## Authentication

All recommendation feedback endpoints require authentication with a valid JWT token.

## Error Handling

### Common Errors

#### Submit Feedback Endpoint

- `400 Bad Request`: Missing required fields or invalid input
  - Example: Missing recommendation_id, invalid recommendation_type, score out of range
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Server-side processing error

#### Feedback Summary Endpoint

- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Server-side processing error

## Feedback Processing

When feedback is submitted, the system performs several actions:

1. Stores the feedback for future analysis
2. Updates user preferences based on feedback patterns
3. Adjusts recommendation algorithms to improve future recommendations
4. Aggregates feedback for reporting and analytics

## Example Usage

### Submit Feedback

```python
import requests

url = "https://api.example.com/recommendations/feedback"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}
payload = {
    "recommendation_id": "job_rec_12345",
    "recommendation_type": "job",
    "relevance_score": 4,
    "accuracy_score": 5,
    "is_helpful": true,
    "feedback_text": "This job recommendation matched my skills well, but the location wasn't ideal.",
    "action_taken": "viewed_details"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
```

### Get Feedback Summary

```python
import requests

url = "https://api.example.com/recommendations/feedback/summary"
headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}
params = {
    "recommendation_type": "job",
    "period": "last_30_days"
}

response = requests.get(url, params=params, headers=headers)
summary = response.json()
```

## Best Practices

1. Always provide accurate relevance and accuracy scores to help improve the recommendation system
2. Include detailed feedback text when recommendations are not relevant or accurate
3. Specify the action taken on the recommendation to help understand user behavior
4. Use the feedback summary endpoint to track improvements in recommendation quality over time 