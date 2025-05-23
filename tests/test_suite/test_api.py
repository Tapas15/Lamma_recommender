"""
API wrapper for the Job Recommender System test suite.
Provides functions to interact with the backend API.
"""
import os
import sys
import requests
import json
import time
from typing import Dict, List, Any, Optional, Union

# Add parent directory to path to find the test_suite module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_suite.test_config import API_BASE_URL

class JobRecommenderAPI:
    """API wrapper for the Job Recommender System"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        """Initialize the API wrapper"""
        self.base_url = base_url
        self.token = None
    
    def login(self, email: str, password: str) -> bool:
        """Login and get access token"""
        data = {
            "username": email,
            "password": password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/token", 
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                return True
            return False
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def register_employer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new employer"""
        return self._make_request("register/employer", method="POST", data=data)
    
    def register_candidate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new candidate"""
        return self._make_request("register/candidate", method="POST", data=data)
    
    def get_profile(self) -> Dict[str, Any]:
        """Get the current user's profile"""
        return self._make_request("profile")
    
    def update_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update the current user's profile"""
        return self._make_request("profile", method="PUT", data=data)
    
    # Job related endpoints
    def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job"""
        return self._make_request("jobs", method="POST", data=job_data)
    
    def get_jobs(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get a list of jobs"""
        return self._make_request(f"jobs?limit={limit}&offset={offset}")
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get a specific job"""
        return self._make_request(f"jobs/{job_id}")
    
    def update_job(self, job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a job"""
        return self._make_request(f"jobs/{job_id}", method="PUT", data=job_data)
    
    def delete_job(self, job_id: str) -> Dict[str, Any]:
        """Delete a job"""
        return self._make_request(f"jobs/{job_id}", method="DELETE")
    
    def search_jobs(self, query: str) -> List[Dict[str, Any]]:
        """Search for jobs"""
        return self._make_request("jobs/search", method="POST", data={"query": query})
    
    # Project related endpoints
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        return self._make_request("projects", method="POST", data=project_data)
    
    def get_projects(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get a list of projects"""
        return self._make_request(f"projects?limit={limit}&offset={offset}")
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project"""
        return self._make_request(f"projects/{project_id}")
    
    def update_project(self, project_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a project"""
        return self._make_request(f"projects/{project_id}", method="PUT", data=project_data)
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project"""
        return self._make_request(f"projects/{project_id}", method="DELETE")
    
    def search_projects(self, query: str) -> List[Dict[str, Any]]:
        """Search for projects"""
        return self._make_request("projects/search", method="POST", data={"query": query})
    
    # Application related endpoints
    def apply_for_job(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply for a job"""
        return self._make_request("applications", method="POST", data=application_data)
    
    def get_job_applications(self, job_id: str) -> List[Dict[str, Any]]:
        """Get applications for a specific job"""
        return self._make_request(f"jobs/{job_id}/applications")
    
    def get_candidate_job_applications(self) -> List[Dict[str, Any]]:
        """Get job applications for the current candidate"""
        return self._make_request("applications/candidate")
    
    def apply_for_project(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply for a project"""
        return self._make_request("project-applications", method="POST", data=application_data)
    
    def get_project_applications(self, project_id: str) -> List[Dict[str, Any]]:
        """Get applications for a specific project"""
        return self._make_request(f"projects/{project_id}/applications")
    
    def get_candidate_project_applications(self) -> List[Dict[str, Any]]:
        """Get project applications for the current candidate"""
        return self._make_request("project-applications/candidate")
    
    # Saved jobs and projects
    def save_job(self, saved_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a job for later"""
        return self._make_request("saved-jobs", method="POST", data=saved_job_data)
    
    def get_saved_jobs(self) -> List[Dict[str, Any]]:
        """Get saved jobs for the current candidate"""
        return self._make_request("saved-jobs")
    
    def save_project(self, saved_project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a project for later"""
        return self._make_request("saved-projects", method="POST", data=saved_project_data)
    
    def get_saved_projects(self) -> List[Dict[str, Any]]:
        """Get saved projects for the current candidate"""
        return self._make_request("saved-projects")
    
    # Recommendation related endpoints
    def get_job_recommendations(self) -> List[Dict[str, Any]]:
        """Get job recommendations for the current candidate"""
        return self._make_request("recommendations/jobs")
    
    def get_project_recommendations(self) -> List[Dict[str, Any]]:
        """Get project recommendations for the current candidate"""
        return self._make_request("recommendations/projects")
    
    def get_candidate_recommendations_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        """Get candidate recommendations for a specific job"""
        return self._make_request(f"recommendations/candidates/{job_id}")
    
    def get_candidate_recommendations_for_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get candidate recommendations for a specific project"""
        return self._make_request(f"recommendations/candidates-for-project/{project_id}")
    
    def get_skill_gap_analysis(self, target_role: str) -> Dict[str, Any]:
        """Get skill gap analysis for the current candidate"""
        return self._make_request(f"recommendations/skill-gap?target_role={target_role}")
    
    def get_learning_recommendations(self, skills: str) -> Dict[str, Any]:
        """Get learning recommendations for specific skills"""
        return self._make_request(f"recommendations/learning?skills={skills}")
    
    def get_career_path_recommendations(self, current_role: str) -> Dict[str, Any]:
        """Get career path recommendations"""
        return self._make_request(f"recommendations/career-path?current_role={current_role}")
    
    def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Dict[str, Any] = None, 
        params: Dict[str, Any] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Make a request to the API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            
            if response.status_code in [200, 201, 204]:
                try:
                    return response.json()
                except:
                    return {"message": "Success"}
            else:
                try:
                    error_data = response.json()
                    return {"error": f"Status {response.status_code}", "detail": error_data}
                except:
                    return {"error": f"Status {response.status_code}", "detail": response.text}
        except Exception as e:
            return {"error": "Request failed", "detail": str(e)} 