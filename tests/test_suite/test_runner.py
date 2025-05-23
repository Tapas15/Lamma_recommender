"""
Test runner for the Job Recommender System test suite.
Executes test flows for employer and candidate users.
"""
import os
import sys
import time
import json
from typing import Dict, List, Any, Tuple, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path to find the test_suite module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_suite.test_config import (
    TEST_USERS, TEST_RESULTS, API_BASE_URL,
    generate_job_data, generate_project_data, 
    generate_job_application, generate_project_application,
    generate_employer_profile, generate_candidate_profile
)
from test_suite.test_api import JobRecommenderAPI

# Console for rich output
console = Console()

class TestRunner:
    """Test runner for the Job Recommender System"""
    
    def __init__(self, api_url: str = API_BASE_URL):
        """Initialize the test runner"""
        self.api = JobRecommenderAPI(base_url=api_url)
        self.results = {
            "employer_flow": False,
            "candidate_flow": False,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        console.print("[bold purple]Job Recommender System - End-to-End Test[/bold purple]")
        console.print("=================================================\n")
        
        # Check if API is running
        if not self._check_api_connection():
            return self.results
        
        # Run employer flow
        employer_results = self.run_employer_flow()
        self.results["employer_flow"] = employer_results["success"]
        
        # Wait for any async operations to complete
        time.sleep(2)
        
        # Run candidate flow
        candidate_results = self.run_candidate_flow(employer_results["data"])
        self.results["candidate_flow"] = candidate_results["success"]
        
        # Generate test report
        self._generate_test_report()
        
        return self.results
    
    def run_employer_flow(self) -> Dict[str, Any]:
        """Run employer flow tests"""
        console.print("\n[bold cyan]===== EMPLOYER FLOW =====[/bold cyan]")
        
        flow_results = {
            "success": False,
            "data": {
                "jobs": [],
                "projects": []
            }
        }
        
        # 1. Login as employer
        employer = TEST_USERS["employer1"]
        console.print(f"\n[bold]1. Logging in as employer ({employer['email']})...[/bold]")
        
        login_success = self.api.login(employer["email"], employer["password"])
        if not login_success:
            # Try registering if login fails
            console.print("Login failed, attempting to register...")
            
            # Create employer registration data
            employer_data = generate_employer_profile()
            employer_data["email"] = employer["email"]
            employer_data["password"] = employer["password"]
            employer_data["user_type"] = "employer"
            
            register_result = self.api.register_employer(employer_data)
            
            if "error" in register_result:
                self._record_test("Employer Registration", False, register_result.get("error", "Unknown error"))
                console.print("[bold red]Failed to register employer[/bold red]")
                return flow_results
            
            self._record_test("Employer Registration", True)
            console.print("[green]Employer registration successful[/green]")
            
            # Try login again
            login_success = self.api.login(employer["email"], employer["password"])
            if not login_success:
                self._record_test("Employer Login After Registration", False, "Failed to login after registration")
                console.print("[bold red]Failed to login as employer after registration[/bold red]")
                return flow_results
        
        self._record_test("Employer Login", True)
        console.print("[green]Employer login successful[/green]")
        
        # 2. Get employer profile
        console.print("\n[bold]2. Getting employer profile...[/bold]")
        profile = self.api.get_profile()
        
        if "error" in profile:
            self._record_test("Get Employer Profile", False, profile.get("error", "Unknown error"))
            console.print(f"[bold red]Failed to get employer profile: {profile.get('error', 'Unknown error')}[/bold red]")
            return flow_results
        
        self._record_test("Get Employer Profile", True)
        console.print(f"[green]Got employer profile for: {profile.get('full_name')}[/green]")
        
        # Store profile in results
        TEST_RESULTS["employer"] = profile
        
        # 3. Post multiple jobs
        console.print("\n[bold]3. Posting jobs...[/bold]")
        job_ids = []
        
        for i in range(3):
            job_data = generate_job_data(profile.get("company_details", {}).get("company_name", "Test Company"))
            job_result = self.api.create_job(job_data)
            
            if "error" in job_result:
                self._record_test(f"Post Job {i+1}", False, job_result.get("error", "Unknown error"))
                console.print(f"[bold red]Failed to post job {i+1}: {job_result.get('error', 'Unknown error')}[/bold red]")
            else:
                job_id = job_result.get("id")
                job_ids.append(job_id)
                flow_results["data"]["jobs"].append(job_id)
                TEST_RESULTS["jobs"].append(job_result)
                self._record_test(f"Post Job {i+1}", True)
                console.print(f"[green]Posted job {i+1} successfully! Job ID: {job_id}[/green]")
        
        if not job_ids:
            console.print("[bold red]Failed to post any jobs[/bold red]")
            return flow_results
        
        # 4. Post multiple projects
        console.print("\n[bold]4. Posting projects...[/bold]")
        project_ids = []
        
        for i in range(2):
            project_data = generate_project_data(profile.get("company_details", {}).get("company_name", "Test Company"))
            project_result = self.api.create_project(project_data)
            
            if "error" in project_result:
                self._record_test(f"Post Project {i+1}", False, project_result.get("error", "Unknown error"))
                console.print(f"[bold red]Failed to post project {i+1}: {project_result.get('error', 'Unknown error')}[/bold red]")
            else:
                project_id = project_result.get("id")
                project_ids.append(project_id)
                flow_results["data"]["projects"].append(project_id)
                TEST_RESULTS["projects"].append(project_result)
                self._record_test(f"Post Project {i+1}", True)
                console.print(f"[green]Posted project {i+1} successfully! Project ID: {project_id}[/green]")
        
        if not project_ids:
            console.print("[bold red]Failed to post any projects[/bold red]")
            return flow_results
        
        # 5. Get job applications (likely none yet)
        console.print("\n[bold]5. Getting job applications...[/bold]")
        job_applications = self.api.get_job_applications(job_ids[0])
        
        if "error" in job_applications:
            self._record_test("Get Job Applications", False, job_applications.get("error", "Unknown error"))
            console.print(f"[yellow]No job applications found or error: {job_applications.get('error', 'Unknown error')}[/yellow]")
        else:
            self._record_test("Get Job Applications", True)
            console.print(f"[green]Retrieved {len(job_applications)} job applications[/green]")
        
        # 6. Get project applications (likely none yet)
        console.print("\n[bold]6. Getting project applications...[/bold]")
        project_applications = self.api.get_project_applications(project_ids[0])
        
        if "error" in project_applications:
            self._record_test("Get Project Applications", False, project_applications.get("error", "Unknown error"))
            console.print(f"[yellow]No project applications found or error: {project_applications.get('error', 'Unknown error')}[/yellow]")
        else:
            self._record_test("Get Project Applications", True)
            console.print(f"[green]Retrieved {len(project_applications)} project applications[/green]")
        
        # 7. Get candidate recommendations for job
        console.print("\n[bold]7. Getting candidate recommendations for job...[/bold]")
        job_recommendations = self.api.get_candidate_recommendations_for_job(job_ids[0])
        
        if "error" in job_recommendations:
            self._record_test("Get Job Recommendations", False, job_recommendations.get("error", "Unknown error"))
            console.print(f"[yellow]No job recommendations found or error: {job_recommendations.get('error', 'Unknown error')}[/yellow]")
        else:
            self._record_test("Get Job Recommendations", True)
            console.print(f"[green]Retrieved candidate recommendations for job[/green]")
        
        # 8. Get candidate recommendations for project
        console.print("\n[bold]8. Getting candidate recommendations for project...[/bold]")
        project_recommendations = self.api.get_candidate_recommendations_for_project(project_ids[0])
        
        if "error" in project_recommendations:
            self._record_test("Get Project Recommendations", False, project_recommendations.get("error", "Unknown error"))
            console.print(f"[yellow]No project recommendations found or error: {project_recommendations.get('error', 'Unknown error')}[/yellow]")
        else:
            self._record_test("Get Project Recommendations", True)
            console.print(f"[green]Retrieved candidate recommendations for project[/green]")
        
        console.print("\n[bold green]Employer flow completed successfully![/bold green]")
        flow_results["success"] = True
        return flow_results
    
    def run_candidate_flow(self, employer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run candidate flow tests"""
        console.print("\n[bold cyan]===== CANDIDATE FLOW =====[/bold cyan]")
        
        flow_results = {
            "success": False,
            "data": {}
        }
        
        # 1. Login as candidate
        candidate = TEST_USERS["candidate1"]
        console.print(f"\n[bold]1. Logging in as candidate ({candidate['email']})...[/bold]")
        
        login_success = self.api.login(candidate["email"], candidate["password"])
        if not login_success:
            # Try registering if login fails
            console.print("Login failed, attempting to register...")
            
            # Create candidate registration data
            candidate_data = generate_candidate_profile()
            candidate_data["email"] = candidate["email"]
            candidate_data["password"] = candidate["password"]
            candidate_data["user_type"] = "candidate"
            
            register_result = self.api.register_candidate(candidate_data)
            
            if "error" in register_result:
                self._record_test("Candidate Registration", False, register_result.get("error", "Unknown error"))
                console.print("[bold red]Failed to register candidate[/bold red]")
                return flow_results
            
            self._record_test("Candidate Registration", True)
            console.print("[green]Candidate registration successful[/green]")
            
            # Try login again
            login_success = self.api.login(candidate["email"], candidate["password"])
            if not login_success:
                self._record_test("Candidate Login After Registration", False, "Failed to login after registration")
                console.print("[bold red]Failed to login as candidate after registration[/bold red]")
                return flow_results
        
        self._record_test("Candidate Login", True)
        console.print("[green]Candidate login successful[/green]")
        
        # 2. Get candidate profile
        console.print("\n[bold]2. Getting candidate profile...[/bold]")
        profile = self.api.get_profile()
        
        if "error" in profile:
            self._record_test("Get Candidate Profile", False, profile.get("error", "Unknown error"))
            console.print(f"[bold red]Failed to get candidate profile: {profile.get('error', 'Unknown error')}[/bold red]")
            return flow_results
        
        self._record_test("Get Candidate Profile", True)
        console.print(f"[green]Got candidate profile for: {profile.get('full_name')}[/green]")
        
        # Store profile in results
        TEST_RESULTS["candidate"] = profile
        
        # 3. Search for jobs
        console.print("\n[bold]3. Searching for jobs...[/bold]")
        search_query = "Software Engineer"
        job_search_results = self.api.search_jobs(search_query)
        
        if "error" in job_search_results:
            self._record_test("Search Jobs", False, job_search_results.get("error", "Unknown error"))
            console.print(f"[bold red]Failed to search for jobs: {job_search_results.get('error', 'Unknown error')}[/bold red]")
        else:
            self._record_test("Search Jobs", True)
            console.print(f"[green]Found {len(job_search_results)} jobs matching search query[/green]")
        
        # 4. Get job recommendations
        console.print("\n[bold]4. Getting job recommendations...[/bold]")
        job_recommendations = self.api.get_job_recommendations()
        
        if "error" in job_recommendations:
            self._record_test("Get Job Recommendations", False, job_recommendations.get("error", "Unknown error"))
            console.print(f"[yellow]No job recommendations found or error: {job_recommendations.get('error', 'Unknown error')}[/yellow]")
        else:
            self._record_test("Get Job Recommendations", True)
            console.print(f"[green]Retrieved {len(job_recommendations)} job recommendations[/green]")
        
        # 5. Get project recommendations
        console.print("\n[bold]5. Getting project recommendations...[/bold]")
        project_recommendations = self.api.get_project_recommendations()
        
        if "error" in project_recommendations:
            self._record_test("Get Project Recommendations", False, project_recommendations.get("error", "Unknown error"))
            console.print(f"[yellow]No project recommendations found or error: {project_recommendations.get('error', 'Unknown error')}[/yellow]")
        else:
            self._record_test("Get Project Recommendations", True)
            console.print(f"[green]Retrieved {len(project_recommendations)} project recommendations[/green]")
        
        # 6. Apply for job (if we have job ID from employer flow)
        if employer_data and "jobs" in employer_data and employer_data["jobs"]:
            job_id = employer_data["jobs"][0]
            console.print(f"\n[bold]6. Applying for job {job_id}...[/bold]")
            job_application = generate_job_application(job_id)
            job_application_result = self.api.apply_for_job(job_application)
            
            if "error" in job_application_result:
                self._record_test("Apply for Job", False, job_application_result.get("error", "Unknown error"))
                console.print(f"[bold red]Failed to apply for job: {job_application_result.get('error', 'Unknown error')}[/bold red]")
            else:
                self._record_test("Apply for Job", True)
                console.print(f"[green]Applied for job successfully! Application ID: {job_application_result.get('id')}[/green]")
                TEST_RESULTS["applications"].append(job_application_result)
        
        # 7. Apply for project (if we have project ID from employer flow)
        if employer_data and "projects" in employer_data and employer_data["projects"]:
            project_id = employer_data["projects"][0]
            console.print(f"\n[bold]7. Applying for project {project_id}...[/bold]")
            project_application = generate_project_application(project_id)
            project_application_result = self.api.apply_for_project(project_application)
            
            if "error" in project_application_result:
                self._record_test("Apply for Project", False, project_application_result.get("error", "Unknown error"))
                console.print(f"[bold red]Failed to apply for project: {project_application_result.get('error', 'Unknown error')}[/bold red]")
            else:
                self._record_test("Apply for Project", True)
                console.print(f"[green]Applied for project successfully! Application ID: {project_application_result.get('id')}[/green]")
                TEST_RESULTS["applications"].append(project_application_result)
        
        # 8. Save a job (if we have job ID from employer flow)
        if employer_data and "jobs" in employer_data and len(employer_data["jobs"]) > 1:
            job_id = employer_data["jobs"][1]  # Use a different job than the one we applied for
            console.print(f"\n[bold]8. Saving job {job_id}...[/bold]")
            saved_job = {
                "job_id": job_id,
                "notes": "Interesting opportunity to apply for later"
            }
            saved_job_result = self.api.save_job(saved_job)
            
            if "error" in saved_job_result:
                self._record_test("Save Job", False, saved_job_result.get("error", "Unknown error"))
                console.print(f"[bold red]Failed to save job: {saved_job_result.get('error', 'Unknown error')}[/bold red]")
            else:
                self._record_test("Save Job", True)
                console.print(f"[green]Saved job successfully! Saved ID: {saved_job_result.get('id')}[/green]")
                TEST_RESULTS["saved"].append(saved_job_result)
        
        # 9. Save a project (if we have project ID from employer flow)
        if employer_data and "projects" in employer_data and len(employer_data["projects"]) > 1:
            project_id = employer_data["projects"][1]  # Use a different project than the one we applied for
            console.print(f"\n[bold]9. Saving project {project_id}...[/bold]")
            saved_project = {
                "project_id": project_id,
                "notes": "Interesting project to consider later"
            }
            saved_project_result = self.api.save_project(saved_project)
            
            if "error" in saved_project_result:
                self._record_test("Save Project", False, saved_project_result.get("error", "Unknown error"))
                console.print(f"[bold red]Failed to save project: {saved_project_result.get('error', 'Unknown error')}[/bold red]")
            else:
                self._record_test("Save Project", True)
                console.print(f"[green]Saved project successfully! Saved ID: {saved_project_result.get('id')}[/green]")
                TEST_RESULTS["saved"].append(saved_project_result)
        
        # 10. Get skill gap analysis
        console.print("\n[bold]10. Getting skill gap analysis...[/bold]")
        skill_gap = self.api.get_skill_gap_analysis("Software Engineer")
        
        if "error" in skill_gap:
            self._record_test("Skill Gap Analysis", False, skill_gap.get("error", "Unknown error"))
            console.print(f"[bold red]Failed to get skill gap analysis: {skill_gap.get('error', 'Unknown error')}[/bold red]")
        else:
            self._record_test("Skill Gap Analysis", True)
            match_score = skill_gap.get("match_score", "N/A")
            console.print(f"[green]Retrieved skill gap analysis. Match score: {match_score}%[/green]")
        
        # 11. Get learning recommendations
        console.print("\n[bold]11. Getting learning recommendations...[/bold]")
        skills = ",".join(["AWS", "Docker", "React"])
        learning_recommendations = self.api.get_learning_recommendations(skills)
        
        if "error" in learning_recommendations:
            self._record_test("Learning Recommendations", False, learning_recommendations.get("error", "Unknown error"))
            console.print(f"[bold red]Failed to get learning recommendations: {learning_recommendations.get('error', 'Unknown error')}[/bold red]")
        else:
            self._record_test("Learning Recommendations", True)
            console.print(f"[green]Retrieved learning recommendations for skills[/green]")
        
        # 12. Get career path recommendations
        console.print("\n[bold]12. Getting career path recommendations...[/bold]")
        career_path = self.api.get_career_path_recommendations("Software Engineer")
        
        if "error" in career_path:
            self._record_test("Career Path Recommendations", False, career_path.get("error", "Unknown error"))
            console.print(f"[bold red]Failed to get career path recommendations: {career_path.get('error', 'Unknown error')}[/bold red]")
        else:
            self._record_test("Career Path Recommendations", True)
            console.print(f"[green]Retrieved career path recommendations[/green]")
        
        # 13. Check job applications
        console.print("\n[bold]13. Checking job applications...[/bold]")
        job_applications = self.api.get_candidate_job_applications()
        
        if "error" in job_applications:
            self._record_test("Get Candidate Job Applications", False, job_applications.get("error", "Unknown error"))
            console.print(f"[yellow]No job applications found or error: {job_applications.get('error', 'Unknown error')}[/yellow]")
        else:
            self._record_test("Get Candidate Job Applications", True)
            console.print(f"[green]Retrieved {len(job_applications)} job applications[/green]")
        
        # 14. Check saved jobs
        console.print("\n[bold]14. Checking saved jobs...[/bold]")
        saved_jobs = self.api.get_saved_jobs()
        
        if "error" in saved_jobs:
            self._record_test("Get Saved Jobs", False, saved_jobs.get("error", "Unknown error"))
            console.print(f"[yellow]No saved jobs found or error: {saved_jobs.get('error', 'Unknown error')}[/yellow]")
        else:
            self._record_test("Get Saved Jobs", True)
            console.print(f"[green]Retrieved {len(saved_jobs)} saved jobs[/green]")
        
        console.print("\n[bold green]Candidate flow completed successfully![/bold green]")
        flow_results["success"] = True
        return flow_results
    
    def _check_api_connection(self) -> bool:
        """Check if the API is running"""
        try:
            import requests
            response = requests.get(f"{self.api.base_url}/docs", timeout=5)
            if response.status_code != 200:
                console.print(f"[bold red]API is not running at {self.api.base_url}. Please start the backend first.[/bold red]")
                return False
            console.print(f"[green]Connected to API at {self.api.base_url}[/green]")
            return True
        except Exception as e:
            console.print(f"[bold red]Cannot connect to API at {self.api.base_url}. Please start the backend first.[/bold red]")
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def _record_test(self, test_name: str, passed: bool, error: str = None) -> None:
        """Record a test result"""
        self.results["tests_run"] += 1
        if passed:
            self.results["tests_passed"] += 1
        else:
            self.results["tests_failed"] += 1
        
        self.results["test_details"].append({
            "name": test_name,
            "passed": passed,
            "error": error
        })
    
    def _generate_test_report(self) -> None:
        """Generate and display a test report"""
        console.print("\n[bold cyan]===== TEST REPORT =====[/bold cyan]")
        
        # Create a table for the test results
        table = Table(title="End-to-End Test Results")
        table.add_column("Flow", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")
        
        table.add_row(
            "Employer Flow", 
            "[SUCCESS] PASSED" if self.results["employer_flow"] else "[ERROR] FAILED",
            "All employer operations completed" if self.results["employer_flow"] else "Some employer operations failed"
        )
        
        table.add_row(
            "Candidate Flow", 
            "[SUCCESS] PASSED" if self.results["candidate_flow"] else "[ERROR] FAILED",
            "All candidate operations completed" if self.results["candidate_flow"] else "Some candidate operations failed"
        )
        
        overall_success = self.results["employer_flow"] and self.results["candidate_flow"]
        table.add_row(
            "Overall Test", 
            "[SUCCESS] PASSED" if overall_success else "[ERROR] FAILED",
            "System functioning correctly" if overall_success else "System requires attention"
        )
        
        console.print(table)
        
        # Create a table for individual test results
        test_table = Table(title="Individual Test Results")
        test_table.add_column("Test", style="cyan")
        test_table.add_column("Status", style="green")
        test_table.add_column("Error", style="red")
        
        for test in self.results["test_details"]:
            test_table.add_row(
                test["name"],
                "[SUCCESS] PASSED" if test["passed"] else "[ERROR] FAILED",
                test.get("error", "") if not test["passed"] else ""
            )
        
        console.print(test_table)
        
        # Summary
        console.print(f"\n[bold]Tests Run: {self.results['tests_run']}[/bold]")
        console.print(f"[bold green]Tests Passed: {self.results['tests_passed']}[/bold green]")
        console.print(f"[bold red]Tests Failed: {self.results['tests_failed']}[/bold red]")
        
        # Additional information
        if overall_success:
            console.print("\n[bold green][SUCCESS] The Job Recommender system is functioning correctly![/bold green]")
            console.print("All test flows completed successfully.")
        else:
            console.print("\n[bold red][ERROR] The Job Recommender system has issues that need to be addressed.[/bold red]")
            if not self.results["employer_flow"]:
                console.print("- Employer flow failed. Check the employer account and job/project creation.")
            if not self.results["candidate_flow"]:
                console.print("- Candidate flow failed. Check the candidate account and application functionality.")

def main():
    """Main function to run the test suite"""
    runner = TestRunner()
    results = runner.run_all_tests()
    
    # Save results to file
    try:
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        console.print("\n[green]Test results saved to test_results.json[/green]")
    except Exception as e:
        console.print(f"\n[red]Failed to save test results: {str(e)}[/red]")

if __name__ == "__main__":
    main() 