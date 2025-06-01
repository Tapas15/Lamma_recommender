// Base URL for the API - using localhost:8000 for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Advanced Recommendations Interfaces
export interface SkillGapAnalysis {
  candidate_skills: string[];
  required_skills: string[];
  missing_skills: string[];
  skill_gaps: Array<{
    skill: string;
    importance: 'high' | 'medium' | 'low';
    learning_resources?: string[];
  }>;
  match_percentage: number;
  recommendation_priority: string[];
}

export interface LearningRecommendation {
  skill: string;
  learning_path: string[];
  resources: Array<{
    title: string;
    type: 'course' | 'certification' | 'project' | 'book';
    provider: string;
    difficulty: 'beginner' | 'intermediate' | 'advanced';
    duration: string;
    url?: string;
    rating?: number;
  }>;
  estimated_completion_time: string;
  priority: 'high' | 'medium' | 'low';
}

export interface CareerPathRecommendation {
  current_role: string;
  target_roles: Array<{
    title: string;
    growth_potential: number;
    salary_range: {
      min: number;
      max: number;
    };
    required_skills: string[];
    experience_required: string;
    pathway_steps: string[];
  }>;
  recommended_next_steps: string[];
  timeline_months: number;
}

export interface TalentSearchRequest {
  job_requirements: {
    skills: string[];
    experience_level: string;
    location?: string;
    salary_range?: {
      min: number;
      max: number;
    };
  };
  search_criteria: {
    match_threshold?: number;
    include_partial_matches?: boolean;
    location_flexibility?: boolean;
  };
  ranking_preferences: {
    skill_weight: number;
    experience_weight: number;
    location_weight: number;
    availability_weight: number;
  };
}

export interface SalaryBenchmarkRequest {
  job_title: string;
  location: string;
  experience_level: string;
  skills: string[];
  company_size?: string;
  industry?: string;
}

export interface SalaryBenchmarkResponse {
  job_title: string;
  location: string;
  salary_range: {
    min: number;
    max: number;
    median: number;
    percentile_25: number;
    percentile_75: number;
  };
  market_trends: {
    growth_rate: number;
    demand_level: 'high' | 'medium' | 'low';
    competition_level: 'high' | 'medium' | 'low';
  };
  factors_analysis: Array<{
    factor: string;
    impact: 'positive' | 'negative' | 'neutral';
    weight: number;
  }>;
}

// Helper function for handling responses
async function handleAdvancedResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`Advanced API failed: ${response.status} - ${errorData.detail || response.statusText}`);
  }
  
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json() as T;
  }
  
  return {} as T;
}

// Advanced Recommendations API
export const advancedRecommendationsApi = {
  // Get skill gap analysis
  getSkillGapAnalysis: async (token: string, jobId?: string, targetRole?: string): Promise<SkillGapAnalysis> => {
    const params: any = {};
    if (jobId) params.job_id = jobId;
    if (targetRole) params.target_role = targetRole;
    
    const queryParams = new URLSearchParams(params);
    const response = await fetch(`${API_BASE_URL}/recommendations/skill-gap?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleAdvancedResponse<SkillGapAnalysis>(response);
  },

  // Get learning recommendations based on skill gaps
  getLearningRecommendations: async (token: string, skillGaps?: string[], targetRole?: string): Promise<LearningRecommendation[]> => {
    const params: any = {};
    if (skillGaps) params.skill_gaps = skillGaps.join(',');
    if (targetRole) params.target_role = targetRole;
    
    const queryParams = new URLSearchParams(params);
    const response = await fetch(`${API_BASE_URL}/recommendations/learning?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleAdvancedResponse<LearningRecommendation[]>(response);
  },

  // Get career path recommendations
  getCareerPathRecommendations: async (token: string, currentRole?: string): Promise<CareerPathRecommendation> => {
    const params = currentRole ? `?current_role=${encodeURIComponent(currentRole)}` : '';
    const response = await fetch(`${API_BASE_URL}/recommendations/career-path${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleAdvancedResponse<CareerPathRecommendation>(response);
  },

  // Get similar jobs for a specific job
  getSimilarJobs: async (token: string, jobId: string, limit: number = 5): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/similar-jobs/${jobId}?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleAdvancedResponse<any[]>(response);
  },

  // Advanced talent search for employers
  performTalentSearch: async (token: string, searchRequest: TalentSearchRequest): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/talent-search`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchRequest),
    });
    
    return handleAdvancedResponse<any>(response);
  },

  // Get salary benchmarking data
  getSalaryBenchmark: async (token: string, benchmarkRequest: SalaryBenchmarkRequest): Promise<SalaryBenchmarkResponse> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/salary`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(benchmarkRequest),
    });
    
    return handleAdvancedResponse<SalaryBenchmarkResponse>(response);
  },

  // Get general candidate recommendations (for employers)
  getCandidateRecommendations: async (token: string, filters?: any): Promise<any[]> => {
    const queryParams = filters ? new URLSearchParams(filters) : '';
    const response = await fetch(`${API_BASE_URL}/recommendations/candidates?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    return handleAdvancedResponse<any[]>(response);
  },
};

export default advancedRecommendationsApi; 