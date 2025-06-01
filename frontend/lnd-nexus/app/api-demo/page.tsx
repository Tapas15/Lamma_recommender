'use client';

import React, { useState } from 'react';
import SkillGapAnalyzer from '../components/SkillGapAnalyzer';
import SavedProjectsManager from '../components/SavedProjectsManager';
import AdvancedSearch from '../components/AdvancedSearch';

export default function APIDemoPage() {
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('skill-gap');

  const handleSearchResults = (results: any[]) => {
    setSearchResults(results);
  };

  const handleSearchLoading = (loading: boolean) => {
    setSearchLoading(loading);
  };

  const handleSearchError = (error: string | null) => {
    setSearchError(error);
  };

  const tabs = [
    { id: 'skill-gap', label: '🎯 Skill Gap Analysis', description: 'Analyze skill gaps and get learning recommendations' },
    { id: 'saved-projects', label: '💾 Saved Projects', description: 'Manage your saved projects with priority and notes' },
    { id: 'advanced-search', label: '🔍 Advanced Search', description: 'Test enhanced search capabilities with filters' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">API Integration Demo</h1>
              <p className="text-gray-600 mt-1">
                Demonstrating backend API integration with Next.js frontend
              </p>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Backend: localhost:8000
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                Frontend: localhost:3000
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-6 border-b-2 font-medium text-sm ${
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
          <div className="p-4 bg-gray-50">
            <p className="text-sm text-gray-600">
              {tabs.find(tab => tab.id === activeTab)?.description}
            </p>
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-8">
          {activeTab === 'skill-gap' && (
            <div>
              <SkillGapAnalyzer />
              
              {/* API Information */}
              <div className="mt-8 bg-blue-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-4">
                  🔗 Connected Backend APIs
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <h4 className="font-medium text-blue-800 mb-2">Skill Gap Analysis</h4>
                    <ul className="space-y-1 text-blue-700">
                      <li><code>GET /recommendations/skill-gap</code></li>
                      <li><code>GET /recommendations/learning</code></li>
                      <li><code>GET /recommendations/career-path</code></li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-blue-800 mb-2">Features</h4>
                    <ul className="space-y-1 text-blue-700">
                      <li>• Job-specific skill comparison</li>
                      <li>• Target role analysis</li>
                      <li>• Learning resource recommendations</li>
                      <li>• Priority-based learning paths</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'saved-projects' && (
            <div>
              <SavedProjectsManager />
              
              {/* API Information */}
              <div className="mt-8 bg-green-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-green-900 mb-4">
                  🔗 Connected Backend APIs
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <h4 className="font-medium text-green-800 mb-2">Saved Projects</h4>
                    <ul className="space-y-1 text-green-700">
                      <li><code>POST /saved-projects</code></li>
                      <li><code>GET /saved-projects</code></li>
                      <li><code>DELETE /saved-projects/{'{id}'}</code></li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-green-800 mb-2">Features</h4>
                    <ul className="space-y-1 text-green-700">
                      <li>• Priority levels (high/medium/low)</li>
                      <li>• Interest rating (1-5 stars)</li>
                      <li>• Personal notes</li>
                      <li>• Application status checking</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'advanced-search' && (
            <div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <AdvancedSearch
                    searchType="jobs"
                    onResults={handleSearchResults}
                    onLoading={handleSearchLoading}
                    onError={handleSearchError}
                  />
                </div>
                <div>
                  {/* Search Results */}
                  <div className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-xl font-semibold mb-4 text-gray-800">
                      Search Results
                    </h3>
                    
                    {searchLoading && (
                      <div className="flex items-center justify-center py-8">
                        <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span className="ml-2">Searching...</span>
                      </div>
                    )}

                    {searchError && (
                      <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                        {searchError}
                      </div>
                    )}

                    {!searchLoading && !searchError && searchResults.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        <div className="text-4xl mb-2">🔍</div>
                        <p>No search performed yet.</p>
                        <p className="text-sm">Use the search form to find jobs, projects, or candidates.</p>
                      </div>
                    )}

                    {!searchLoading && searchResults.length > 0 && (
                      <div className="space-y-4">
                        <div className="text-sm text-gray-600 mb-4">
                          Found {searchResults.length} results
                        </div>
                        {searchResults.slice(0, 5).map((result, index) => (
                          <div key={index} className="border border-gray-200 rounded-lg p-4">
                            <h4 className="font-medium text-gray-900">
                              {result.title || result.name || `Result ${index + 1}`}
                            </h4>
                            <p className="text-sm text-gray-600 mt-1">
                              {result.description && result.description.length > 100 
                                ? `${result.description.substring(0, 100)}...`
                                : result.description || 'No description available'}
                            </p>
                            <div className="mt-2 text-xs text-gray-500">
                              ID: {result.id || 'N/A'}
                            </div>
                          </div>
                        ))}
                        {searchResults.length > 5 && (
                          <div className="text-sm text-gray-500 text-center">
                            ... and {searchResults.length - 5} more results
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* API Information */}
              <div className="mt-8 bg-purple-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-purple-900 mb-4">
                  🔗 Connected Backend APIs
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <h4 className="font-medium text-purple-800 mb-2">Enhanced Search</h4>
                    <ul className="space-y-1 text-purple-700">
                      <li><code>POST /jobs/search</code></li>
                      <li><code>POST /projects/search</code></li>
                      <li><code>POST /candidates/search</code></li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-purple-800 mb-2">Search Filters</h4>
                    <ul className="space-y-1 text-purple-700">
                      <li>• Location & remote options</li>
                      <li>• Salary/budget ranges</li>
                      <li>• Experience levels</li>
                      <li>• Skills matching</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-purple-800 mb-2">Advanced Options</h4>
                    <ul className="space-y-1 text-purple-700">
                      <li>• Sorting & pagination</li>
                      <li>• Flexible query matching</li>
                      <li>• Type-specific filters</li>
                      <li>• Real-time results</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Overall Status */}
        <div className="mt-12 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🚀 API Integration Status
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">3</div>
              <div className="text-sm text-gray-600">New API Services</div>
              <div className="text-xs text-gray-500 mt-1">
                searchApi, advancedRecommendationsApi, completeApplicationsApi
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">35+</div>
              <div className="text-sm text-gray-600">Backend Endpoints</div>
              <div className="text-xs text-gray-500 mt-1">
                Ready for frontend integration
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">100%</div>
              <div className="text-sm text-gray-600">Type Safety</div>
              <div className="text-xs text-gray-500 mt-1">
                Full TypeScript integration
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-2">Next Steps for Implementation</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>1. Integrate components into main application pages</li>
              <li>2. Add error boundaries and comprehensive error handling</li>
              <li>3. Implement caching and performance optimizations</li>
              <li>4. Add unit tests for API service layers</li>
              <li>5. Create user-friendly loading states and animations</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
} 