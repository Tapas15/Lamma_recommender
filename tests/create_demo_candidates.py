#!/usr/bin/env python
"""
Test script to create demo candidate accounts for testing purposes.
This script will create a specified number of candidate accounts with realistic data.

Usage:
    python create_demo_candidates.py [--count N]
    
    --count N: Number of candidate accounts to create (default: 10)
"""

import os
import sys
import json
import random
import argparse
import requests
from datetime import datetime, timedelta
from faker import Faker

# Add the parent directory to the path so we can import from utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
API_BASE_URL = "http://localhost:8000"
fake = Faker()

# Tech skills data
PROGRAMMING_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C#", "C++", "Go", "Rust",
    "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB"
]

FRAMEWORKS = [
    "React", "Angular", "Vue.js", "Django", "Flask", "FastAPI", "Spring Boot",
    "Express.js", "Next.js", "ASP.NET Core", "Laravel", "Ruby on Rails",
    "TensorFlow", "PyTorch", "Pandas", "NumPy", "Node.js", "Bootstrap", "Tailwind CSS"
]

DATABASES = [
    "MongoDB", "PostgreSQL", "MySQL", "SQLite", "Oracle", "SQL Server",
    "Redis", "Elasticsearch", "Cassandra", "DynamoDB", "Firebase"
]

CLOUD_PLATFORMS = [
    "AWS", "Azure", "Google Cloud", "Heroku", "DigitalOcean", "Vercel",
    "Netlify", "Firebase", "Cloudflare"
]

TOOLS = [
    "Git", "Docker", "Kubernetes", "Jenkins", "GitHub Actions", "CircleCI",
    "Terraform", "Ansible", "Prometheus", "Grafana", "Jira", "Confluence"
]

SOFT_SKILLS = [
    "Communication", "Teamwork", "Problem Solving", "Critical Thinking",
    "Adaptability", "Time Management", "Leadership", "Creativity",
    "Emotional Intelligence", "Conflict Resolution", "Negotiation",
    "Presentation Skills", "Customer Service", "Mentoring"
]

AI_ML_DATA = [
    "Machine Learning", "Deep Learning", "Natural Language Processing",
    "Computer Vision", "Data Analysis", "Data Visualization", "Big Data",
    "Data Mining", "Statistical Analysis", "Predictive Modeling",
    "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "NLTK", "spaCy",
    "Hadoop", "Spark", "Tableau", "Power BI"
]

EDUCATION_DEGREES = [
    "Bachelor of Science in Computer Science",
    "Bachelor of Engineering in Computer Engineering",
    "Bachelor of Science in Information Technology",
    "Bachelor of Science in Data Science",
    "Bachelor of Science in Software Engineering",
    "Master of Science in Computer Science",
    "Master of Science in Data Science",
    "Master of Science in Artificial Intelligence",
    "Master of Business Administration",
    "Ph.D. in Computer Science"
]

UNIVERSITIES = [
    "Stanford University", "Massachusetts Institute of Technology",
    "University of California, Berkeley", "Harvard University",
    "Carnegie Mellon University", "University of Washington",
    "Georgia Institute of Technology", "University of Illinois",
    "University of Michigan", "University of Texas at Austin",
    "California Institute of Technology", "Princeton University",
    "Cornell University", "University of Toronto", "University of Waterloo"
]

JOB_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Full Stack Developer",
    "Frontend Developer", "Backend Developer", "DevOps Engineer",
    "Data Scientist", "Machine Learning Engineer", "AI Researcher",
    "Cloud Architect", "Systems Architect", "Mobile Developer",
    "iOS Developer", "Android Developer", "UI/UX Designer",
    "Product Manager", "Project Manager", "QA Engineer",
    "Database Administrator", "Network Engineer", "Security Engineer"
]

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Apple", "Facebook", "Netflix", "Uber",
    "Airbnb", "Twitter", "LinkedIn", "Salesforce", "Adobe", "IBM", "Intel",
    "Oracle", "SAP", "Cisco", "VMware", "Spotify", "Slack", "Zoom",
    "TechStartup Inc.", "Innovative Solutions", "Digital Dynamics",
    "CodeCrafters", "DataDriven Analytics", "CloudNative Systems",
    "Quantum Computing", "AI Innovations", "Mobile Creations"
]

LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Boston, MA",
    "Austin, TX", "Chicago, IL", "Los Angeles, CA", "Denver, CO",
    "Portland, OR", "Atlanta, GA", "Toronto, Canada", "Vancouver, Canada",
    "London, UK", "Berlin, Germany", "Paris, France", "Amsterdam, Netherlands",
    "Sydney, Australia", "Singapore", "Tokyo, Japan", "Remote"
]

CERTIFICATIONS = [
    "AWS Certified Solutions Architect", "AWS Certified Developer",
    "Microsoft Certified: Azure Developer Associate",
    "Microsoft Certified: Azure Solutions Architect",
    "Google Cloud Professional Cloud Architect",
    "Google Cloud Professional Data Engineer",
    "Certified Kubernetes Administrator (CKA)",
    "Certified Kubernetes Application Developer (CKAD)",
    "Certified Information Systems Security Professional (CISSP)",
    "Certified Ethical Hacker (CEH)",
    "Project Management Professional (PMP)",
    "Scrum Master Certification",
    "Cisco Certified Network Associate (CCNA)",
    "Cisco Certified Network Professional (CCNP)",
    "Oracle Certified Professional (OCP)",
    "MongoDB Certified Developer",
    "TensorFlow Developer Certificate"
]

def generate_candidate_data():
    """Generate realistic candidate data"""
    first_name = fake.first_name()
    last_name = fake.last_name()
    full_name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
    
    # Select random skills
    languages_frameworks = random.sample(PROGRAMMING_LANGUAGES, random.randint(2, 5)) + \
                          random.sample(FRAMEWORKS, random.randint(2, 5))
    ai_ml_data = random.sample(AI_ML_DATA, random.randint(0, 5)) if random.random() > 0.5 else []
    tools_platforms = random.sample(TOOLS, random.randint(2, 5)) + \
                     random.sample(CLOUD_PLATFORMS, random.randint(1, 3)) + \
                     random.sample(DATABASES, random.randint(1, 3))
    soft_skills = random.sample(SOFT_SKILLS, random.randint(3, 6))
    
    # Generate experience (1-15 years)
    experience_years = str(random.randint(1, 15))  # Convert to string as API expects
    
    # Generate work experience
    num_experiences = min(int(experience_years) // 2 + 1, 5)  # More experience years = more job entries
    experiences = []
    current_date = datetime.now()
    
    for i in range(num_experiences):
        is_current = (i == 0)  # Most recent experience is current job
        duration = random.randint(12, 36)  # 1-3 years per job
        
        # Calculate duration in months
        if is_current:
            duration_months = duration
            end_date = "Present"
            start_date = (current_date - timedelta(days=30*duration)).strftime("%Y-%m")
        else:
            duration_months = duration
            end_date = (current_date - timedelta(days=30*(sum(range(i))*duration))).strftime("%Y-%m")
            start_date = (current_date - timedelta(days=30*(sum(range(i+1))*duration))).strftime("%Y-%m")
        
        experiences.append({
            "title": random.choice(JOB_TITLES),
            "company": random.choice(COMPANIES),
            "location": random.choice(LOCATIONS),
            "duration": f"{duration_months} months",
            "responsibilities": [fake.sentence() for _ in range(3)]
        })
    
    # Generate education
    grad_year = current_date.year - int(experience_years) - random.randint(0, 2)
    start_year = grad_year - random.randint(2, 5)  # 2-5 years of education
    education = [{
        "degree": random.choice(EDUCATION_DEGREES),
        "institution": random.choice(UNIVERSITIES),
        "duration": f"{start_year} - {grad_year}"
    }]
    
    # Generate certifications (50% chance of having certifications)
    certifications = []
    if random.random() > 0.5:
        num_certs = random.randint(1, 3)
        for _ in range(num_certs):
            cert_year = current_date.year - random.randint(0, 5)
            expires_year = cert_year + 3
            certifications.append(
                f"{random.choice(CERTIFICATIONS)} (Issued: {cert_year}, Expires: {expires_year})"
            )
    
    # Generate job search status as dictionary
    job_search_status = {
        "currently_looking": random.choice([True, False]),
        "available_from": (datetime.now() + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
        "desired_job_titles": random.sample(JOB_TITLES, random.randint(1, 3)),
        "preferred_employment_type": random.sample(["Full-time", "Part-time", "Contract", "Freelance"], random.randint(1, 2)),
        "salary_expectation_usd": {
            "min": random.randint(70000, 100000),
            "max": random.randint(100001, 150000)
        },
        "notice_period_days": random.randint(14, 60),
        "relocation_willingness": random.choice([True, False]),
        "additional_notes": fake.sentence()
    }
    
    # Generate candidate data
    return {
        "email": email,
        "password": "Password123!",  # Standard password for all test accounts
        "full_name": full_name,
        "phone": fake.phone_number(),
        "location": random.choice(LOCATIONS),
        "experience_years": experience_years,
        "education_summary": f"{education[0]['degree']} from {education[0]['institution']}",
        "bio": fake.paragraph(nb_sentences=2),
        "about": fake.paragraph(nb_sentences=3),
        "links": {
            "linkedin": f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
            "github": f"https://github.com/{first_name.lower()}{last_name.lower()}",
            "portfolio": f"https://{first_name.lower()}{last_name.lower()}.dev"
        },
        "skills": {
            "languages_frameworks": languages_frameworks,
            "ai_ml_data": ai_ml_data,
            "tools_platforms": tools_platforms,
            "soft_skills": soft_skills
        },
        "experience": experiences,
        "education": education,
        "certifications": certifications,
        "preferred_job_locations": random.sample(LOCATIONS, random.randint(1, 3)),
        "job_search_status": job_search_status
    }

def create_candidate(candidate_data):
    """Create a candidate account using the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/register/candidate",
            json=candidate_data
        )
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Created candidate: {candidate_data['full_name']} ({candidate_data['email']})")
            return response.json()
        else:
            print(f"❌ Failed to create candidate {candidate_data['email']}: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating candidate {candidate_data['email']}: {str(e)}")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Create demo candidate accounts")
    parser.add_argument("--count", type=int, default=10, help="Number of candidates to create")
    args = parser.parse_args()
    
    print(f"Creating {args.count} demo candidate accounts...")
    
    created_candidates = []
    for i in range(args.count):
        candidate_data = generate_candidate_data()
        result = create_candidate(candidate_data)
        if result:
            created_candidates.append(result)
    
    print(f"\nSuccessfully created {len(created_candidates)} out of {args.count} candidate accounts.")
    
    # Save created candidates to a JSON file for reference
    with open("tests/demo_candidates.json", "w") as f:
        json.dump(created_candidates, f, indent=2)
    print(f"Candidate data saved to tests/demo_candidates.json")

if __name__ == "__main__":
    main() 