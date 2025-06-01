'use client';

import React, { useState } from 'react';
import { advancedRecommendationsApi, SkillGapAnalysis, LearningRecommendation } from '../services/advancedRecommendationsApi';

interface SkillGapAnalyzerProps {
  jobId?: string;
  targetRole?: string;
}

export default function SkillGapAnalyzer({ jobId, targetRole }: SkillGapAnalyzerProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [skillGap, setSkillGap] = useState<SkillGapAnalysis | null>(null);
  const [learningRecommendations, setLearningRecommendations] = useState<LearningRecommendation[]>([]);
  const [inputJobId, setInputJobId] = useState(jobId || '');
  const [inputTargetRole, setInputTargetRole] = useState(targetRole || '');

  const analyzeSkillGap = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authentication required. Please log in.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Get skill gap analysis
      const analysis = await advancedRecommendationsApi.getSkillGapAnalysis(
        token, 
        inputJobId || undefined, 
        inputTargetRole || undefined
      );
      setSkillGap(analysis);

      // Get learning recommendations based on missing skills
      if (analysis.missing_skills && analysis.missing_skills.length > 0) {
        const recommendations = await advancedRecommendationsApi.getLearningRecommendations(
          token,
          analysis.missing_skills,
          inputTargetRole || undefined
        );
        setLearningRecommendations(recommendations);
      }
    } catch (error: any) {
      console.error('Skill gap analysis failed:', error);
      setError(error.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getImportanceColor = (importance: 'high' | 'medium' | 'low') => {
    switch (importance) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: 'high' | 'medium' | 'low') => {
    switch (priority) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold mb-4 text-gray-800">
        🎯 Skill Gap Analysis
      </h3>

      {/* Input Fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job ID (Optional)
          </label>
          <input
            type="text"
            value={inputJobId}
            onChange={(e) => setInputJobId(e.target.value)}
            placeholder="Enter job ID for comparison"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Role (Optional)
          </label>
          <input
            type="text"
            value={inputTargetRole}
            onChange={(e) => setInputTargetRole(e.target.value)}
            placeholder="e.g., Senior React Developer"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Analyze Button */}
      <div className="mb-6">
        <button
          onClick={analyzeSkillGap}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
        >
          {loading && (
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {loading ? 'Analyzing...' : 'Analyze Skills'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Skill Gap Results */}
      {skillGap && (
        <div className="space-y-6">
          {/* Overview */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-lg font-semibold mb-2">📊 Match Overview</h4>
            <div className="flex items-center mb-2">
              <span className="text-2xl font-bold text-blue-600">
                {skillGap.match_percentage}%
              </span>
              <span className="ml-2 text-gray-600">skill match</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full" 
                style={{ width: `${skillGap.match_percentage}%` }}
              ></div>
            </div>
          </div>

          {/* Current Skills */}
          {skillGap.candidate_skills && skillGap.candidate_skills.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-3">✅ Your Current Skills</h4>
              <div className="flex flex-wrap gap-2">
                {skillGap.candidate_skills.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Missing Skills */}
          {skillGap.missing_skills && skillGap.missing_skills.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-3">❌ Skills to Develop</h4>
              <div className="flex flex-wrap gap-2">
                {skillGap.missing_skills.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-red-100 text-red-800"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Skill Gaps */}
          {skillGap.skill_gaps && skillGap.skill_gaps.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-3">🎯 Priority Skills</h4>
              <div className="space-y-3">
                {skillGap.skill_gaps.map((gap, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-medium text-gray-900">{gap.skill}</h5>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImportanceColor(gap.importance)}`}>
                        {gap.importance} priority
                      </span>
                    </div>
                    {gap.learning_resources && gap.learning_resources.length > 0 && (
                      <div className="text-sm text-gray-600">
                        <strong>Resources:</strong> {gap.learning_resources.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Learning Recommendations */}
          {learningRecommendations.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-3">📚 Learning Recommendations</h4>
              <div className="space-y-4">
                {learningRecommendations.map((recommendation, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-medium text-gray-900">{recommendation.skill}</h5>
                      <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full ${getPriorityColor(recommendation.priority)} mr-2`}></div>
                        <span className="text-sm text-gray-600">{recommendation.priority} priority</span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      <strong>Estimated time:</strong> {recommendation.estimated_completion_time}
                    </p>
                    
                    {recommendation.learning_path.length > 0 && (
                      <div className="mb-3">
                        <strong className="text-sm text-gray-700">Learning Path:</strong>
                        <ol className="list-decimal list-inside text-sm text-gray-600 mt-1">
                          {recommendation.learning_path.map((step, stepIndex) => (
                            <li key={stepIndex}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {recommendation.resources.length > 0 && (
                      <div>
                        <strong className="text-sm text-gray-700">Resources:</strong>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                          {recommendation.resources.map((resource, resourceIndex) => (
                            <div key={resourceIndex} className="text-sm border border-gray-100 rounded p-2">
                              <div className="font-medium">{resource.title}</div>
                              <div className="text-gray-600">
                                {resource.provider} • {resource.type} • {resource.difficulty}
                              </div>
                              <div className="text-gray-500">{resource.duration}</div>
                              {resource.rating && (
                                <div className="text-yellow-600">
                                  {'★'.repeat(Math.floor(resource.rating))} {resource.rating}/5
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Next Steps */}
          {skillGap.recommendation_priority && skillGap.recommendation_priority.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-3">🚀 Next Steps</h4>
              <ol className="list-decimal list-inside space-y-1">
                {skillGap.recommendation_priority.map((step, index) => (
                  <li key={index} className="text-gray-700">{step}</li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  );
} 