// Base URL for the API - using localhost:8000 for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Search interfaces
export interface SearchFilters {
  location?: string;
  salary_min?: number;
  salary_max?: number;
  experience_level?: string;
  employment_type?: string;
  remote_option?: boolean;
  company_size?: string;
  industry?: string;
  required_skills?: string[];
  [key: string]: any;
}

export interface JobSearchRequest {
  query?: string;
  filters?: SearchFilters;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface ProjectSearchRequest {
  query?: string;
  filters?: {
    budget_min?: number;
    budget_max?: number;
    duration?: string;
    project_type?: string;
    required_skills?: string[];
    location?: string;
    remote_option?: boolean;
    [key: string]: any;
  };
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface CandidateSearchRequest {
  query?: string;
  filters?: {
    location?: string;
    experience_level?: string;
    skills?: string[];
    availability?: string;
    salary_expectation_min?: number;
    salary_expectation_max?: number;
    remote_preference?: string;
    [key: string]: any;
  };
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// Helper function for handling responses
async function handleSearchResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`Search failed: ${response.status} - ${errorData.detail || response.statusText}`);
  }
  
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json() as T;
  }
  
  return {} as T;
}

// Enhanced Search API
export const searchApi = {
  // Search jobs with advanced filters
  searchJobs: async (token: string, searchRequest: JobSearchRequest): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/jobs/search`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchRequest),
    });
    
    return handleSearchResponse<any[]>(response);
  },

  // Search projects with advanced filters
  searchProjects: async (token: string, searchRequest: ProjectSearchRequest): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/projects/search`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchRequest),
    });
    
    return handleSearchResponse<any[]>(response);
  },

  // Search candidates with advanced filters (for employers)
  searchCandidates: async (token: string, searchRequest: CandidateSearchRequest): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/candidates/search`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchRequest),
    });
    
    return handleSearchResponse<any[]>(response);
  },
};

export default searchApi; 