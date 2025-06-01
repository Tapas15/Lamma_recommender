'use client';

import React, { useState, useEffect } from 'react';
import { mlApi, SkillClustersResponse, MarketTrendsResponse, MLLearningRecommendationsResponse } from '../services/mlApi';
import { enhancedCareerApi, EnhancedCareerPathsResponse } from '../services/enhancedCareerApi';

export default function MLDashboard() {
  const [activeTab, setActiveTab] = useState('skills-clusters');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ML data states
  const [skillClusters, setSkillClusters] = useState<SkillClustersResponse | null>(null);
  const [marketTrends, setMarketTrends] = useState<MarketTrendsResponse | null>(null);
  const [mlLearningRecs, setMlLearningRecs] = useState<MLLearningRecommendationsResponse | null>(null);
  const [enhancedCareerPaths, setEnhancedCareerPaths] = useState<EnhancedCareerPathsResponse | null>(null);

  useEffect(() => {
    loadSkillClusters();
  }, []);

  const loadSkillClusters = async () => {
    setLoading(true);
    setError(null);

    try {
      const clusters = await mlApi.getSkillClusters({
        confidence_threshold: 0.7,
        include_emerging: true,
        max_clusters: 10
      });
      setSkillClusters(clusters);
    } catch (error: any) {
      console.error('Error loading skill clusters:', error);
      setError(error.message || 'Failed to load skill clusters');
    } finally {
      setLoading(false);
    }
  };

  const loadMarketTrends = async () => {
    setLoading(true);
    try {
      const trends = await mlApi.getMarketTrends({
        time_period: '1y',
        trend_direction: 'rising'
      });
      setMarketTrends(trends);
      setError(null);
    } catch (error: any) {
      console.error('Error loading market trends:', error);
      setError(error.message || 'Failed to load market trends');
    } finally {
      setLoading(false);
    }
  };

  const loadMLLearningRecommendations = async () => {
    const token = localStorage.getItem('token');
    
    setLoading(true);
    try {
      if (token) {
        // Use authenticated endpoint
        const recs = await mlApi.getLearningRecommendations(token, {
          target_role: 'Software Engineer',
          experience_level: 'intermediate',
          time_commitment: 'medium'
        });
        setMlLearningRecs(recs);
      } else {
        // Use public endpoint
        const recs = await mlApi.getLearningRecommendationsPublic({
          target_role: 'Software Engineer',
          experience_level: 'intermediate',
          time_commitment: 'medium'
        });
        setMlLearningRecs(recs);
      }
      setError(null);
    } catch (error: any) {
      console.error('Error loading ML learning recommendations:', error);
      setError(error.message || 'Failed to load ML learning recommendations');
    } finally {
      setLoading(false);
    }
  };

  const loadEnhancedCareerPaths = async () => {
    const token = localStorage.getItem('token');
    
    setLoading(true);
    try {
      if (token) {
        const paths = await enhancedCareerApi.getEnhancedCareerPaths(token, {
          current_role: 'Software Engineer',
          industry: 'Technology',
          timeframe_years: 5,
          include_skill_requirements: true,
          include_salary_data: true
        });
        setEnhancedCareerPaths(paths);
      } else {
        const paths = await enhancedCareerApi.getPublicCareerPaths({
          current_role: 'Software Engineer',
          industry: 'Technology',
          timeframe_years: 5,
          include_skill_requirements: true,
          include_salary_data: true
        });
        setEnhancedCareerPaths(paths);
      }
      setError(null);
    } catch (error: any) {
      console.error('Error loading enhanced career paths:', error);
      setError(error.message || 'Failed to load enhanced career paths');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'skills-clusters', label: '🧠 ML Skill Clusters', action: loadSkillClusters },
    { id: 'market-trends', label: '📈 Market Trends', action: loadMarketTrends },
    { id: 'ml-learning', label: '🎯 ML Learning Recs', action: loadMLLearningRecommendations },
    { id: 'enhanced-career', label: '🚀 Enhanced Career Paths', action: loadEnhancedCareerPaths },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold mb-4 text-gray-800">
        🤖 ML & Enhanced APIs Dashboard
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

      {/* Skills Clusters Tab */}
      {activeTab === 'skills-clusters' && !loading && (
        <div className="space-y-6">
          {skillClusters ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {skillClusters.total_clusters}
                  </div>
                  <div className="text-sm text-blue-800">Total Clusters</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {skillClusters.skill_statistics.total_skills_analyzed}
                  </div>
                  <div className="text-sm text-green-800">Skills Analyzed</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {skillClusters.skill_statistics.emerging_skills.length}
                  </div>
                  <div className="text-sm text-purple-800">Emerging Skills</div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3">Skill Clusters</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                  {skillClusters.clusters.slice(0, 8).map((cluster, index) => (
                    <div key={cluster.cluster_id} className="bg-white p-4 rounded border">
                      <div className="font-medium text-gray-900 mb-2">{cluster.cluster_name}</div>
                      <div className="text-sm text-gray-600 mb-2">
                        Confidence: {(cluster.confidence_score * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-500">
                        Core Skills: {cluster.core_skills.slice(0, 3).join(', ')}
                        {cluster.core_skills.length > 3 && ` +${cluster.core_skills.length - 3} more`}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-4 p-3 bg-blue-50 rounded">
                  <h5 className="font-medium text-blue-900 mb-2">Emerging Skills Detected</h5>
                  <div className="flex flex-wrap gap-2">
                    {skillClusters.skill_statistics.emerging_skills.slice(0, 10).map((skill, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">🧠</div>
              <p>Click "ML Skill Clusters" to load clustering analysis</p>
            </div>
          )}
        </div>
      )}

      {/* Market Trends Tab */}
      {activeTab === 'market-trends' && !loading && (
        <div className="space-y-6">
          {marketTrends ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {marketTrends.market_insights.fastest_growing_skills.length}
                  </div>
                  <div className="text-sm text-green-800">Fast Growing Skills</div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {marketTrends.market_insights.highest_demand_skills.length}
                  </div>
                  <div className="text-sm text-blue-800">High Demand Skills</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {marketTrends.market_insights.emerging_technologies.length}
                  </div>
                  <div className="text-sm text-purple-800">Emerging Technologies</div>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-orange-600">
                    {marketTrends.predictions.market_outlook}
                  </div>
                  <div className="text-sm text-orange-800">Market Outlook</div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3">Trending Skills</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-80 overflow-y-auto">
                  {marketTrends.trends.slice(0, 6).map((trend, index) => (
                    <div key={index} className="bg-white p-4 rounded border">
                      <div className="flex justify-between items-start mb-2">
                        <div className="font-medium text-gray-900">{trend.skill}</div>
                        <span className={`px-2 py-1 rounded text-xs ${
                          trend.trend_direction === 'rising' 
                            ? 'bg-green-100 text-green-800' 
                            : trend.trend_direction === 'stable'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {trend.trend_direction}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        Growth: {(trend.growth_rate * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">
                        Demand Score: {trend.demand_score.toFixed(1)}/10
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">📈</div>
              <p>Click "Market Trends" to load trend analysis</p>
            </div>
          )}
        </div>
      )}

      {/* ML Learning Recommendations Tab */}
      {activeTab === 'ml-learning' && !loading && (
        <div className="space-y-6">
          {mlLearningRecs ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {mlLearningRecs.recommendations.length}
                  </div>
                  <div className="text-sm text-blue-800">ML Recommendations</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {mlLearningRecs.learning_insights.total_estimated_time_weeks}
                  </div>
                  <div className="text-sm text-green-800">Total Weeks</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {(mlLearningRecs.personalization_metadata.recommendation_confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-purple-800">Confidence</div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3">ML-Generated Learning Path</h4>
                <div className="space-y-4 max-h-80 overflow-y-auto">
                  {mlLearningRecs.recommendations.slice(0, 3).map((rec, index) => (
                    <div key={rec.recommendation_id} className="bg-white p-4 rounded border">
                      <div className="flex justify-between items-start mb-2">
                        <div className="font-medium text-gray-900">{rec.recommended_skill}</div>
                        <span className={`px-2 py-1 rounded text-xs ${
                          rec.priority === 'high' 
                            ? 'bg-red-100 text-red-800' 
                            : rec.priority === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {rec.priority} priority
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        Confidence: {(rec.confidence_score * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">
                        Salary Impact: +{rec.career_impact.salary_increase_potential}%
                      </div>
                      <div className="text-sm text-gray-600">
                        Learning Steps: {rec.learning_path.length}
                      </div>
                    </div>
                  ))}
                </div>

                {mlLearningRecs.learning_insights.skill_gap_analysis && (
                  <div className="mt-4 p-3 bg-orange-50 rounded">
                    <h5 className="font-medium text-orange-900 mb-2">Skill Gap Analysis</h5>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <div className="font-medium text-orange-800">Critical Gaps</div>
                        <div className="text-orange-700">
                          {mlLearningRecs.learning_insights.skill_gap_analysis.critical_gaps.slice(0, 3).join(', ')}
                        </div>
                      </div>
                      <div>
                        <div className="font-medium text-orange-800">Improvement Areas</div>
                        <div className="text-orange-700">
                          {mlLearningRecs.learning_insights.skill_gap_analysis.improvement_areas.slice(0, 3).join(', ')}
                        </div>
                      </div>
                      <div>
                        <div className="font-medium text-orange-800">Strengths</div>
                        <div className="text-orange-700">
                          {mlLearningRecs.learning_insights.skill_gap_analysis.strengths.slice(0, 3).join(', ')}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">🎯</div>
              <p>Click "ML Learning Recs" to load ML-powered recommendations</p>
            </div>
          )}
        </div>
      )}

      {/* Enhanced Career Paths Tab */}
      {activeTab === 'enhanced-career' && !loading && (
        <div className="space-y-6">
          {enhancedCareerPaths ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {Object.keys(enhancedCareerPaths.career_tracks).length}
                  </div>
                  <div className="text-sm text-blue-800">Career Tracks</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {enhancedCareerPaths.timeframe_years}
                  </div>
                  <div className="text-sm text-green-800">Years Planned</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {enhancedCareerPaths.skill_development_plan.priority_skills.length}
                  </div>
                  <div className="text-sm text-purple-800">Priority Skills</div>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg text-center">
                  <div className="text-3xl font-bold text-orange-600">
                    {enhancedCareerPaths.market_insights.highest_demand_roles.length}
                  </div>
                  <div className="text-sm text-orange-800">High Demand Roles</div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3">Career Tracks for {enhancedCareerPaths.current_role}</h4>
                <div className="space-y-4 max-h-80 overflow-y-auto">
                  {Object.entries(enhancedCareerPaths.career_tracks).slice(0, 3).map(([trackName, track]) => (
                    <div key={trackName} className="bg-white p-4 rounded border">
                      <div className="flex justify-between items-start mb-2">
                        <div className="font-medium text-gray-900">{track.name}</div>
                        <span className={`px-2 py-1 rounded text-xs ${
                          track.market_demand === 'high' 
                            ? 'bg-green-100 text-green-800' 
                            : track.market_demand === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {track.market_demand} demand
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">{track.description}</div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Duration:</span> {track.average_time_years} years
                        </div>
                        <div>
                          <span className="font-medium">Salary Growth:</span> +{track.salary_growth_percentage}%
                        </div>
                        <div>
                          <span className="font-medium">Difficulty:</span> {track.difficulty}/10
                        </div>
                        <div>
                          <span className="font-medium">Steps:</span> {track.steps.length}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {enhancedCareerPaths.personalized_recommendations && (
                  <div className="mt-4 p-3 bg-blue-50 rounded">
                    <h5 className="font-medium text-blue-900 mb-2">Personalized Recommendation</h5>
                    <div className="text-sm text-blue-800">
                      <div><strong>Best Fit:</strong> {enhancedCareerPaths.personalized_recommendations.best_fit_track}</div>
                      <div><strong>Reasoning:</strong> {enhancedCareerPaths.personalized_recommendations.reasoning}</div>
                      <div><strong>Next Steps:</strong> {enhancedCareerPaths.personalized_recommendations.immediate_next_steps.slice(0, 2).join(', ')}</div>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">🚀</div>
              <p>Click "Enhanced Career Paths" to load comprehensive career planning</p>
            </div>
          )}
        </div>
      )}

      {/* API Information */}
      <div className="mt-8 p-4 bg-indigo-50 rounded-lg">
        <h5 className="font-medium text-indigo-800 mb-2">🆕 Newly Integrated APIs</h5>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h6 className="font-medium text-indigo-700 mb-2">ML APIs</h6>
            <ul className="text-indigo-600 space-y-1">
              <li>• <code>GET /ml/skills/clusters</code></li>
              <li>• <code>GET /ml/market-trends</code></li>
              <li>• <code>GET /ml/learning-recommendations</code></li>
              <li>• <code>GET /ml/learning-recommendations-public</code></li>
            </ul>
          </div>
          <div>
            <h6 className="font-medium text-indigo-700 mb-2">Enhanced Career APIs</h6>
            <ul className="text-indigo-600 space-y-1">
              <li>• <code>GET /recommendations/career-paths</code></li>
              <li>• <code>GET /recommendations/career-paths/public</code></li>
              <li>• <code>GET /recommendations/career-paths/analytics</code></li>
              <li>• <code>GET /recommendations/career-paths/industry</code></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
} 