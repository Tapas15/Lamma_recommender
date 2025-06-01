// Base URL for the API - using localhost:8000 for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Analytics API Interfaces
export interface RecommendationImpactAnalytics {
  total_recommendations_generated: number;
  recommendations_by_type: {
    job_recommendations: number;
    candidate_recommendations: number;
    project_recommendations: number;
    skill_recommendations: number;
  };
  user_engagement: {
    click_through_rate: number;
    application_rate: number;
    save_rate: number;
    avg_time_spent: number;
  };
  success_metrics: {
    successful_matches: number;
    hirings_from_recommendations: number;
    project_completions: number;
    user_satisfaction_score: number;
  };
  trends: {
    daily_recommendations: Array<{
      date: string;
      count: number;
      success_rate: number;
    }>;
    popular_skills: string[];
    top_industries: string[];
  };
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
}

export interface UserAnalytics {
  user_id: string;
  user_type: 'candidate' | 'employer';
  activity_summary: {
    profile_views: number;
    applications_sent: number;
    recommendations_received: number;
    jobs_saved: number;
    projects_saved: number;
  };
  engagement_metrics: {
    login_frequency: number;
    avg_session_duration: number;
    last_active: string;
    feature_usage: {
      search_usage: number;
      recommendation_clicks: number;
      profile_updates: number;
    };
  };
  performance_metrics?: {
    application_success_rate?: number;
    response_rate?: number;
    recommendation_accuracy?: number;
  };
}

export interface SystemAnalytics {
  total_users: {
    candidates: number;
    employers: number;
    total: number;
  };
  content_metrics: {
    total_jobs: number;
    active_jobs: number;
    total_projects: number;
    active_projects: number;
  };
  activity_metrics: {
    daily_active_users: number;
    weekly_active_users: number;
    monthly_active_users: number;
  };
  performance_metrics: {
    avg_response_time: number;
    success_rate: number;
    error_rate: number;
  };
}

export interface AnalyticsFilters {
  start_date?: string;
  end_date?: string;
  user_type?: 'candidate' | 'employer';
  recommendation_type?: 'job' | 'candidate' | 'project' | 'skill';
  industry?: string;
  location?: string;
}

// Helper function for handling responses
async function handleAnalyticsResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`Analytics API failed: ${response.status} - ${errorData.detail || response.statusText}`);
  }
  
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json() as T;
  }
  
  return {} as T;
}

// Analytics API
export const analyticsApi = {
  // Get recommendation impact analytics
  getRecommendationImpact: async (token: string, filters?: AnalyticsFilters): Promise<RecommendationImpactAnalytics> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/analytics/recommendations/impact?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleAnalyticsResponse<RecommendationImpactAnalytics>(response);
  },

  // Get user-specific analytics
  getUserAnalytics: async (token: string, userId?: string): Promise<UserAnalytics> => {
    const endpoint = userId 
      ? `${API_BASE_URL}/analytics/users/${userId}`
      : `${API_BASE_URL}/analytics/profile`;
      
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleAnalyticsResponse<UserAnalytics>(response);
  },

  // Get system-wide analytics (admin only)
  getSystemAnalytics: async (token: string, filters?: AnalyticsFilters): Promise<SystemAnalytics> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/analytics/system?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleAnalyticsResponse<SystemAnalytics>(response);
  },

  // Get recommendation trends
  getRecommendationTrends: async (token: string, filters?: AnalyticsFilters): Promise<any> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/analytics/recommendations/trends?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleAnalyticsResponse<any>(response);
  },

  // Get user engagement analytics
  getUserEngagement: async (token: string, filters?: AnalyticsFilters): Promise<any> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/analytics/engagement?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleAnalyticsResponse<any>(response);
  },

  // Get content performance analytics
  getContentAnalytics: async (token: string, contentType: 'jobs' | 'projects', filters?: AnalyticsFilters): Promise<any> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/analytics/${contentType}?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleAnalyticsResponse<any>(response);
  },

  // Get skill analytics and trends
  getSkillAnalytics: async (token: string, filters?: AnalyticsFilters): Promise<any> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/analytics/skills?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleAnalyticsResponse<any>(response);
  },
};

export default analyticsApi; 