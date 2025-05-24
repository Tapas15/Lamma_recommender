# Career Paths Endpoint Documentation

## Overview

The Career Paths endpoint provides personalized career progression recommendations for candidates based on their current role, industry, and other parameters. It offers detailed information about potential career paths, including skill requirements, salary data, and step-by-step progression timelines.

## Endpoint Details

- **URL**: `/recommendations/career-paths`
- **Method**: `GET`
- **Authentication**: Required (JWT token)
- **Authorization**: Candidate users only

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `current_role` | string | No | Inferred from profile | The candidate's current job role |
| `industry` | string | No | Inferred from profile | The industry sector of interest |
| `timeframe_years` | integer | No | 5 | Number of years to plan for career progression |
| `include_skill_requirements` | boolean | No | true | Whether to include detailed skill requirements |
| `include_salary_data` | boolean | No | true | Whether to include salary information |

## Response Format

```json
{
  "paths": [
    {
      "name": "Technical Leadership Track",
      "description": "Progress from Software Engineer to Technical Leadership roles",
      "average_time_years": 6,
      "salary_growth_percentage": 75,
      "difficulty": 7,
      "steps": [
        {
          "role": "Software Engineer",
          "timeline": "0-2 years",
          "description": "Build strong programming fundamentals and contribute to team projects",
          "skills": ["Programming", "Data Structures", "Algorithms", "Testing"],
          "skill_requirements": {
            "technical": ["JavaScript", "Python", "SQL", "Git"],
            "soft": ["Communication", "Problem Solving", "Teamwork"]
          },
          "responsibilities": ["Implement features", "Fix bugs", "Write tests", "Participate in code reviews"],
          "salary_data": {
            "median": 90000,
            "range": {"min": 75000, "max": 110000},
            "currency": "USD"
          }
        },
        {
          "role": "Senior Software Engineer",
          "timeline": "2-4 years",
          "description": "Lead projects and mentor junior engineers",
          "skills": ["System Design", "Technical Leadership", "Mentoring", "Architecture"],
          "skill_requirements": {
            "technical": ["Advanced Programming", "System Design", "Architecture Patterns", "CI/CD"],
            "soft": ["Mentoring", "Project Planning", "Technical Communication"]
          },
          "responsibilities": ["Design systems", "Lead projects", "Mentor junior engineers", "Improve development processes"],
          "salary_data": {
            "median": 130000,
            "range": {"min": 110000, "max": 160000},
            "currency": "USD"
          }
        }
      ]
    }
  ]
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `paths` | array | List of career paths available for the candidate |
| `paths[].name` | string | Name of the career path |
| `paths[].description` | string | Description of the career path |
| `paths[].average_time_years` | integer | Average time to complete the career path in years |
| `paths[].salary_growth_percentage` | integer | Expected salary growth percentage from start to end of path |
| `paths[].difficulty` | integer | Difficulty rating of the path (1-10) |
| `paths[].steps` | array | List of career steps in the path |
| `paths[].steps[].role` | string | Job title for this career step |
| `paths[].steps[].timeline` | string | Expected timeline for this step (e.g., "2-4 years") |
| `paths[].steps[].description` | string | Description of the role and responsibilities |
| `paths[].steps[].skills` | array | Key skills for this role |
| `paths[].steps[].skill_requirements` | object | Detailed skill requirements by category (only if `include_skill_requirements=true`) |
| `paths[].steps[].responsibilities` | array | Key responsibilities for this role |
| `paths[].steps[].salary_data` | object | Salary information for this role (only if `include_salary_data=true`) |

## Skill Categories

The endpoint categorizes skills into the following types:

- **Technical**: Programming languages, frameworks, tools, etc.
- **Soft**: Communication, leadership, teamwork, etc.
- **Domain**: Industry-specific knowledge and skills

## Salary Data

When `include_salary_data=true`, the endpoint includes the following salary information for each role:

- **Median**: The median salary for the role
- **Range**: The typical salary range (min and max)
- **Currency**: The currency of the salary data (default: USD)

## Timeframe Filtering

When `timeframe_years` is specified, the endpoint filters the career steps to only include those that can be achieved within the specified timeframe. This helps candidates plan their career progression based on their desired timeline.

## Supported Roles and Industries

The endpoint currently supports the following roles and industries:

### Roles
- Software Engineer
- Data Scientist
- Product Manager

### Industries
- Technology
- Finance
- Healthcare

## Example Usage

```
GET /recommendations/career-paths?current_role=Software%20Engineer&industry=Finance&timeframe_years=3&include_salary_data=true
```

## Testing

You can test this endpoint using the `test_career_paths.py` script in the `backend/utils` directory:

```
python test_career_paths.py
``` 