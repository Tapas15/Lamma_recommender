"""
Test configuration for the Job Recommender System test suite.
Contains shared configuration, test data, and utility functions.
"""
import os
import random
import uuid
import datetime
from typing import Dict, List, Any

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
STREAMLIT_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")

# Test user credentials
TEST_USERS = {
    "employer1": {
        "email": f"employer_{uuid.uuid4().hex[:8]}@example.com",
        "password": "test_password123",
        "type": "employer"
    },
    "employer2": {
        "email": f"employer2_{uuid.uuid4().hex[:8]}@example.com",
        "password": "test_password123",
        "type": "employer"
    },
    "candidate1": {
        "email": f"candidate_{uuid.uuid4().hex[:8]}@example.com",
        "password": "test_password123",
        "type": "candidate"
    },
    "candidate2": {
        "email": f"candidate2_{uuid.uuid4().hex[:8]}@example.com",
        "password": "test_password123",
        "type": "candidate"
    }
}

# Test data generation
def generate_job_data(company_name: str = None, employer_id: str = None) -> Dict[str, Any]:
    """Generate test job data"""
    job_titles = [
        "Senior Software Engineer", "Data Scientist", "UI/UX Designer",
        "Product Manager", "DevOps Engineer", "Full Stack Developer",
        "Machine Learning Engineer", "Backend Developer", "Frontend Developer"
    ]
    
    locations = ["Remote", "New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA"]
    
    tech_stacks = [
        ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
        ["JavaScript", "React", "Node.js", "MongoDB", "GraphQL"],
        ["Java", "Spring Boot", "MySQL", "Kubernetes", "GCP"],
        ["Python", "FastAPI", "MongoDB", "Docker", "Azure"],
        ["TypeScript", "Angular", "Express", "Redis", "AWS"]
    ]
    
    benefits = [
        ["Health insurance", "401k matching", "Unlimited PTO", "Remote work option"],
        ["Health insurance", "Retirement plan", "Paid parental leave", "Stock options"],
        ["Medical benefits", "Dental and vision", "Flexible hours", "Learning budget"],
        ["Comprehensive healthcare", "Gym membership", "Free lunch", "Home office stipend"]
    ]
    
    if not company_name:
        companies = ["Tech Innovations Inc.", "DataSphere", "CodeCraft Solutions", "Quantum Software", "EvoTech"]
        company_name = random.choice(companies)
    
    job_title = random.choice(job_titles)
    
    # Create salary range as string instead of dict based on API requirements
    min_salary = random.randint(80000, 120000)
    max_salary = random.randint(130000, 180000)
    salary_range = f"${min_salary} - ${max_salary}"
    
    job_data = {
        "title": job_title,
        "company": company_name,
        "description": f"We are looking for a {job_title} to join our team and help us build innovative solutions.",
        "requirements": random.sample(["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes", "FastAPI", "MongoDB", "SQL", "Git", "CI/CD", "Agile"], 4),
        "location": random.choice(locations),
        "employment_type": random.choice(["Full-time", "Part-time", "Contract"]),
        "experience_level": random.choice(["Entry", "Mid", "Senior"]),
        "industry": "Technology",
        "responsibilities": [
            "Design and develop high-quality software",
            "Collaborate with cross-functional teams",
            "Participate in code reviews",
            f"Build and maintain {random.choice(['web applications', 'APIs', 'microservices', 'data pipelines'])}"
        ],
        "preferred_qualifications": [
            f"Bachelor's degree in {random.choice(['Computer Science', 'Information Technology', 'Software Engineering'])}",
            f"{random.randint(2, 8)}+ years of experience"
        ],
        "tech_stack": random.choice(tech_stacks),
        "remote_option": random.choice([True, False]),
        "work_mode": random.choice([["Remote"], ["On-site"], ["Hybrid"], ["Remote", "Hybrid"]]),
        "salary_range": salary_range,  # String format
        "benefits": random.choice(benefits),
        "application_deadline": (datetime.datetime.now() + datetime.timedelta(days=random.randint(14, 45))).isoformat(),
        "posted_date": datetime.datetime.now().isoformat(),
        "contact_email": f"hr@{company_name.lower().replace(' ', '')}.example.com"
    }
    
    # Add employer_id if provided - ensure it's at the top level
    if employer_id:
        job_data["employer_id"] = employer_id
        
    return job_data

def generate_project_data(company_name: str = None, employer_id: str = None) -> Dict[str, Any]:
    """Generate test project data"""
    project_titles = [
        "E-commerce Platform Development", 
        "AI-Powered Recommendation Engine",
        "Mobile App Development",
        "Cloud Migration Project",
        "Data Analytics Dashboard",
        "Blockchain Implementation",
        "IoT Monitoring System",
        "Automated Testing Framework"
    ]
    
    project_types = [
        "Software Development", 
        "Mobile App Development",
        "Web Development",
        "Data Science",
        "DevOps",
        "UI/UX Design"
    ]
    
    tech_stacks = [
        ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
        ["JavaScript", "React", "Node.js", "MongoDB", "GraphQL"],
        ["Java", "Spring Boot", "MySQL", "Kubernetes", "GCP"],
        ["Python", "FastAPI", "MongoDB", "Docker", "Azure"],
        ["TypeScript", "Angular", "Express", "Redis", "AWS"]
    ]
    
    if not company_name:
        companies = ["Tech Innovations Inc.", "DataSphere", "CodeCraft Solutions", "Quantum Software", "EvoTech"]
        company_name = random.choice(companies)
    
    project_title = random.choice(project_titles)
    project_type = random.choice(project_types)
    tech_stack = random.choice(tech_stacks)
    
    # Format budget as string
    min_budget = random.randint(5000, 15000)
    max_budget = random.randint(20000, 50000)
    budget_range = f"${min_budget} - ${max_budget}"
    
    project_data = {
        "title": project_title,
        "company": company_name,
        "description": f"We are looking for talented individuals to help with our {project_title} project.",
        "project_type": project_type,
        "skills_required": random.sample(tech_stack + ["Communication", "Problem Solving", "Teamwork"], 5),
        "requirements": [
            f"{random.randint(1, 5)}+ years of experience in {project_type}",
            f"Experience with {', '.join(random.sample(tech_stack, 2))}",
            "Strong communication skills"
        ],
        "location": random.choice(["Remote", "On-site", "Hybrid"]),
        "budget_range": budget_range,  # String format
        "duration": f"{random.randint(1, 12)} {random.choice(['weeks', 'months'])}",  # String format
        "tools_technologies": tech_stack,
        "objectives": [
            f"Design and develop {project_title.lower()}",
            "Create comprehensive documentation",
            "Implement automated tests",
            "Deploy to production"
        ]
    }
    
    # Add employer_id if provided - ensure it's at the top level
    if employer_id:
        project_data["employer_id"] = employer_id
        
    return project_data

def generate_candidate_profile() -> Dict[str, Any]:
    """Generate test candidate profile data"""
    names = ["Alex Johnson", "Sam Taylor", "Jordan Smith", "Morgan Lee", "Casey Wilson"]
    locations = ["New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA", "Chicago, IL"]
    
    skills = {
        "languages_frameworks": random.sample(["Python", "JavaScript", "Java", "TypeScript", "C#", "React", "Angular", "Vue.js", "Django", "Flask", "FastAPI", "Spring Boot"], 5),
        "tools_platforms": random.sample(["Git", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Jenkins", "CircleCI", "GitHub Actions", "Jira", "Confluence"], 4),
        "ai_ml_data": random.sample(["TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Data Analysis", "SQL", "NoSQL", "ETL", "Big Data"], 3),
        "soft_skills": random.sample(["Communication", "Teamwork", "Problem-solving", "Time Management", "Leadership", "Creativity", "Adaptability"], 4)
    }
    
    # Ensure all date fields are in proper format
    start_year = 2010 + random.randint(0, 8)
    first_job_start = f"{start_year}-{random.randint(1, 12):02d}"
    first_job_end = "Present" if random.choice([True, False]) else f"{start_year + random.randint(1, 5)}-{random.randint(1, 12):02d}"
    
    second_job_start = f"{start_year - random.randint(3, 6)}-{random.randint(1, 12):02d}"
    second_job_end = f"{start_year - random.randint(0, 1)}-{random.randint(1, 12):02d}"
    
    return {
        "full_name": random.choice(names),
        "phone": f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "location": random.choice(locations),
        "experience_years": str(random.randint(1, 15)),
        "education_summary": random.choice(["BS in Computer Science", "MS in Computer Science", "BS in Information Technology", "MS in Data Science", "Self-taught"]),
        "bio": "Software professional with expertise in building scalable applications",
        "about": "Passionate about technology and solving complex problems",
        "skills": skills,
        "experience": [
            {
                "title": random.choice(["Software Engineer", "Senior Developer", "Full Stack Engineer", "Data Scientist"]),
                "company": random.choice(["Tech Corp", "DataSphere", "CodeCraft", "InnovateSoft"]),
                "location": random.choice(locations),
                "start_date": first_job_start,
                "end_date": first_job_end,
                "description": "Developed and maintained web applications using modern technologies"
            },
            {
                "title": random.choice(["Junior Developer", "Software Developer", "Web Developer"]),
                "company": random.choice(["StartupX", "DevStudio", "TechStart", "WebWorks"]),
                "location": random.choice(locations),
                "start_date": second_job_start,
                "end_date": second_job_end,
                "description": "Built and enhanced software products and client projects"
            }
        ],
        "education": [
            {
                "degree": random.choice(["MS in Computer Science", "BS in Computer Science", "BS in Information Technology", "MS in Data Science"]),
                "institution": random.choice(["MIT", "Stanford University", "UC Berkeley", "Georgia Tech", "University of Washington"]),
                "location": random.choice(locations),
                "graduation_year": str(random.randint(2010, 2022))  # String type
            }
        ],
        "preferred_job_locations": random.sample(["Remote", "New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA", "Chicago, IL"], 3)
    }

def generate_employer_profile() -> Dict[str, Any]:
    """Generate test employer profile data"""
    company_names = ["TechNova", "DataPulse", "CodeSphere", "CloudEdge", "QuantumBit"]
    locations = ["New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA", "Chicago, IL"]
    
    company_name = random.choice(company_names)
    
    return {
        "full_name": f"{random.choice(['John', 'Sarah', 'Michael', 'Emily', 'David'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown'])}",
        "position": random.choice(["HR Manager", "Talent Acquisition Specialist", "Recruiter", "CEO", "CTO"]),
        "bio": f"Hiring manager at {company_name}, looking for top talent to join our team",
        "contact_email": f"hr@{company_name.lower().replace(' ', '')}.example.com",
        "location": random.choice(locations),
        "company_details": {
            "company_name": company_name,
            "company_description": f"{company_name} is a technology company focused on building innovative solutions for our clients",
            "company_website": f"https://{company_name.lower().replace(' ', '')}.example.com",
            "company_location": random.choice(locations),
            "company_size": random.choice(["1-10 employees", "11-50 employees", "51-200 employees", "201-500 employees", "501+ employees"]),
            "industry": random.choice(["Technology", "Software", "IT Services", "FinTech", "EdTech", "HealthTech"]),
            "founded_year": random.randint(2000, 2020),
        },
        "hiring_preferences": {
            "job_roles_hiring": random.sample(["Software Engineer", "Data Scientist", "DevOps Engineer", "Product Manager", "UX Designer", "Full Stack Developer"], 3),
            "employment_types": random.sample(["Full-time", "Part-time", "Contract"], 2),
            "locations_hiring": random.sample(["Remote", "New York, NY", "San Francisco, CA", "Austin, TX"], 2),
            "remote_friendly": random.choice([True, False]),
            "tech_stack": random.sample(["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes"], 4)
        }
    }

# Application data
def generate_job_application(job_id: str) -> Dict[str, Any]:
    """Generate test job application data"""
    return {
        "job_id": job_id,
        "cover_letter": "I am excited to apply for this position and believe my skills align well with your requirements.",
        "resume_url": "https://example.com/resume.pdf",
        "notes": "Available to start immediately"
    }

def generate_project_application(project_id: str) -> Dict[str, Any]:
    """Generate test project application data"""
    return {
        "project_id": project_id,
        "cover_letter": "I am interested in working on this project and have relevant experience with the required technologies.",
        "resume_url": "https://example.com/resume.pdf",
        "notes": "Available for 20+ hours per week",
        "availability": random.choice(["Full-time", "Part-time", "Weekends"])
    }

# Test results storage
TEST_RESULTS = {
    "employer": {},
    "candidate": {},
    "jobs": [],
    "projects": [],
    "applications": [],
    "saved": []
} 