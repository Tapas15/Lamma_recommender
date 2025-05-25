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

export interface CandidateRegistrationRequest {
  email: string;
  password: string;
  full_name: string;
  phone?: string | null;
  location?: string | null;
  bio?: string | null;
  skills?: {
    languages_frameworks?: string[];
    ai_ml_data?: string[];
    tools_platforms?: string[];
    soft_skills?: string[];
  };
  experience?: any[];
  education?: any[];
  [key: string]: any;
}

export interface EmployerRegistrationRequest {
  email: string;
  password: string;
  full_name: string;
  user_type: 'employer';
  company_details: {
    company_name: string;
    industry: string;
    company_location?: string | null;
    company_size?: string | null;
    company_website?: string | null;
    company_description?: string | null;
    [key: string]: any;
  };
  hiring_preferences?: {
    job_roles_hiring?: string[];
    remote_friendly?: boolean;
    [key: string]: any;
  };
  [key: string]: any;
}

export type RegistrationRequest = CandidateRegistrationRequest | EmployerRegistrationRequest;

export interface RegistrationResponse {
  user_id?: string;
  email?: string;
  user_type?: string;
  full_name?: string;
  message?: string;
  id?: string;
}

export interface CandidateProfileData {
  skills: Array<{
    name: string;
    proficiency: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  }>;
  education: Array<{
    institution: string;
    degree: string;
    field_of_study: string;
    start_date: string;
    end_date?: string;
    current?: boolean;
  }>;
  experience: Array<{
    company: string;
    title: string;
    description: string;
    start_date: string;
    end_date?: string;
    current?: boolean;
  }>;
  availability_hours?: number;
  remote_preference?: 'remote' | 'hybrid' | 'onsite';
  career_goals?: string;
  location?: string;
}

export interface EmployerProfileData {
  company_name: string;
  company_size: 'small' | 'medium' | 'large' | 'enterprise';
  industry: string;
  location: string;
  website?: string;
  description?: string;
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
  
  // Register a new user
  register: async (userData: RegistrationRequest): Promise<RegistrationResponse> => {
    const endpoint = userData.user_type === 'candidate' 
      ? `${API_BASE_URL}/register/candidate` 
      : `${API_BASE_URL}/register/employer`;
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    
    return handleResponse<RegistrationResponse>(response);
  },
  
  // Create candidate profile
  createCandidateProfile: async (token: string, profileData: CandidateProfileData): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/profile/candidate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });
    
    return handleResponse<any>(response);
  },
  
  // Create employer profile
  createEmployerProfile: async (token: string, profileData: EmployerProfileData): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/profile/employer`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });
    
    return handleResponse<any>(response);
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
  
  // Update user profile
  updateProfile: async (token: string, profileData: any): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/profile`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });
    
    return handleResponse<any>(response);
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