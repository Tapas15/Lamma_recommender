// Base URL for the API - using localhost:8000 for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Enhanced Career API Interfaces
export interface CareerStep {
  role: string;
  timeline: string;
  description: string;
  skills: string[];
  skill_requirements: {
    technical: string[];
    soft: string[];
  };
  average_salary?: number;
  difficulty_level?: number;
  prerequisites: string[];
  typical_responsibilities: string[];
  advancement_criteria: string[];
}

export interface CareerTrack {
  name: string;
  description: string;
  average_time_years: number;
  salary_growth_percentage: number;
  difficulty: number;
  steps: CareerStep[];
  market_demand: 'high' | 'medium' | 'low';
  growth_outlook: 'excellent' | 'good' | 'moderate' | 'limited';
  recommended_certifications: string[];
  industry_relevance: string[];
}

export interface EnhancedCareerPathsResponse {
  current_role: string;
  industry: string;
  timeframe_years: number;
  career_tracks: {
    [trackName: string]: CareerTrack;
  };
  personalized_recommendations: {
    best_fit_track: string;
    reasoning: string;
    skill_gaps: string[];
    immediate_next_steps: string[];
    long_term_goals: string[];
  };
  market_insights: {
    highest_demand_roles: string[];
    fastest_growing_roles: string[];
    highest_paying_roles: string[];
    emerging_roles: string[];
  };
  skill_development_plan: {
    priority_skills: Array<{
      skill: string;
      importance: 'critical' | 'important' | 'nice-to-have';
      estimated_learning_time: string;
      recommended_resources: Array<{
        type: 'course' | 'certification' | 'project' | 'book';
        title: string;
        provider?: string;
        duration?: string;
        difficulty?: 'beginner' | 'intermediate' | 'advanced';
      }>;
    }>;
  };
  salary_projections: {
    [year: number]: {
      conservative_estimate: number;
      optimistic_estimate: number;
      market_average: number;
    };
  };
  networking_suggestions: {
    professional_organizations: string[];
    key_conferences: string[];
    influential_people_to_follow: string[];
    relevant_communities: string[];
  };
}

export interface EnhancedCareerPathsFilters {
  current_role?: string;
  industry?: string;
  timeframe_years?: number;
  include_skill_requirements?: boolean;
  include_salary_data?: boolean;
  experience_level?: 'entry' | 'mid' | 'senior' | 'executive';
  location_preference?: string;
  work_style_preference?: 'remote' | 'hybrid' | 'onsite';
  career_goals?: 'leadership' | 'technical_expert' | 'entrepreneurship' | 'consulting';
}

// Helper function for handling responses
async function handleEnhancedCareerResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`Enhanced Career API failed: ${response.status} - ${errorData.detail || response.statusText}`);
  }
  
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json() as T;
  }
  
  return {} as T;
}

// Enhanced Career Paths API
export const enhancedCareerApi = {
  // Get enhanced career path recommendations
  getEnhancedCareerPaths: async (token: string, filters?: EnhancedCareerPathsFilters): Promise<EnhancedCareerPathsResponse> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/recommendations/career-paths?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleEnhancedCareerResponse<EnhancedCareerPathsResponse>(response);
  },

  // Get public career path information (no authentication required)
  getPublicCareerPaths: async (filters?: EnhancedCareerPathsFilters): Promise<EnhancedCareerPathsResponse> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/recommendations/career-paths/public?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return handleEnhancedCareerResponse<EnhancedCareerPathsResponse>(response);
  },

  // Get career progression analytics
  getCareerProgressionAnalytics: async (token: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/career-paths/analytics`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleEnhancedCareerResponse<any>(response);
  },

  // Get industry-specific career paths
  getIndustryCareerPaths: async (industry: string, filters?: EnhancedCareerPathsFilters): Promise<EnhancedCareerPathsResponse> => {
    const queryParams = filters ? new URLSearchParams({ ...filters, industry } as any) : new URLSearchParams({ industry });
    const response = await fetch(`${API_BASE_URL}/recommendations/career-paths/industry?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return handleEnhancedCareerResponse<EnhancedCareerPathsResponse>(response);
  },
};

export default enhancedCareerApi; 