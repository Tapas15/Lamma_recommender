// Base URL for the API - using localhost:8000 for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// ML API Interfaces
export interface SkillCluster {
  cluster_id: string;
  cluster_name: string;
  core_skills: string[];
  related_skills: string[];
  confidence_score: number;
  skill_relationships: {
    [skill: string]: {
      relevance_score: number;
      co_occurrence_frequency: number;
      market_demand: 'high' | 'medium' | 'low';
    };
  };
  industry_relevance: {
    [industry: string]: number;
  };
  growth_rate: number;
  average_salary_impact: number;
}

export interface SkillClustersResponse {
  clusters: SkillCluster[];
  total_clusters: number;
  clustering_metadata: {
    algorithm_used: string;
    confidence_threshold: number;
    last_updated: string;
    data_sources: string[];
  };
  skill_statistics: {
    total_skills_analyzed: number;
    most_connected_skill: string;
    emerging_skills: string[];
    declining_skills: string[];
  };
}

export interface MarketTrend {
  skill: string;
  trend_direction: 'rising' | 'stable' | 'declining';
  growth_rate: number;
  demand_score: number;
  supply_score: number;
  salary_impact: number;
  geographic_distribution: {
    [location: string]: {
      demand: number;
      avg_salary: number;
      job_count: number;
    };
  };
  industry_breakdown: {
    [industry: string]: {
      demand_percentage: number;
      growth_rate: number;
    };
  };
  predictions: {
    next_quarter: number;
    next_year: number;
    confidence_level: number;
  };
}

export interface MarketTrendsResponse {
  trends: MarketTrend[];
  analysis_period: {
    start_date: string;
    end_date: string;
    data_points: number;
  };
  market_insights: {
    fastest_growing_skills: string[];
    highest_demand_skills: string[];
    highest_paying_skills: string[];
    emerging_technologies: string[];
  };
  predictions: {
    market_outlook: 'bullish' | 'bearish' | 'stable';
    key_trends: string[];
    recommendation_summary: string;
  };
}

export interface MLLearningRecommendation {
  recommendation_id: string;
  recommended_skill: string;
  priority: 'high' | 'medium' | 'low';
  learning_path: {
    step: number;
    skill: string;
    estimated_time_weeks: number;
    prerequisites: string[];
    resources: {
      type: 'course' | 'book' | 'project' | 'certification';
      title: string;
      provider: string;
      difficulty: 'beginner' | 'intermediate' | 'advanced';
      duration: string;
      rating: number;
      url?: string;
      cost?: number;
    }[];
  }[];
  career_impact: {
    salary_increase_potential: number;
    job_opportunities_increase: number;
    career_advancement_probability: number;
    industry_relevance: string[];
  };
  personalization_factors: {
    current_skill_level: string;
    learning_style: string[];
    time_availability: string;
    career_goals: string[];
  };
  confidence_score: number;
}

export interface MLLearningRecommendationsResponse {
  recommendations: MLLearningRecommendation[];
  personalization_metadata: {
    user_profile_completeness: number;
    recommendation_confidence: number;
    last_updated: string;
  };
  learning_insights: {
    total_estimated_time_weeks: number;
    skill_gap_analysis: {
      critical_gaps: string[];
      improvement_areas: string[];
      strengths: string[];
    };
    career_trajectory: {
      current_level: string;
      target_level: string;
      estimated_progression_time: string;
    };
  };
}

export interface SkillClustersFilters {
  confidence_threshold?: number;
  include_emerging?: boolean;
  industry_filter?: string;
  min_cluster_size?: number;
  max_clusters?: number;
}

export interface MarketTrendsFilters {
  time_period?: '1m' | '3m' | '6m' | '1y' | '2y';
  skill_categories?: string[];
  geographic_scope?: string[];
  industry_filter?: string;
  trend_direction?: 'rising' | 'stable' | 'declining';
}

export interface MLLearningFilters {
  target_role?: string;
  experience_level?: 'beginner' | 'intermediate' | 'advanced';
  time_commitment?: 'low' | 'medium' | 'high';
  learning_style?: 'visual' | 'auditory' | 'kinesthetic' | 'reading';
  budget_range?: 'free' | 'low' | 'medium' | 'high';
}

// Helper function for handling responses
async function handleMLResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`ML API failed: ${response.status} - ${errorData.detail || response.statusText}`);
  }
  
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json() as T;
  }
  
  return {} as T;
}

// Machine Learning API
export const mlApi = {
  // Get skill clusters analysis
  getSkillClusters: async (filters?: SkillClustersFilters): Promise<SkillClustersResponse> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/ml/skills/clusters?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return handleMLResponse<SkillClustersResponse>(response);
  },

  // Get market trends analysis
  getMarketTrends: async (filters?: MarketTrendsFilters): Promise<MarketTrendsResponse> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/ml/market-trends?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return handleMLResponse<MarketTrendsResponse>(response);
  },

  // Get ML-based learning recommendations (authenticated)
  getLearningRecommendations: async (token: string, filters?: MLLearningFilters): Promise<MLLearningRecommendationsResponse> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/ml/learning-recommendations?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleMLResponse<MLLearningRecommendationsResponse>(response);
  },

  // Get ML-based learning recommendations (public)
  getLearningRecommendationsPublic: async (filters?: MLLearningFilters): Promise<MLLearningRecommendationsResponse> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/ml/learning-recommendations-public?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return handleMLResponse<MLLearningRecommendationsResponse>(response);
  },
};

export default mlApi; 