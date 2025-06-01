// Base URL for the API - using localhost:8000 for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// System API Interfaces
export interface JobRole {
  id: string;
  title: string;
  category: string;
}

export interface Industry {
  id: string;
  name: string;
  category?: string;
  description?: string;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  database?: string;
  version?: string;
  uptime?: string;
}

export interface EmployerProfile {
  id: string;
  email: string;
  full_name: string;
  user_type: 'employer';
  company_details?: {
    company_name: string;
    industry?: string;
    company_location?: string;
    company_size?: string;
    company_website?: string;
    company_description?: string;
  };
  hiring_preferences?: {
    job_roles_hiring?: string[];
    remote_friendly?: boolean;
  };
  [key: string]: any;
}

export interface EmployerProjectsFilters {
  status?: 'active' | 'completed' | 'paused' | 'cancelled';
  created_after?: string;
  created_before?: string;
  budget_min?: number;
  budget_max?: number;
}

// Helper function for handling responses
async function handleSystemResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`System API failed: ${response.status} - ${errorData.detail || response.statusText}`);
  }
  
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json() as T;
  }
  
  return {} as T;
}

// System Utilities API
export const systemApi = {
  // Health check endpoint
  getHealth: async (): Promise<HealthStatus> => {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return handleSystemResponse<HealthStatus>(response);
  },

  // Get job roles list
  getJobRoles: async (): Promise<JobRole[]> => {
    const response = await fetch(`${API_BASE_URL}/job-roles`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return handleSystemResponse<JobRole[]>(response);
  },

  // Get industries list
  getIndustries: async (): Promise<Industry[]> => {
    const response = await fetch(`${API_BASE_URL}/industries`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return handleSystemResponse<Industry[]>(response);
  },

  // Get employer profile by ID
  getEmployerProfile: async (employerId: string): Promise<EmployerProfile> => {
    const response = await fetch(`${API_BASE_URL}/employer/${employerId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return handleSystemResponse<EmployerProfile>(response);
  },

  // Get employer's projects (for employers only)
  getEmployerProjects: async (token: string, filters?: EmployerProjectsFilters): Promise<any[]> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/employer-projects?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleSystemResponse<any[]>(response);
  },

  // Get specific project by ID
  getProjectById: async (token: string, projectId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleSystemResponse<any>(response);
  },

  // Delete user profile (advanced profile management)
  deleteProfile: async (token: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/profile`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleSystemResponse<any>(response);
  },

  // Alternative PATCH endpoint for profile updates
  patchProfile: async (token: string, profileData: any): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/profile`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });
    
    return handleSystemResponse<any>(response);
  },
};

export default systemApi; 