'use client';

import React, { useState, useEffect } from 'react';
import { systemApi, HealthStatus, JobRole, Industry } from '../services/systemApi';
import { analyticsApi, RecommendationImpactAnalytics } from '../services/analyticsApi';
import { feedbackApi, FeedbackSummary, RecommendationFeedbackRequest } from '../services/feedbackApi';

export default function SystemDashboard() {
  const [activeTab, setActiveTab] = useState('system');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // System data
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [jobRoles, setJobRoles] = useState<JobRole[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);

  // Analytics data
  const [analyticsData, setAnalyticsData] = useState<RecommendationImpactAnalytics | null>(null);

  // Feedback data
  const [feedbackSummary, setFeedbackSummary] = useState<FeedbackSummary | null>(null);
  const [feedbackForm, setFeedbackForm] = useState<RecommendationFeedbackRequest>({
    recommendation_id: '',
    recommendation_type: 'job',
    relevance_score: 3,
    accuracy_score: 3,
    is_helpful: true,
    feedback_text: '',
    action_taken: 'viewed_details'
  });

  useEffect(() => {
    loadSystemData();
  }, []);

  const loadSystemData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load system health (no auth required)
      const health = await systemApi.getHealth();
      setHealthStatus(health);

      // Load job roles and industries (no auth required)
      const [rolesData, industriesData] = await Promise.all([
        systemApi.getJobRoles(),
        systemApi.getIndustries()
      ]);
      setJobRoles(rolesData);
      setIndustries(industriesData);

    } catch (error: any) {
      console.error('Error loading system data:', error);
      setError(error.message || 'Failed to load system data');
    } finally {
      setLoading(false);
    }
  };

  const loadAnalyticsData = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authentication required for analytics data');
      return;
    }

    setLoading(true);
    try {
      const analytics = await analyticsApi.getRecommendationImpact(token);
      setAnalyticsData(analytics);
      setError(null);
    } catch (error: any) {
      console.error('Error loading analytics:', error);
      setError(error.message || 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const loadFeedbackData = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authentication required for feedback data');
      return;
    }

    setLoading(true);
    try {
      const feedback = await feedbackApi.getFeedbackSummary(token);
      setFeedbackSummary(feedback);
      setError(null);
    } catch (error: any) {
      console.error('Error loading feedback:', error);
      setError(error.message || 'Failed to load feedback data');
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authentication required to submit feedback');
      return;
    }

    if (!feedbackForm.recommendation_id.trim()) {
      setError('Please enter a recommendation ID');
      return;
    }

    try {
      await feedbackApi.submitFeedback(token, feedbackForm);
      setError(null);
      alert('Feedback submitted successfully!');
      
      // Reset form
      setFeedbackForm({
        recommendation_id: '',
        recommendation_type: 'job',
        relevance_score: 3,
        accuracy_score: 3,
        is_helpful: true,
        feedback_text: '',
        action_taken: 'viewed_details'
      });
      
      // Reload feedback data
      loadFeedbackData();
    } catch (error: any) {
      console.error('Error submitting feedback:', error);
      setError(error.message || 'Failed to submit feedback');
    }
  };

  const tabs = [
    { id: 'system', label: '🏥 System Health', action: loadSystemData },
    { id: 'analytics', label: '📊 Analytics', action: loadAnalyticsData },
    { id: 'feedback', label: '💬 Feedback', action: loadFeedbackData },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold mb-4 text-gray-800">
        🚀 System Dashboard - New API Integration
      </h3>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id);
                tab.action();
              }}
              className={`py-2 px-4 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-2">Loading...</span>
        </div>
      )}

      {/* System Health Tab */}
      {activeTab === 'system' && !loading && (
        <div className="space-y-6">
          {/* Health Status */}
          {healthStatus && (
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="text-lg font-semibold mb-2 text-green-800">System Health</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                    healthStatus.status === 'healthy' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {healthStatus.status === 'healthy' ? '✅' : '❌'} {healthStatus.status}
                  </span>
                </div>
                <div className="text-sm text-green-700">
                  Last check: {new Date(healthStatus.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          )}

          {/* Job Roles */}
          <div>
            <h4 className="text-lg font-semibold mb-3">Available Job Roles ({jobRoles.length})</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-48 overflow-y-auto">
              {jobRoles.map((role) => (
                <div key={role.id} className="bg-blue-50 p-3 rounded border">
                  <div className="font-medium text-blue-900">{role.title}</div>
                  <div className="text-sm text-blue-600">{role.category}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Industries */}
          <div>
            <h4 className="text-lg font-semibold mb-3">Available Industries ({industries.length})</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-48 overflow-y-auto">
              {industries.map((industry) => (
                <div key={industry.id} className="bg-purple-50 p-3 rounded border">
                  <div className="font-medium text-purple-900">{industry.name}</div>
                  {industry.category && (
                    <div className="text-sm text-purple-600">{industry.category}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && !loading && (
        <div className="space-y-6">
          {analyticsData ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {analyticsData.total_recommendations_generated}
                  </div>
                  <div className="text-sm text-blue-800">Total Recommendations</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {(analyticsData.user_engagement.click_through_rate * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-green-800">Click Through Rate</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {analyticsData.success_metrics.successful_matches}
                  </div>
                  <div className="text-sm text-purple-800">Successful Matches</div>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-orange-600">
                    {analyticsData.success_metrics.user_satisfaction_score.toFixed(1)}/5
                  </div>
                  <div className="text-sm text-orange-800">Satisfaction Score</div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-2">Recommendations by Type</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  {Object.entries(analyticsData.recommendations_by_type).map(([type, count]) => (
                    <div key={type} className="text-center">
                      <div className="font-bold text-lg">{count}</div>
                      <div className="text-gray-600">{type.replace('_', ' ')}</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">📊</div>
              <p>Click "Analytics" tab to load recommendation impact data</p>
              <p className="text-sm">Requires authentication</p>
            </div>
          )}
        </div>
      )}

      {/* Feedback Tab */}
      {activeTab === 'feedback' && !loading && (
        <div className="space-y-6">
          {/* Submit Feedback Form */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-3">Submit Recommendation Feedback</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Recommendation ID *
                </label>
                <input
                  type="text"
                  value={feedbackForm.recommendation_id}
                  onChange={(e) => setFeedbackForm({...feedbackForm, recommendation_id: e.target.value})}
                  placeholder="Enter recommendation ID"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Recommendation Type
                </label>
                <select
                  value={feedbackForm.recommendation_type}
                  onChange={(e) => setFeedbackForm({...feedbackForm, recommendation_type: e.target.value as any})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="job">Job</option>
                  <option value="candidate">Candidate</option>
                  <option value="project">Project</option>
                  <option value="skill">Skill</option>
                  <option value="career_path">Career Path</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Relevance Score (1-5)
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={feedbackForm.relevance_score}
                  onChange={(e) => setFeedbackForm({...feedbackForm, relevance_score: Number(e.target.value)})}
                  className="w-full"
                />
                <div className="text-center text-sm text-gray-600">{feedbackForm.relevance_score}/5</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Accuracy Score (1-5)
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={feedbackForm.accuracy_score}
                  onChange={(e) => setFeedbackForm({...feedbackForm, accuracy_score: Number(e.target.value)})}
                  className="w-full"
                />
                <div className="text-center text-sm text-gray-600">{feedbackForm.accuracy_score}/5</div>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Feedback Text (Optional)
                </label>
                <textarea
                  value={feedbackForm.feedback_text}
                  onChange={(e) => setFeedbackForm({...feedbackForm, feedback_text: e.target.value})}
                  placeholder="Share your thoughts about this recommendation..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <button
              onClick={submitFeedback}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Submit Feedback
            </button>
          </div>

          {/* Feedback Summary */}
          {feedbackSummary ? (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-3">Feedback Summary</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-800">
                    {feedbackSummary.total_feedback_count}
                  </div>
                  <div className="text-sm text-gray-600">Total Feedback</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {feedbackSummary.average_scores.relevance.toFixed(1)}/5
                  </div>
                  <div className="text-sm text-gray-600">Avg Relevance</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {feedbackSummary.average_scores.accuracy.toFixed(1)}/5
                  </div>
                  <div className="text-sm text-gray-600">Avg Accuracy</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">💬</div>
              <p>Click "Feedback" tab to load feedback analytics</p>
              <p className="text-sm">Requires authentication</p>
            </div>
          )}
        </div>
      )}

      {/* API Information */}
      <div className="mt-8 p-4 bg-yellow-50 rounded-lg">
        <h5 className="font-medium text-yellow-800 mb-2">🆕 New API Integrations</h5>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <h6 className="font-medium text-yellow-700 mb-2">System APIs</h6>
            <ul className="text-yellow-600 space-y-1">
              <li>• <code>GET /health</code></li>
              <li>• <code>GET /job-roles</code></li>
              <li>• <code>GET /industries</code></li>
              <li>• <code>GET /employer/{'{id}'}</code></li>
              <li>• <code>DELETE /profile</code></li>
            </ul>
          </div>
          <div>
            <h6 className="font-medium text-yellow-700 mb-2">Analytics APIs</h6>
            <ul className="text-yellow-600 space-y-1">
              <li>• <code>GET /analytics/recommendations/impact</code></li>
              <li>• <code>GET /analytics/users/{'{id}'}</code></li>
              <li>• <code>GET /analytics/system</code></li>
              <li>• <code>GET /analytics/trends</code></li>
            </ul>
          </div>
          <div>
            <h6 className="font-medium text-yellow-700 mb-2">Feedback APIs</h6>
            <ul className="text-yellow-600 space-y-1">
              <li>• <code>POST /recommendations/feedback</code></li>
              <li>• <code>GET /recommendations/feedback/summary</code></li>
              <li>• <code>GET /recommendations/feedback/analytics</code></li>
              <li>• <code>PUT /recommendations/feedback/{'{id}'}</code></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
} 