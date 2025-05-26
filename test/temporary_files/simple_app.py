from fastapi import FastAPI, HTTPException
import json
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ml/learning-recommendations", response_model=dict)
async def get_ml_learning_recommendations(
    skills: str = None,
    career_goal: str = None,
    timeframe: str = "6_months"
):
    """
    Get learning recommendations based on skills, career goal, and timeframe.
    This endpoint provides personalized learning recommendations for candidates.
    
    - **skills**: JSON string or comma-separated list of skills to get recommendations for
    - **career_goal**: Target role to get skill recommendations for (e.g., "Senior Software Engineer")
    - **timeframe**: Learning timeframe (3_months, 6_months, 1_year, 2_years)
    """
    # Convert timeframe to months for calculations
    timeframe_months = {
        "3_months": 3,
        "6_months": 6,
        "1_year": 12,
        "2_years": 24
    }.get(timeframe, 6)
    
    # Parse skills if provided
    parsed_skills = []
    if skills:
        try:
            # Try to parse as JSON
            parsed_skills = json.loads(skills)
        except json.JSONDecodeError:
            # If not JSON, treat as comma-separated list
            parsed_skills = [s.strip() for s in skills.split(",")]
    
    # Define career goals and their required skills
    career_goals = {
        "Senior Software Engineer": [
            "System Design", "Architecture", "Leadership", 
            "Advanced Algorithms", "Code Review", "Mentoring", 
            "Performance Optimization", "Scalability"
        ],
        "Data Scientist": [
            "Machine Learning", "Statistics", "Python", 
            "Data Visualization", "SQL", "Big Data", 
            "Data Cleaning", "Experimental Design"
        ],
        "DevOps Engineer": [
            "CI/CD", "Docker", "Kubernetes", "Cloud Platforms", 
            "Infrastructure as Code", "Monitoring", "Automation"
        ],
        "Frontend Engineer": [
            "React", "JavaScript", "TypeScript", "CSS", 
            "Responsive Design", "Web Performance", "Accessibility"
        ],
        "Backend Engineer": [
            "API Design", "Database Design", "Caching", 
            "Microservices", "Security", "Scalability"
        ],
        "Full Stack Engineer": [
            "Frontend Frameworks", "Backend Development", 
            "Database Design", "API Design", "DevOps", 
            "System Architecture"
        ]
    }
    
    # Get skills for career goal if provided
    career_goal_skills = []
    if career_goal and career_goal in career_goals:
        career_goal_skills = career_goals[career_goal]
        
        # Add career goal skills to the list if not already present
        for skill in career_goal_skills:
            if skill not in parsed_skills:
                parsed_skills.append(skill)
    
    # Define learning resources for common skills
    # In a real system, this would come from a database or external API
    learning_resources = {
        "Python": [
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
        "JavaScript": [
            {
                "title": "JavaScript: The Definitive Guide",
                "provider": "O'Reilly",
                "description": "Comprehensive guide to JavaScript programming.",
                "url": "https://www.oreilly.com/library/view/javascript-the-definitive/9781491952016/",
                "duration": "3 months",
                "level": "Beginner to Advanced"
            },
            {
                "title": "Modern JavaScript Tutorial",
                "provider": "JavaScript.info",
                "description": "Modern JavaScript tutorial from the basics to advanced topics.",
                "url": "https://javascript.info/",
                "duration": "2 months",
                "level": "Beginner to Intermediate"
            }
        ],
        "React": [
            {
                "title": "React - The Complete Guide",
                "provider": "Udemy",
                "description": "Dive in and learn React from scratch.",
                "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
                "duration": "2 months",
                "level": "Beginner to Advanced"
            },
            {
                "title": "React Documentation",
                "provider": "React.dev",
                "description": "Official React documentation and tutorials.",
                "url": "https://react.dev/learn",
                "duration": "1 month",
                "level": "Beginner to Intermediate"
            }
        ],
        "System Design": [
            {
                "title": "System Design Interview",
                "provider": "Alex Xu",
                "description": "An insider's guide to system design interviews.",
                "url": "https://www.amazon.com/System-Design-Interview-insiders-Second/dp/B08CMF2CQF",
                "duration": "2 months",
                "level": "Intermediate to Advanced"
            }
        ],
        "Architecture": [
            {
                "title": "Clean Architecture",
                "provider": "Robert C. Martin",
                "description": "A craftsman's guide to software structure and design.",
                "url": "https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164",
                "duration": "2 months",
                "level": "Advanced"
            }
        ],
        "Leadership": [
            {
                "title": "The Manager's Path",
                "provider": "O'Reilly",
                "description": "A guide for tech leaders navigating growth and change.",
                "url": "https://www.oreilly.com/library/view/the-managers-path/9781491973882/",
                "duration": "1 month",
                "level": "Intermediate to Advanced"
            }
        ]
    }
    
    # Prepare resources for response
    resources = []
    for skill in parsed_skills:
        if skill in learning_resources:
            # Check if this is a career goal skill
            from_career_goal = skill in career_goal_skills
            
            resources.append({
                "skill": skill,
                "from_career_goal": from_career_goal,
                "resources": learning_resources[skill]
            })
    
    # Helper function to create a learning path
    def create_learning_path(career_goal, timeframe_months, resources):
        """Create a structured learning path for the given career goal and timeframe"""
        # Define phases based on timeframe
        if timeframe_months <= 3:
            phases = [
                {"name": "Foundation", "duration_months": 1},
                {"name": "Core Skills", "duration_months": 2}
            ]
        elif timeframe_months <= 6:
            phases = [
                {"name": "Foundation", "duration_months": 1},
                {"name": "Core Skills", "duration_months": 2},
                {"name": "Advanced Topics", "duration_months": 3}
            ]
        elif timeframe_months <= 12:
            phases = [
                {"name": "Foundation", "duration_months": 2},
                {"name": "Core Skills", "duration_months": 4},
                {"name": "Advanced Topics", "duration_months": 3},
                {"name": "Specialization", "duration_months": 3}
            ]
        else:  # 2 years
            phases = [
                {"name": "Foundation", "duration_months": 3},
                {"name": "Core Skills", "duration_months": 6},
                {"name": "Advanced Topics", "duration_months": 6},
                {"name": "Specialization", "duration_months": 6},
                {"name": "Leadership & Architecture", "duration_months": 3}
            ]
        
        # Distribute resources across phases
        career_resources = []
        for resource_group in resources:
            if resource_group.get("from_career_goal", False):
                for resource in resource_group.get("resources", []):
                    career_resources.append({
                        "skill": resource_group.get("skill"),
                        "title": resource.get("title"),
                        "provider": resource.get("provider"),
                        "duration": resource.get("duration"),
                        "level": resource.get("level", "Intermediate"),
                        "url": resource.get("url")
                    })
        
        # Sort resources by level
        level_order = {"Beginner": 0, "Beginner to Intermediate": 1, "Intermediate": 2, 
                      "Intermediate to Advanced": 3, "Advanced": 4}
        career_resources.sort(key=lambda x: level_order.get(x.get("level", "Intermediate"), 2))
        
        # Distribute resources to phases
        resources_per_phase = len(career_resources) // len(phases)
        if resources_per_phase == 0:
            resources_per_phase = 1
        
        for i, phase in enumerate(phases):
            start_idx = i * resources_per_phase
            end_idx = (i + 1) * resources_per_phase if i < len(phases) - 1 else len(career_resources)
            phase["resources"] = career_resources[start_idx:end_idx] if start_idx < len(career_resources) else []
        
        return {
            "career_goal": career_goal,
            "timeframe_months": timeframe_months,
            "phases": phases
        }
    
    # Create learning path if career goal is provided
    learning_path = None
    if career_goal:
        learning_path = create_learning_path(career_goal, timeframe_months, resources)
    
    response = {
        "resources": resources,
        "timeframe": timeframe,
        "timeframe_months": timeframe_months
    }
    
    # Add career goal information if provided
    if career_goal:
        response["career_goal"] = career_goal
        response["learning_path"] = learning_path
    
    return response

if __name__ == "__main__":
    print("Starting FastAPI server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000) 