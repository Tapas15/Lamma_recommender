# Improved Skill Gap Analysis Endpoint

## Overview

The improved skill gap analysis endpoint provides comprehensive information about the gap between a candidate's current skills and the skills required for a target role in a specific industry. It includes industry-specific skill requirements, categorized missing skills, market demand data, and optional learning resources.

## Endpoint Details

- **URL**: `/recommendations/skill-gap`
- **Method**: `GET`
- **Authentication**: Required (JWT token)
- **Authorization**: Candidate users only

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target_role` | string | Yes | - | The target job role (e.g., "Software Engineer", "Data Scientist") |
| `industry` | string | No | "Technology" | The industry sector (e.g., "Technology", "Finance", "Healthcare") |
| `experience_level` | string | No | "Mid-level" | The experience level ("Entry-level", "Mid-level", "Senior", "Lead") |
| `include_learning_resources` | boolean | No | false | Whether to include learning resources for missing skills |

## Response Format

```json
{
  "match_score": 75,
  "your_skills": [
    { "name": "Python", "proficiency": 8 },
    { "name": "React", "proficiency": 7 }
  ],
  "required_skills": [
    { "name": "Python", "importance": 9 },
    { "name": "JavaScript", "importance": 8 }
  ],
  "missing_skills": [
    { "name": "JavaScript", "importance": 8 }
  ],
  "categorized_missing_skills": {
    "technical": [
      { "name": "JavaScript", "importance": 8 }
    ],
    "soft_skills": [],
    "domain_knowledge": [],
    "architecture": []
  },
  "industry_specific_requirements": [
    { "name": "Agile Methodologies", "importance": 8 }
  ],
  "market_demand": {
    "demand_score": 85,
    "growth_rate": 22,
    "avg_salary": "$110,000"
  },
  "learning_resources": {
    "resources": [
      {
        "skill": "JavaScript",
        "resources": [
          {
            "title": "JavaScript: The Definitive Guide",
            "provider": "O'Reilly",
            "description": "Comprehensive guide to JavaScript programming.",
            "url": "https://www.oreilly.com/library/view/javascript-the-definitive/9781491952016/"
          }
        ]
      }
    ]
  }
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `match_score` | integer | The match percentage (0-100) between candidate skills and required skills |
| `your_skills` | array | List of candidate's skills with proficiency levels |
| `required_skills` | array | List of skills required for the target role with importance levels |
| `missing_skills` | array | List of required skills that the candidate is missing |
| `categorized_missing_skills` | object | Missing skills categorized by type (technical, soft_skills, domain_knowledge, architecture) |
| `industry_specific_requirements` | array | Industry-specific skill requirements for the target role |
| `market_demand` | object | Market demand data for the target role in the specified industry |
| `learning_resources` | object | Learning resources for the top missing skills (only if `include_learning_resources=true`) |

## Skill Categories

The endpoint categorizes missing skills into the following categories:

- **Technical**: Programming languages, frameworks, databases, etc.
- **Soft Skills**: Communication, leadership, teamwork, etc.
- **Domain Knowledge**: Industry-specific knowledge and regulations
- **Architecture**: System design, architecture patterns, etc.

## Market Demand Data

The market demand data includes:

- **Demand Score**: A score from 0-100 indicating the demand for the role
- **Growth Rate**: The year-over-year growth rate as a percentage
- **Average Salary**: The average salary for the role in the industry

## Learning Resources

When `include_learning_resources=true`, the endpoint includes learning resources for the top 5 most important missing skills. Each resource includes:

- **Title**: The title of the learning resource
- **Provider**: The provider of the resource (e.g., Coursera, Udemy)
- **Description**: A brief description of the resource
- **URL**: The URL to access the resource

## Industry Support

The endpoint currently supports the following industries:

- Technology
- Finance
- Healthcare

## Experience Levels

The endpoint supports the following experience levels:

- **Entry-level**: Reduces the importance of required skills
- **Mid-level**: Standard importance levels
- **Senior**: Increases the importance of required skills
- **Lead**: Further increases the importance of required skills

## Example Usage

```
GET /recommendations/skill-gap?target_role=Software%20Engineer&industry=Technology&include_learning_resources=true
```

## Testing

You can test this endpoint using the `test_skill_gap.py` script in the `backend/utils` directory.

```
python test_skill_gap.py
``` 