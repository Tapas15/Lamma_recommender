/**
 * API service for connecting to the FastAPI backend
 */

// Base URL for the API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  email: string;
  user_type: string;
  full_name?: string;
  [key: string]: any;
}

// API error class
export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// Helper function to handle API responses
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      errorData = { detail: 'Unknown error' };
    }
    
    const errorMessage = errorData.detail || `API error: ${response.status}`;
    throw new ApiError(errorMessage, response.status, errorData);
  }
  
  // Check if response is empty
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json() as T;
  }
  
  return {} as T;
}

// Authentication API
export const authApi = {
  // Login and get token
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await fetch(`${API_BASE_URL}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });
    
    return handleResponse<TokenResponse>(response);
  },
  
  // Get user profile
  getProfile: async (token: string): Promise<UserProfile> => {
    const response = await fetch(`${API_BASE_URL}/profile`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleResponse<UserProfile>(response);
  },
};

// Jobs API
export const jobsApi = {
  // Get all jobs
  getJobs: async (token: string): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/jobs`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleResponse<any[]>(response);
  },
  
  // Get job by ID
  getJob: async (token: string, jobId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleResponse<any>(response);
  },
  
  // Create job
  createJob: async (token: string, jobData: any): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/jobs`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jobData),
    });
    
    return handleResponse<any>(response);
  },
};

// Recommendations API
export const recommendationsApi = {
  // Get job recommendations for a candidate
  getJobRecommendations: async (token: string): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/jobs`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleResponse<any[]>(response);
  },
  
  // Get candidate recommendations for a job
  getCandidateRecommendations: async (token: string, jobId: string): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/candidates/${jobId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleResponse<any[]>(response);
  },
  
  // Submit feedback for a recommendation
  submitFeedback: async (token: string, feedbackData: any): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/feedback`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedbackData),
    });
    
    return handleResponse<any>(response);
  },
};

// Skill Gap Analysis API
export const skillGapApi = {
  // Get skill gap analysis for a candidate and job
  getSkillGapAnalysis: async (token: string, jobId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/skill-gap/${jobId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleResponse<any>(response);
  },
};

// Career Paths API
export const careerPathsApi = {
  // Get career path recommendations
  getCareerPaths: async (token: string): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/career-paths`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleResponse<any[]>(response);
  },
};

// Projects API
export const projectsApi = {
  // Get all projects
  getProjects: async (token: string): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/projects`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleResponse<any[]>(response);
  },
  
  // Get project by ID
  getProject: async (token: string, projectId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleResponse<any>(response);
  },
  
  // Create project
  createProject: async (token: string, projectData: any): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(projectData),
    });
    
    return handleResponse<any>(response);
  },
}; 