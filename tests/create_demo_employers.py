#!/usr/bin/env python
"""
Test script to create demo employer accounts for testing purposes.
This script will create a specified number of employer accounts with realistic data.

Usage:
    python create_demo_employers.py [--count N]
    
    --count N: Number of employer accounts to create (default: 10)
"""

import os
import sys
import json
import random
import argparse
import requests
from faker import Faker

# Add the parent directory to the path so we can import from utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
API_BASE_URL = "http://localhost:8000"
fake = Faker()

# Company data
INDUSTRIES = [
    "Technology", "Finance", "Healthcare", "Education", "E-commerce", 
    "Manufacturing", "Retail", "Media", "Consulting", "Telecommunications",
    "Energy", "Transportation", "Real Estate", "Hospitality", "Entertainment"
]

COMPANY_SIZES = [
    "1-10", "11-50", "51-200", "201-500", "501-1000", 
    "1001-5000", "5001-10000", "10000+"
]

COMPANY_VALUES = [
    "Innovation", "Integrity", "Excellence", "Customer Focus", "Teamwork",
    "Diversity", "Sustainability", "Quality", "Accountability", "Transparency",
    "Creativity", "Respect", "Growth", "Passion", "Balance"
]

TECH_STACK = [
    "Python", "JavaScript", "TypeScript", "Java", "C#", "Go", "Rust",
    "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring Boot",
    "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch",
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform"
]

JOB_ROLES = [
    "Software Engineer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "DevOps Engineer", "Data Scientist",
    "Machine Learning Engineer", "Product Manager", "Project Manager",
    "UI/UX Designer", "QA Engineer", "Technical Writer", "Security Engineer",
    "Database Administrator", "Mobile Developer", "Cloud Architect"
]

EMPLOYMENT_TYPES = [
    "Full-time", "Part-time", "Contract", "Freelance", 
    "Internship", "Remote"
]

LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Boston, MA",
    "Austin, TX", "Chicago, IL", "Los Angeles, CA", "Denver, CO",
    "Portland, OR", "Atlanta, GA", "Toronto, Canada", "Vancouver, Canada",
    "London, UK", "Berlin, Germany", "Paris, France", "Amsterdam, Netherlands",
    "Sydney, Australia", "Singapore", "Tokyo, Japan", "Remote"
]

RECRUITER_TITLES = [
    "Talent Acquisition Specialist", "HR Manager", "Technical Recruiter",
    "Hiring Manager", "Talent Acquisition Manager", "HR Director",
    "Recruitment Specialist", "People Operations Manager", "HR Business Partner",
    "Chief People Officer", "VP of Human Resources", "Founder", "CEO", "CTO"
]

def generate_employer_data():
    """Generate realistic employer data"""
    company_name = fake.company()
    domain = company_name.lower().replace(" ", "").replace(",", "").replace(".", "") + ".com"
    
    # Generate recruiter info
    first_name = fake.first_name()
    last_name = fake.last_name()
    full_name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
    
    # Generate company location
    company_location = random.choice(LOCATIONS)
    
    # Generate company founding year (between 1980 and 2020)
    founded_year = random.randint(1980, 2020)
    
    # Generate company details
    company_details = {
        "company_name": company_name,
        "company_description": fake.paragraph(nb_sentences=3),
        "company_website": f"https://www.{domain}",
        "company_location": company_location,
        "company_size": random.choice(COMPANY_SIZES),
        "industry": random.choice(INDUSTRIES),
        "founded_year": founded_year,
        "company_logo": f"https://logo.clearbit.com/{domain}",
        "company_socials": {
            "linkedin": f"https://linkedin.com/company/{domain.split('.')[0]}",
            "twitter": f"https://twitter.com/{domain.split('.')[0]}",
            "glassdoor": f"https://glassdoor.com/company/{domain.split('.')[0]}"
        },
        "values": random.sample(COMPANY_VALUES, random.randint(3, 5)),
        "mission": fake.sentence(),
        "vision": fake.sentence()
    }
    
    # Generate hiring preferences
    salary_min = random.choice([50000, 60000, 70000, 80000, 90000, 100000, 120000])
    salary_max = salary_min + random.choice([20000, 30000, 40000, 50000, 60000, 80000])
    
    hiring_preferences = {
        "job_roles_hiring": random.sample(JOB_ROLES, random.randint(2, 5)),
        "employment_types": random.sample(EMPLOYMENT_TYPES, random.randint(1, 3)),
        "locations_hiring": random.sample(LOCATIONS, random.randint(1, 3)),
        "salary_range_usd": {
            "min": salary_min,
            "max": salary_max
        },
        "remote_friendly": random.choice([True, False]),
        "tech_stack": random.sample(TECH_STACK, random.randint(3, 8))
    }
    
    # Generate employer data
    return {
        "email": email,
        "password": "Password123!",  # Standard password for all test accounts
        "full_name": full_name,
        "user_type": "employer",
        "position": random.choice(RECRUITER_TITLES),
        "bio": fake.paragraph(nb_sentences=1),
        "about": fake.paragraph(nb_sentences=2),
        "contact_email": f"careers@{domain}",
        "contact_phone": fake.phone_number(),
        "location": company_location,
        "company_details": {
            "company_name": company_name,
            "company_description": fake.paragraph(nb_sentences=3),
            "company_website": f"https://www.{domain}",
            "company_location": company_location,
            "company_size": random.choice(COMPANY_SIZES),
            "industry": random.choice(INDUSTRIES),
            "founded_year": founded_year,
            "company_logo": f"https://logo.clearbit.com/{domain}",
            "company_socials": {
                "linkedin": f"https://linkedin.com/company/{domain.split('.')[0]}",
                "twitter": f"https://twitter.com/{domain.split('.')[0]}",
                "glassdoor": f"https://glassdoor.com/company/{domain.split('.')[0]}"
            },
            "values": random.sample(COMPANY_VALUES, random.randint(3, 5)),
            "mission": fake.sentence(),
            "vision": fake.sentence()
        },
        "hiring_preferences": {
            "job_roles_hiring": random.sample(JOB_ROLES, random.randint(2, 5)),
            "employment_types": random.sample(EMPLOYMENT_TYPES, random.randint(1, 3)),
            "locations_hiring": random.sample(LOCATIONS, random.randint(1, 3)),
            "salary_range_usd": {
                "min": salary_min,
                "max": salary_max
            },
            "remote_friendly": random.choice([True, False]),
            "tech_stack": random.sample(TECH_STACK, random.randint(3, 8))
        }
    }

def create_employer(employer_data):
    """Create an employer account using the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/register/employer",
            json=employer_data
        )
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Created employer: {employer_data['full_name']} ({employer_data['company_details']['company_name']})")
            return response.json()
        else:
            print(f"❌ Failed to create employer {employer_data['email']}: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating employer {employer_data['email']}: {str(e)}")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Create demo employer accounts")
    parser.add_argument("--count", type=int, default=10, help="Number of employers to create")
    args = parser.parse_args()
    
    print(f"Creating {args.count} demo employer accounts...")
    
    created_employers = []
    for i in range(args.count):
        employer_data = generate_employer_data()
        result = create_employer(employer_data)
        if result:
            created_employers.append(result)
    
    print(f"\nSuccessfully created {len(created_employers)} out of {args.count} employer accounts.")
    
    # Save created employers to a JSON file for reference
    with open("tests/demo_employers.json", "w") as f:
        json.dump(created_employers, f, indent=2)
    print(f"Employer data saved to tests/demo_employers.json")

if __name__ == "__main__":
    main() 