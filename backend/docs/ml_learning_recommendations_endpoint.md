# ML Learning Recommendations Endpoint

This endpoint provides personalized learning recommendations based on skills, career goals, and timeframes.

## Endpoint

```
GET /ml/learning-recommendations
```

## Authentication

This endpoint requires authentication. Include a valid JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skills` | string | No | - | JSON string or comma-separated list of skills to get recommendations for |
| `career_goal` | string | No | - | Target role to get skill recommendations for (e.g., "Senior Software Engineer") |
| `timeframe` | string | No | `6_months` | Learning timeframe. Valid values: `3_months`, `6_months`, `1_year`, `2_years` |

## Response Format

```json
{
  "resources": [
    {
      "skill": "Python",
      "from_career_goal": true,
      "resources": [
        {
          "title": "Python for Everybody",
          "provider": "Coursera",
          "description": "Learn to program and analyze data with Python.",
          "url": "https://www.coursera.org/specializations/python",
          "duration": "3 months",
          "level": "Beginner"
        },
        {
          "title": "Python Crash Course",
          "provider": "No Starch Press",
          "description": "A hands-on, project-based introduction to programming.",
          "url": "https://nostarch.com/pythoncrashcourse2e",
          "duration": "2 months",
          "level": "Beginner to Intermediate"
        }
      ]
    }
  ],
  "timeframe": "6_months",
  "timeframe_months": 6,
  "career_goal": "Senior Software Engineer",
  "learning_path": {
    "career_goal": "Senior Software Engineer",
    "timeframe_months": 6,
    "phases": [
      {
        "name": "Foundation",
        "duration_months": 1,
        "resources": [
          {
            "skill": "Python",
            "title": "Python for Everybody",
            "provider": "Coursera",
            "duration": "3 months",
            "level": "Beginner",
            "url": "https://www.coursera.org/specializations/python"
          }
        ]
      },
      {
        "name": "Core Skills",
        "duration_months": 2,
        "resources": [
          {
            "skill": "System Design",
            "title": "System Design Interview",
            "provider": "Alex Xu",
            "duration": "2 months",
            "level": "Intermediate to Advanced",
            "url": "https://www.amazon.com/System-Design-Interview-insiders-Second/dp/B08CMF2CQF"
          }
        ]
      },
      {
        "name": "Advanced Topics",
        "duration_months": 3,
        "resources": [
          {
            "skill": "Architecture",
            "title": "Clean Architecture",
            "provider": "Robert C. Martin",
            "duration": "2 months",
            "level": "Advanced",
            "url": "https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164"
          }
        ]
      }
    ]
  }
}
```

### Resource Object

Each item in the `resources` array contains:

| Field | Type | Description |
|-------|------|-------------|
| `skill` | string | The skill name |
| `from_career_goal` | boolean | Whether this skill is derived from the career goal |
| `resources` | array | List of learning resources for this skill |

### Learning Resource

Each item in a skill's `resources` array contains:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | The title of the resource |
| `provider` | string | The provider of the resource (e.g., Coursera, Udemy) |
| `description` | string | A brief description of the resource |
| `url` | string | The URL to access the resource |
| `duration` | string | Estimated time to complete the resource |
| `level` | string | Difficulty level of the resource |

### Learning Path

The `learning_path` object contains:

| Field | Type | Description |
|-------|------|-------------|
| `career_goal` | string | The specified career goal |
| `timeframe_months` | integer | The timeframe in months |
| `phases` | array | Learning phases organized by priority and difficulty |

### Learning Phase

Each item in the `phases` array contains:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The name of the learning phase |
| `duration_months` | number | The duration of the phase in months |
| `resources` | array | List of learning resources for this phase |

## Examples

### Basic Request (Skills Only)

```
GET /ml/learning-recommendations?skills=["Python","JavaScript","React"]
```

### Career Goal Request

```
GET /ml/learning-recommendations?career_goal=Senior%20Software%20Engineer&timeframe=1_year
```

## Behavior

1. **Skills Parameter**: If provided, returns learning resources for the specified skills.
2. **Career Goal Parameter**: If provided, identifies skills needed for that career goal and returns learning resources.
3. **Timeframe Parameter**: Filters resources to those that can be completed within the specified timeframe.
4. **Learning Path**: When a career goal is specified, organizes resources into a structured learning path with phases.
5. **Fallback**: If no parameters are provided, uses the candidate's profile to identify skill gaps and recommend resources.

## Supported Career Goals

- Senior Software Engineer
- Data Scientist
- DevOps Engineer
- Frontend Engineer
- Backend Engineer
- Full Stack Engineer

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 401 | Unauthorized - Authentication token is missing or invalid |
| 400 | Bad Request - Invalid parameter format |
| 500 | Internal Server Error - Server-side error occurred | 