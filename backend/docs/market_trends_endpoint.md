# Market Trends Endpoint

This endpoint provides ML-based predictions for market trends related to specific skill categories over different timeframes.

## Endpoint

```
GET /ml/market-trends
```

## Authentication

This endpoint requires authentication. Include a valid JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `timeframe` | string | No | `6_months` | The timeframe for the predictions. Valid values: `3_months`, `6_months`, `1_year`, `2_years`, `5_years` |
| `skill_category` | string | No | `software_development` | The skill category to analyze. See supported categories below. |
| `include_details` | boolean | No | `true` | Whether to include detailed information about each trend. |

## Supported Skill Categories

- `software_development` - Programming languages and software engineering skills
- `data_science` - Data analysis, machine learning, and statistical skills
- `cloud_computing` - Cloud platforms, services, and infrastructure skills
- `cybersecurity` - Security, encryption, and threat protection skills
- `devops` - Development operations, CI/CD, and infrastructure automation
- `mobile_development` - Mobile app development for iOS and Android
- `web_development` - Frontend and backend web development
- `artificial_intelligence` - AI, machine learning, and related technologies
- `blockchain` - Blockchain, cryptocurrency, and distributed ledger technologies
- `iot` - Internet of Things and connected device technologies
- `ar_vr` - Augmented reality and virtual reality
- `ui_ux` - User interface and user experience design
- `project_management` - Project planning, execution, and team management
- `business_analysis` - Business requirements and process analysis
- `product_management` - Product development and lifecycle management

## Response Format

```json
{
  "timeframe": "6_months",
  "skill_category": "software_development",
  "trends": [
    {
      "skill": "Python",
      "current_demand": 85,
      "projected_demand": 92,
      "growth_rate": 8.2,
      "confidence": 0.87,
      "details": {
        "salary_data": {
          "current_avg": "$120,000",
          "projected_avg": "$130,000",
          "growth_percentage": 8.3
        },
        "industry_relevance": {
          "Technology": 0.92,
          "Finance": 0.85,
          "Healthcare": 0.78,
          "Retail": 0.65,
          "Manufacturing": 0.58,
          "Media": 0.72
        },
        "role_relevance": {
          "Junior Developer": 0.85,
          "Senior Developer": 0.92,
          "Architect": 0.78,
          "Team Lead": 0.82,
          "Manager": 0.68
        },
        "learning_curve": "Moderate",
        "complementary_skills": ["SQL", "JavaScript", "Docker"],
        "market_factors": [
          "Increasing adoption in enterprise"
        ]
      }
    },
    {
      "skill": "JavaScript",
      "current_demand": 82,
      "projected_demand": 88,
      "growth_rate": 7.3,
      "confidence": 0.85
    }
    // Additional trends...
  ],
  "metadata": {
    "analysis_timestamp": "2023-10-15T14:32:17.123456",
    "confidence_score": 0.85,
    "data_sources": ["job_postings", "industry_reports", "hiring_patterns", "skill_demand_metrics"],
    "prediction_model": "market_trend_predictor_v1.2"
  }
}
```

## Response Fields

### Top Level

| Field | Type | Description |
|-------|------|-------------|
| `timeframe` | string | The timeframe used for the predictions |
| `skill_category` | string | The skill category analyzed |
| `trends` | array | List of skill trends sorted by projected demand (descending) |
| `metadata` | object | Information about the analysis process |

### Trends

Each trend in the `trends` array contains:

| Field | Type | Description |
|-------|------|-------------|
| `skill` | string | The name of the skill |
| `current_demand` | integer | Current demand score (0-100) |
| `projected_demand` | integer | Projected demand score at the end of the timeframe (0-100) |
| `growth_rate` | number | Projected growth rate as a percentage |
| `confidence` | number | Confidence score for this prediction (0.0-1.0) |
| `details` | object | (Optional) Detailed information about this skill trend |

### Details (when include_details=true)

| Field | Type | Description |
|-------|------|-------------|
| `salary_data` | object | Salary information for roles requiring this skill |
| `industry_relevance` | object | Relevance scores by industry (0.0-1.0) |
| `role_relevance` | object | Relevance scores by job role (0.0-1.0) |
| `learning_curve` | string | Difficulty of learning this skill ("Steep", "Moderate", or "Gradual") |
| `complementary_skills` | array | Skills that pair well with this skill |
| `market_factors` | array | Factors driving demand for this skill |

### Metadata

| Field | Type | Description |
|-------|------|-------------|
| `analysis_timestamp` | string | When the analysis was performed (ISO format) |
| `confidence_score` | number | Overall confidence in the analysis (0.0-1.0) |
| `data_sources` | array | Data sources used for the analysis |
| `prediction_model` | string | The model version used for predictions |

## Examples

### Basic Request

```
GET /ml/market-trends
```

### Request with Parameters

```
GET /ml/market-trends?timeframe=1_year&skill_category=data_science&include_details=true
```

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid parameters (e.g., unsupported timeframe or skill category) |
| 401 | Unauthorized (missing or invalid token) |
| 500 | Server error |

## Testing

You can test this endpoint using the `test_market_trends.py` script in the `backend/tests` directory:

```
python test_market_trends.py
```

## Use Cases

1. **Career Planning**: Help users identify high-growth skills to focus on for career advancement
2. **Hiring Strategy**: Guide employers in understanding future skill demands for strategic hiring
3. **Curriculum Development**: Assist educational institutions in developing relevant training programs
4. **Workforce Planning**: Support organizations in planning for future skill needs
5. **Salary Negotiations**: Provide data-backed insights for salary discussions based on skill demand 