// Base URL for the API - using localhost:8000 for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Feedback API Interfaces
export interface RecommendationFeedbackRequest {
  recommendation_id: string;
  recommendation_type: 'job' | 'candidate' | 'project' | 'skill' | 'career_path';
  relevance_score: number; // 1-5 scale
  accuracy_score: number; // 1-5 scale
  is_helpful?: boolean;
  feedback_text?: string;
  action_taken?: 'viewed_details' | 'applied' | 'saved' | 'dismissed' | 'contacted' | 'shared';
}

export interface RecommendationFeedbackResponse {
  status: 'success' | 'error';
  message: string;
  feedback_id: string;
  timestamp: string;
}

export interface FeedbackSummary {
  total_feedback_count: number;
  average_scores: {
    relevance: number;
    accuracy: number;
    helpfulness_rate: number;
  };
  feedback_by_type: {
    [key: string]: {
      count: number;
      avg_relevance: number;
      avg_accuracy: number;
    };
  };
  common_actions: {
    action: string;
    count: number;
    percentage: number;
  }[];
  recent_feedback: Array<{
    feedback_id: string;
    recommendation_type: string;
    relevance_score: number;
    accuracy_score: number;
    timestamp: string;
    feedback_text?: string;
  }>;
  trends: {
    daily_feedback: Array<{
      date: string;
      count: number;
      avg_score: number;
    }>;
  };
}

export interface DetailedFeedback {
  feedback_id: string;
  user_id: string;
  recommendation_id: string;
  recommendation_type: string;
  relevance_score: number;
  accuracy_score: number;
  is_helpful: boolean;
  feedback_text?: string;
  action_taken?: string;
  timestamp: string;
  user_context?: {
    user_type: 'candidate' | 'employer';
    experience_level?: string;
    industry?: string;
  };
}

export interface FeedbackFilters {
  start_date?: string;
  end_date?: string;
  recommendation_type?: 'job' | 'candidate' | 'project' | 'skill' | 'career_path';
  min_score?: number;
  max_score?: number;
  user_type?: 'candidate' | 'employer';
  has_text_feedback?: boolean;
}

export interface BulkFeedbackRequest {
  feedback_items: RecommendationFeedbackRequest[];
}

// Helper function for handling responses
async function handleFeedbackResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`Feedback API failed: ${response.status} - ${errorData.detail || response.statusText}`);
  }
  
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json() as T;
  }
  
  return {} as T;
}

// Recommendation Feedback API
export const feedbackApi = {
  // Submit feedback for a recommendation
  submitFeedback: async (token: string, feedbackData: RecommendationFeedbackRequest): Promise<RecommendationFeedbackResponse> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/feedback`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedbackData),
    });
    
    return handleFeedbackResponse<RecommendationFeedbackResponse>(response);
  },

  // Submit bulk feedback for multiple recommendations
  submitBulkFeedback: async (token: string, bulkFeedbackData: BulkFeedbackRequest): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/feedback/bulk`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bulkFeedbackData),
    });
    
    return handleFeedbackResponse<any>(response);
  },

  // Get feedback summary/analytics
  getFeedbackSummary: async (token: string, filters?: FeedbackFilters): Promise<FeedbackSummary> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/recommendations/feedback/summary?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleFeedbackResponse<FeedbackSummary>(response);
  },

  // Get detailed feedback analytics (admin/system level)
  getFeedbackAnalytics: async (token: string, filters?: FeedbackFilters): Promise<any> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/recommendations/feedback/analytics?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleFeedbackResponse<any>(response);
  },

  // Get user's own feedback history
  getUserFeedbackHistory: async (token: string, filters?: FeedbackFilters): Promise<DetailedFeedback[]> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/recommendations/feedback/user?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleFeedbackResponse<DetailedFeedback[]>(response);
  },

  // Get feedback for a specific recommendation
  getRecommendationFeedback: async (token: string, recommendationId: string): Promise<DetailedFeedback[]> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/${recommendationId}/feedback`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleFeedbackResponse<DetailedFeedback[]>(response);
  },

  // Update existing feedback
  updateFeedback: async (token: string, feedbackId: string, updateData: Partial<RecommendationFeedbackRequest>): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/feedback/${feedbackId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateData),
    });
    
    return handleFeedbackResponse<any>(response);
  },

  // Delete feedback
  deleteFeedback: async (token: string, feedbackId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/recommendations/feedback/${feedbackId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleFeedbackResponse<any>(response);
  },

  // Get feedback trends and insights
  getFeedbackTrends: async (token: string, filters?: FeedbackFilters): Promise<any> => {
    const queryParams = filters ? new URLSearchParams(filters as any) : '';
    const response = await fetch(`${API_BASE_URL}/recommendations/feedback/trends?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    return handleFeedbackResponse<any>(response);
  },
};

export default feedbackApi; 