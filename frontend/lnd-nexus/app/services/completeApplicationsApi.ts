// Base URL for the API - using localhost:8000 for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Application Interfaces
export interface JobApplicationRequest {
  job_id: string;
  cover_letter?: string;
  custom_message?: string;
  portfolio_links?: string[];
  availability_date?: string;
  salary_expectation?: number;
}

export interface ProjectApplicationRequest {
  project_id: string;
  proposal: string;
  estimated_duration: string;
  proposed_budget?: number;
  portfolio_samples?: string[];
  availability_date?: string;
  custom_message?: string;
}

export interface ApplicationResponse {
  id: string;
  status: 'pending' | 'reviewed' | 'accepted' | 'rejected';
  submitted_at: string;
  candidate_id: string;
  candidate_name: string;
  candidate_email: string;
  cover_letter?: string;
  proposal?: string;
  portfolio_links?: string[];
  estimated_duration?: string;
  proposed_budget?: number;
  [key: string]: any;
}

export interface SavedJobRequest {
  job_id: string;
  notes?: string;
  priority?: 'high' | 'medium' | 'low';
}

export interface SavedProjectRequest {
  project_id: string;
  notes?: string;
  priority?: 'high' | 'medium' | 'low';
  interest_level?: number; // 1-5 scale
}

// Helper function for handling responses
async function handleApplicationResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`Application API failed: ${response.status} - ${errorData.detail || response.statusText}`);
  }
  
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json() as T;
  }
  
  return {} as T;
}

// Complete Applications API
export const completeApplicationsApi = {
  // ===== JOB APPLICATIONS =====
  
  // Apply for a job
  applyForJob: async (token: string, applicationData: JobApplicationRequest): Promise<ApplicationResponse> => {
    const response = await fetch(`${API_BASE_URL}/applications`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(applicationData),
    });
    
    return handleApplicationResponse<ApplicationResponse>(response);
  },

  // Get all job applications for current candidate
  getMyJobApplications: async (token: string): Promise<ApplicationResponse[]> => {
    const response = await fetch(`${API_BASE_URL}/applications`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleApplicationResponse<ApplicationResponse[]>(response);
  },

  // Get applications for a specific job (for employers)
  getJobApplications: async (token: string, jobId: string): Promise<ApplicationResponse[]> => {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/applications`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleApplicationResponse<ApplicationResponse[]>(response);
  },

  // ===== PROJECT APPLICATIONS =====
  
  // Apply for a project
  applyForProject: async (token: string, applicationData: ProjectApplicationRequest): Promise<ApplicationResponse> => {
    const response = await fetch(`${API_BASE_URL}/project-applications`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(applicationData),
    });
    
    return handleApplicationResponse<ApplicationResponse>(response);
  },

  // Get all project applications for current candidate
  getMyProjectApplications: async (token: string): Promise<ApplicationResponse[]> => {
    const response = await fetch(`${API_BASE_URL}/project-applications`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleApplicationResponse<ApplicationResponse[]>(response);
  },

  // Get applications for a specific project (for employers)
  getProjectApplications: async (token: string, projectId: string): Promise<ApplicationResponse[]> => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/applications`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleApplicationResponse<ApplicationResponse[]>(response);
  },

  // ===== SAVED JOBS =====
  
  // Save a job
  saveJob: async (token: string, savedJobData: SavedJobRequest): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/saved-jobs`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(savedJobData),
    });
    
    return handleApplicationResponse<any>(response);
  },

  // Get all saved jobs
  getSavedJobs: async (token: string): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/saved-jobs`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleApplicationResponse<any[]>(response);
  },

  // Remove a saved job
  removeSavedJob: async (token: string, savedJobId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/saved-jobs/${savedJobId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleApplicationResponse<any>(response);
  },

  // ===== SAVED PROJECTS =====
  
  // Save a project
  saveProject: async (token: string, savedProjectData: SavedProjectRequest): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/saved-projects`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(savedProjectData),
    });
    
    return handleApplicationResponse<any>(response);
  },

  // Get all saved projects
  getSavedProjects: async (token: string): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/saved-projects`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleApplicationResponse<any[]>(response);
  },

  // Remove a saved project
  removeSavedProject: async (token: string, savedProjectId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/saved-projects/${savedProjectId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleApplicationResponse<any>(response);
  },

  // ===== UTILITY FUNCTIONS =====
  
  // Check if user has applied to a job
  hasAppliedToJob: async (token: string, jobId: string): Promise<boolean> => {
    try {
      const applications = await completeApplicationsApi.getMyJobApplications(token);
      return applications?.some((app: any) => app.job_id === jobId) ?? false;
    } catch (error) {
      console.error('Error checking job application status:', error);
      return false;
    }
  },

  // Check if user has applied to a project
  hasAppliedToProject: async (token: string, projectId: string): Promise<boolean> => {
    try {
      const applications = await completeApplicationsApi.getMyProjectApplications(token);
      return applications?.some((app: any) => app.project_id === projectId) ?? false;
    } catch (error) {
      console.error('Error checking project application status:', error);
      return false;
    }
  },

  // Check if user has saved a job
  hasSavedJob: async (token: string, jobId: string): Promise<boolean> => {
    try {
      const savedJobs = await completeApplicationsApi.getSavedJobs(token);
      return savedJobs?.some((saved: any) => saved.job_id === jobId) ?? false;
    } catch (error) {
      console.error('Error checking saved job status:', error);
      return false;
    }
  },

  // Check if user has saved a project
  hasSavedProject: async (token: string, projectId: string): Promise<boolean> => {
    try {
      const savedProjects = await completeApplicationsApi.getSavedProjects(token);
      return savedProjects?.some((saved: any) => saved.project_id === projectId) ?? false;
    } catch (error) {
      console.error('Error checking saved project status:', error);
      return false;
    }
  },
};

export default completeApplicationsApi; 