#!/usr/bin/env python
"""
Test script to create demo project postings for testing purposes.
This script will create a specified number of projects using employer accounts.
If the employer login fails, it will register a new employer account.

Usage:
    python create_demo_projects.py [--count N]
    
    --count N: Number of project postings to create (default: 10)
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

# Try to load existing employers from the demo file
EMPLOYERS = []
try:
    with open("tests/demo_employers.json", "r") as f:
        EMPLOYERS = json.load(f)
except Exception:
    print("No existing demo employers found. Will create new employers as needed.")

# Project data
PROJECT_TITLES = [
    "E-commerce Website Development", "Mobile App Development", 
    "Machine Learning Recommendation System", "Data Visualization Dashboard",
    "API Integration", "Cloud Migration", "DevOps Pipeline Setup",
    "Security Assessment", "UI/UX Redesign", "Database Optimization",
    "Blockchain Implementation", "IoT System Development", "AI Chatbot",
    "Content Management System", "Payment Gateway Integration",
    "Social Media Platform", "Video Streaming Service", "Real-time Analytics Platform",
    "Customer Portal Development", "Enterprise Resource Planning System"
]

PROJECT_TYPES = [
    "Web Application", "Mobile Application", "API Development",
    "Data Science", "Machine Learning", "DevOps", "Cloud Infrastructure",
    "UI/UX Design", "Database Design", "Security Implementation",
    "Blockchain", "IoT", "AI/ML", "Content Management", "E-commerce"
]

TECH_STACK = [
    "Python", "JavaScript", "TypeScript", "Java", "C#", "Go", "Rust",
    "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot",
    "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch",
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform"
]

LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Boston, MA",
    "Austin, TX", "Chicago, IL", "Los Angeles, CA", "Denver, CO",
    "Portland, OR", "Atlanta, GA", "Toronto, Canada", "Vancouver, Canada",
    "London, UK", "Berlin, Germany", "Paris, France", "Amsterdam, Netherlands",
    "Sydney, Australia", "Singapore", "Tokyo, Japan", "Remote"
]

def login_employer(email, password):
    """Login as an employer and get access token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={
                "username": email,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Login failed for {email}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error logging in as {email}: {str(e)}")
        return None

def generate_project_data(employer_id=None):
    """Generate realistic project posting data"""
    title = random.choice(PROJECT_TITLES)
    company = fake.company()
    project_type = random.choice(PROJECT_TYPES)
    
    # Select project details
    location = random.choice(LOCATIONS)
    requirements = random.sample(TECH_STACK, random.randint(3, 8))
    skills_required = random.sample(TECH_STACK, random.randint(3, 8))
    
    # Generate budget range
    budget_min = random.choice([5000, 10000, 15000, 20000, 25000, 30000, 40000, 50000])
    budget_max = budget_min + random.choice([5000, 10000, 15000, 20000, 30000, 50000])
    
    # Generate duration
    duration_months = random.randint(1, 12)
    estimated_hours = duration_months * random.randint(40, 160)
    
    # Generate tools and technologies
    tools_technologies = random.sample(TECH_STACK, random.randint(3, 8))
    
    # Generate objectives and qualifications
    objectives = [fake.sentence() for _ in range(random.randint(3, 6))]
    preferred_qualifications = [fake.sentence() for _ in range(random.randint(3, 5))]
    
    # Generate dates for timeline
    today = datetime.now()
    start_date = (today + timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=30*duration_months + random.randint(0, 30))).strftime("%Y-%m-%d")
    
    # Generate milestones
    num_milestones = random.randint(2, 5)
    milestones = []
    for i in range(num_milestones):
        milestone_date = (today + timedelta(days=30*(i+1))).strftime("%Y-%m-%d")
        milestones.append({
            "name": f"Milestone {i+1}: {fake.bs()}",
            "deadline": milestone_date
        })
    
    # Generate deliverables
    deliverables = [fake.sentence() for _ in range(random.randint(3, 6))]
    
    # Generate project data
    project_data = {
        "title": title,
        "company": company,
        "description": fake.paragraph(nb_sentences=4),
        "project_type": project_type,
        "requirements": requirements,
        "skills_required": skills_required,
        "location": location,
        "budget_range": {
            "min": budget_min,
            "max": budget_max,
            "currency": "USD"
        },
        "duration": {
            "time_frame": f"{duration_months} months",
            "estimated_hours": estimated_hours
        },
        "tools_technologies": tools_technologies,
        "objectives": objectives,
        "preferred_qualifications": preferred_qualifications,
        "timeline": {
            "start_date": start_date,
            "end_date": end_date,
            "milestones": milestones
        },
        "experience": {
            "level": random.choice(["Beginner", "Intermediate", "Advanced", "Expert"]),
            "domain": random.choice(PROJECT_TYPES),
            "years": f"{random.randint(1, 10)}+ years",
            "project_examples": [fake.bs() for _ in range(random.randint(1, 3))]
        },
        "deliverables": deliverables
    }
    
    # Add employer ID if provided
    if employer_id:
        project_data["employer_id"] = employer_id
    
    return project_data

def create_project(token, project_data):
    """Create a project posting using the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/projects",
            json=project_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Created project: {project_data['title']} at {project_data['company']}")
            return response.json()
        else:
            print(f"❌ Failed to create project {project_data['title']}: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating project {project_data['title']}: {str(e)}")
        return None

def get_employer_token():
    """Get an employer token, either by logging in or creating a new account"""
    # Try to login with existing employers
    for employer in EMPLOYERS:
        email = employer.get("email")
        if not email:
            continue
            
        token = login_employer(email, "Password123!")
        if token:
            print(f"✅ Logged in as existing employer: {email}")
            
            # Get employer ID from API
            try:
                response = requests.get(
                    f"{API_BASE_URL}/profile",
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )
                
                if response.status_code == 200:
                    employer_id = response.json().get("id")
                    if employer_id:
                        print(f"Retrieved employer ID: {employer_id}")
                        return token, employer_id
                    else:
                        print("Error: No employer ID found in profile response.")
                else:
                    print(f"Error getting profile: {response.status_code}")
            except Exception as e:
                print(f"Error retrieving employer profile: {str(e)}")
            
            return token, None
    
    # If no existing employers or login failed, create a new one
    print("Creating a new employer account...")
    from create_demo_employers import generate_employer_data, create_employer
    
    employer_data = generate_employer_data()
    new_employer = create_employer(employer_data)
    
    if new_employer:
        # Try to login with the new employer
        token = login_employer(employer_data["email"], "Password123!")
        if token:
            print(f"✅ Logged in as new employer: {employer_data['email']}")
            
            # Get employer ID from API
            try:
                response = requests.get(
                    f"{API_BASE_URL}/profile",
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )
                
                if response.status_code == 200:
                    employer_id = response.json().get("id")
                    if employer_id:
                        print(f"Retrieved employer ID: {employer_id}")
                        return token, employer_id
                    else:
                        print("Error: No employer ID found in profile response.")
                else:
                    print(f"Error getting profile: {response.status_code}")
            except Exception as e:
                print(f"Error retrieving employer profile: {str(e)}")
    
    print("❌ Failed to get an employer token. Cannot create projects.")
    return None, None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Create demo project postings")
    parser.add_argument("--count", type=int, default=10, help="Number of projects to create")
    args = parser.parse_args()
    
    # Get employer token
    token, employer_id = get_employer_token()
    if not token:
        print("Exiting due to authentication failure.")
        return
    
    if not employer_id:
        print("Error: No employer ID available. Cannot create projects.")
        return
        
    # Create projects
    print(f"\nCreating {args.count} demo project postings...")
    created_projects = []
    for i in range(args.count):
        project_data = generate_project_data(employer_id)
        result = create_project(token, project_data)
        if result:
            created_projects.append(result)
    
    print(f"\nSuccessfully created {len(created_projects)} out of {args.count} project postings.")
    
    # Save created projects to a JSON file for reference
    with open("tests/demo_projects.json", "w") as f:
        json.dump(created_projects, f, indent=2)
    print(f"Project data saved to tests/demo_projects.json")

if __name__ == "__main__":
    main() 