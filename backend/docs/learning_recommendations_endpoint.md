# Learning Recommendations Endpoint

This endpoint provides personalized learning recommendations based on skills, career goals, and timeframes.

## Endpoint

```
GET /recommendations/learning
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
      ],
      "from_career_goal": true
    },
    {
      "skill": "System Design",
      "resources": [
        {
          "title": "System Design Interview",
          "provider": "ByteByteGo",
          "description": "An insider's guide to system design interviews.",
          "url": "https://bytebytego.com/",
          "duration": "2 months",
          "level": "Intermediate to Advanced"
        }
      ],
      "from_career_goal": true
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
        "name": "Phase 1: Foundation",
        "duration_months": 3,
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
        "name": "Phase 2: Intermediate",
        "duration_months": 2,
        "resources": [
          {
            "skill": "System Design",
            "title": "System Design Interview",
            "provider": "ByteByteGo",
            "duration": "2 months",
            "level": "Intermediate to Advanced",
            "url": "https://bytebytego.com/"
          }
        ]
      }
    ]
  }
}
```

## Response Fields

### Top Level

| Field | Type | Description |
|-------|------|-------------|
| `resources` | array | List of skill resources |
| `timeframe` | string | The timeframe used for recommendations |
| `timeframe_months` | integer | The timeframe in months |
| `career_goal` | string | (Optional) The career goal if specified |
| `learning_path` | object | (Optional) Structured learning path if career goal is specified |

### Resources

Each item in the `resources` array contains:

| Field | Type | Description |
|-------|------|-------------|
| `skill` | string | The name of the skill |
| `resources` | array | List of learning resources for this skill |
| `from_career_goal` | boolean | Whether this skill is related to the specified career goal |

### Learning Resource

Each item in the `resources` array of a skill contains:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | The title of the learning resource |
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
GET /recommendations/learning?skills=["Python","JavaScript","React"]
```

### Career Goal Request

```
GET /recommendations/learning?career_goal=Senior%20Software%20Engineer&timeframe=1_year
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
- Engineering Manager

## Testing

You can test this endpoint using the `test_learning_recommendations.py` script in the `backend/tests` directory:

```
python test_learning_recommendations.py
```

## Use Cases

1. **Career Advancement**: Help users plan their learning journey to reach specific career goals
2. **Skill Development**: Provide targeted resources for specific skills
3. **Time-Bound Learning**: Create learning plans that fit within specific timeframes
4. **Personalized Learning**: Generate recommendations based on user profiles and skill gaps 