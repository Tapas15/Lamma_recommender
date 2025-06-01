'use client';

import React, { useState, useEffect } from 'react';
import { completeApplicationsApi, SavedProjectRequest } from '../services/completeApplicationsApi';

interface SavedProject {
  id: string;
  project_id: string;
  project_title: string;
  project_description: string;
  budget: number;
  duration: string;
  notes?: string;
  priority?: 'high' | 'medium' | 'low';
  interest_level?: number;
  saved_at: string;
  [key: string]: any;
}

export default function SavedProjectsManager() {
  const [savedProjects, setSavedProjects] = useState<SavedProject[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newProjectId, setNewProjectId] = useState('');
  const [newNotes, setNewNotes] = useState('');
  const [newPriority, setNewPriority] = useState<'high' | 'medium' | 'low'>('medium');
  const [newInterestLevel, setNewInterestLevel] = useState(3);

  useEffect(() => {
    loadSavedProjects();
  }, []);

  const loadSavedProjects = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authentication required. Please log in.');
      return;
    }

    setLoading(true);
    try {
      const projects = await completeApplicationsApi.getSavedProjects(token);
      setSavedProjects(projects);
      setError(null);
    } catch (error: any) {
      console.error('Failed to load saved projects:', error);
      setError(error.message || 'Failed to load saved projects.');
    } finally {
      setLoading(false);
    }
  };

  const saveProject = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authentication required. Please log in.');
      return;
    }

    if (!newProjectId.trim()) {
      setError('Please enter a project ID.');
      return;
    }

    try {
      const saveRequest: SavedProjectRequest = {
        project_id: newProjectId.trim(),
        notes: newNotes.trim() || undefined,
        priority: newPriority,
        interest_level: newInterestLevel,
      };

      await completeApplicationsApi.saveProject(token, saveRequest);
      
      // Clear form
      setNewProjectId('');
      setNewNotes('');
      setNewPriority('medium');
      setNewInterestLevel(3);
      
      // Reload projects
      loadSavedProjects();
      setError(null);
    } catch (error: any) {
      console.error('Failed to save project:', error);
      setError(error.message || 'Failed to save project.');
    }
  };

  const removeProject = async (savedProjectId: string) => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authentication required. Please log in.');
      return;
    }

    try {
      await completeApplicationsApi.removeSavedProject(token, savedProjectId);
      loadSavedProjects();
      setError(null);
    } catch (error: any) {
      console.error('Failed to remove project:', error);
      setError(error.message || 'Failed to remove project.');
    }
  };

  const checkIfApplied = async (projectId: string) => {
    const token = localStorage.getItem('token');
    if (!token) return false;

    try {
      return await completeApplicationsApi.hasAppliedToProject(token, projectId);
    } catch (error) {
      console.error('Error checking application status:', error);
      return false;
    }
  };

  const getPriorityColor = (priority: 'high' | 'medium' | 'low' | undefined) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span
        key={i}
        className={`text-lg ${i < rating ? 'text-yellow-400' : 'text-gray-300'}`}
      >
        ★
      </span>
    ));
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold mb-4 text-gray-800">
        💾 Saved Projects Manager
      </h3>

      {/* Add New Saved Project */}
      <div className="bg-gray-50 p-4 rounded-lg mb-6">
        <h4 className="text-lg font-semibold mb-3">Save a New Project</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project ID *
            </label>
            <input
              type="text"
              value={newProjectId}
              onChange={(e) => setNewProjectId(e.target.value)}
              placeholder="Enter project ID"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority Level
            </label>
            <select
              value={newPriority}
              onChange={(e) => setNewPriority(e.target.value as 'high' | 'medium' | 'low')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Interest Level (1-5)
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="range"
                min="1"
                max="5"
                value={newInterestLevel}
                onChange={(e) => setNewInterestLevel(Number(e.target.value))}
                className="flex-1"
              />
              <span className="text-sm text-gray-600">{newInterestLevel}/5</span>
            </div>
            <div className="mt-1">
              {renderStars(newInterestLevel)}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes (Optional)
            </label>
            <textarea
              value={newNotes}
              onChange={(e) => setNewNotes(e.target.value)}
              placeholder="Add personal notes about this project..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={saveProject}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Save Project
          </button>
        </div>
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
          <span className="ml-2 text-gray-600">Loading saved projects...</span>
        </div>
      )}

      {/* Saved Projects List */}
      {!loading && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold">Your Saved Projects ({savedProjects.length})</h4>
            <button
              onClick={loadSavedProjects}
              className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
            >
              Refresh
            </button>
          </div>

          {savedProjects.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">📂</div>
              <p>No saved projects yet.</p>
              <p className="text-sm">Save projects you're interested in to keep track of them!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {savedProjects.map((project) => (
                <div key={project.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h5 className="font-medium text-gray-900">
                          {project.project_title || `Project ${project.project_id}`}
                        </h5>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(project.priority)}`}>
                          {project.priority || 'medium'} priority
                        </span>
                      </div>
                      
                      {project.project_description && (
                        <p className="text-sm text-gray-600 mb-2">
                          {project.project_description.length > 150 
                            ? `${project.project_description.substring(0, 150)}...` 
                            : project.project_description}
                        </p>
                      )}

                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-2">
                        {project.budget && (
                          <span>💰 ${project.budget.toLocaleString()}</span>
                        )}
                        {project.duration && (
                          <span>⏱️ {project.duration}</span>
                        )}
                        <span>📅 Saved: {new Date(project.saved_at).toLocaleDateString()}</span>
                      </div>

                      {project.interest_level && (
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-sm text-gray-600">Interest:</span>
                          {renderStars(project.interest_level)}
                          <span className="text-sm text-gray-500">({project.interest_level}/5)</span>
                        </div>
                      )}

                      {project.notes && (
                        <div className="bg-blue-50 p-3 rounded-md mt-2">
                          <div className="text-sm text-gray-700">
                            <strong>Notes:</strong> {project.notes}
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col gap-2 ml-4">
                      <button
                        onClick={() => removeProject(project.id)}
                        className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200"
                      >
                        Remove
                      </button>
                      <button
                        onClick={() => window.open(`/projects/${project.project_id}`, '_blank')}
                        className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200"
                      >
                        View
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Demo Information */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg">
        <h5 className="font-medium text-blue-800 mb-2">🚀 API Integration Demonstration</h5>
        <p className="text-sm text-blue-700">
          This component demonstrates the integration with the backend <code>saved-projects</code> APIs:
        </p>
        <ul className="text-sm text-blue-700 mt-2 ml-4 list-disc">
          <li><code>POST /saved-projects</code> - Save a new project</li>
          <li><code>GET /saved-projects</code> - Get all saved projects</li>
          <li><code>DELETE /saved-projects/{'{id}'}</code> - Remove a saved project</li>
          <li><code>hasAppliedToProject()</code> - Check application status</li>
        </ul>
      </div>
    </div>
  );
} 