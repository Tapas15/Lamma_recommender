'use client';

import React, { useState, useEffect } from 'react';
import { searchApi, JobSearchRequest, ProjectSearchRequest, CandidateSearchRequest } from '../services/searchApi';

interface AdvancedSearchProps {
  searchType: 'jobs' | 'projects' | 'candidates';
  onResults: (results: any[]) => void;
  onLoading: (loading: boolean) => void;
  onError: (error: string | null) => void;
}

export default function AdvancedSearch({ 
  searchType, 
  onResults, 
  onLoading, 
  onError 
}: AdvancedSearchProps) {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<any>({});
  const [isSearching, setIsSearching] = useState(false);

  // Common filter states
  const [location, setLocation] = useState('');
  const [remoteOption, setRemoteOption] = useState(false);
  const [skills, setSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState('');

  // Job-specific filters
  const [salaryMin, setSalaryMin] = useState<number | ''>('');
  const [salaryMax, setSalaryMax] = useState<number | ''>('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [employmentType, setEmploymentType] = useState('');
  const [companySize, setCompanySize] = useState('');
  const [industry, setIndustry] = useState('');

  // Project-specific filters
  const [budgetMin, setBudgetMin] = useState<number | ''>('');
  const [budgetMax, setBudgetMax] = useState<number | ''>('');
  const [duration, setDuration] = useState('');
  const [projectType, setProjectType] = useState('');

  // Candidate-specific filters
  const [availability, setAvailability] = useState('');
  const [salaryExpectationMin, setSalaryExpectationMin] = useState<number | ''>('');
  const [salaryExpectationMax, setSalaryExpectationMax] = useState<number | ''>('');
  const [remotePreference, setRemotePreference] = useState('');

  const addSkill = () => {
    if (skillInput.trim() && !skills.includes(skillInput.trim())) {
      setSkills([...skills, skillInput.trim()]);
      setSkillInput('');
    }
  };

  const removeSkill = (skillToRemove: string) => {
    setSkills(skills.filter(skill => skill !== skillToRemove));
  };

  const buildFilters = () => {
    const baseFilters: any = {
      location: location || undefined,
      remote_option: remoteOption || undefined,
      required_skills: skills.length > 0 ? skills : undefined,
    };

    if (searchType === 'jobs') {
      return {
        ...baseFilters,
        salary_min: salaryMin || undefined,
        salary_max: salaryMax || undefined,
        experience_level: experienceLevel || undefined,
        employment_type: employmentType || undefined,
        company_size: companySize || undefined,
        industry: industry || undefined,
      };
    } else if (searchType === 'projects') {
      return {
        budget_min: budgetMin || undefined,
        budget_max: budgetMax || undefined,
        duration: duration || undefined,
        project_type: projectType || undefined,
        required_skills: skills.length > 0 ? skills : undefined,
        location: location || undefined,
        remote_option: remoteOption || undefined,
      };
    } else if (searchType === 'candidates') {
      return {
        location: location || undefined,
        experience_level: experienceLevel || undefined,
        skills: skills.length > 0 ? skills : undefined,
        availability: availability || undefined,
        salary_expectation_min: salaryExpectationMin || undefined,
        salary_expectation_max: salaryExpectationMax || undefined,
        remote_preference: remotePreference || undefined,
      };
    }
    return baseFilters;
  };

  const handleSearch = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      onError('Authentication required. Please log in.');
      return;
    }

    setIsSearching(true);
    onLoading(true);
    onError(null);

    try {
      const searchFilters = buildFilters();
      let results: any[] = [];

      if (searchType === 'jobs') {
        const searchRequest: JobSearchRequest = {
          query: query || undefined,
          filters: searchFilters,
          limit: 20,
          sort_by: 'relevance',
          sort_order: 'desc',
        };
        results = await searchApi.searchJobs(token, searchRequest);
      } else if (searchType === 'projects') {
        const searchRequest: ProjectSearchRequest = {
          query: query || undefined,
          filters: searchFilters,
          limit: 20,
          sort_by: 'relevance',
          sort_order: 'desc',
        };
        results = await searchApi.searchProjects(token, searchRequest);
      } else if (searchType === 'candidates') {
        const searchRequest: CandidateSearchRequest = {
          query: query || undefined,
          filters: searchFilters,
          limit: 20,
          sort_by: 'relevance',
          sort_order: 'desc',
        };
        results = await searchApi.searchCandidates(token, searchRequest);
      }

      onResults(results);
      onError(null);
    } catch (error: any) {
      console.error('Search failed:', error);
      onError(error.message || 'Search failed. Please try again.');
      onResults([]);
    } finally {
      setIsSearching(false);
      onLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      const target = e.target as HTMLElement;
      if (target && target.id === 'skill-input') {
        e.preventDefault();
        addSkill();
      } else {
        e.preventDefault();
        handleSearch();
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h3 className="text-xl font-semibold mb-4 text-gray-800">
        Advanced {searchType.charAt(0).toUpperCase() + searchType.slice(1)} Search
      </h3>
      
      {/* Search Query */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Search Query
        </label>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={`Search for ${searchType}...`}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Skills */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {searchType === 'candidates' ? 'Skills' : 'Required Skills'}
        </label>
        <div className="flex mb-2">
          <input
            id="skill-input"
            type="text"
            value={skillInput}
            onChange={(e) => setSkillInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Add a skill..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={addSkill}
            className="px-4 py-2 bg-blue-500 text-white rounded-r-md hover:bg-blue-600"
          >
            Add
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {skills.map((skill, index) => (
            <span
              key={index}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
            >
              {skill}
              <button
                onClick={() => removeSkill(skill)}
                className="ml-2 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      {/* Common Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g., San Francisco, Remote"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            id="remote-option"
            checked={remoteOption}
            onChange={(e) => setRemoteOption(e.target.checked)}
            className="mr-2"
          />
          <label htmlFor="remote-option" className="text-sm text-gray-700">
            Remote work available
          </label>
        </div>
      </div>

      {/* Job-specific filters */}
      {searchType === 'jobs' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Min Salary ($)
            </label>
            <input
              type="number"
              value={salaryMin}
              onChange={(e) => setSalaryMin(e.target.value ? Number(e.target.value) : '')}
              placeholder="50000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Salary ($)
            </label>
            <input
              type="number"
              value={salaryMax}
              onChange={(e) => setSalaryMax(e.target.value ? Number(e.target.value) : '')}
              placeholder="150000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Experience Level
            </label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Any</option>
              <option value="entry">Entry Level</option>
              <option value="mid">Mid Level</option>
              <option value="senior">Senior Level</option>
              <option value="lead">Lead/Principal</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Employment Type
            </label>
            <select
              value={employmentType}
              onChange={(e) => setEmploymentType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Any</option>
              <option value="full-time">Full Time</option>
              <option value="part-time">Part Time</option>
              <option value="contract">Contract</option>
              <option value="freelance">Freelance</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Company Size
            </label>
            <select
              value={companySize}
              onChange={(e) => setCompanySize(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Any</option>
              <option value="startup">Startup (1-10)</option>
              <option value="small">Small (11-50)</option>
              <option value="medium">Medium (51-200)</option>
              <option value="large">Large (201-1000)</option>
              <option value="enterprise">Enterprise (1000+)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Industry
            </label>
            <input
              type="text"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              placeholder="e.g., Technology, Healthcare"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      )}

      {/* Project-specific filters */}
      {searchType === 'projects' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Min Budget ($)
            </label>
            <input
              type="number"
              value={budgetMin}
              onChange={(e) => setBudgetMin(e.target.value ? Number(e.target.value) : '')}
              placeholder="1000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Budget ($)
            </label>
            <input
              type="number"
              value={budgetMax}
              onChange={(e) => setBudgetMax(e.target.value ? Number(e.target.value) : '')}
              placeholder="10000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration
            </label>
            <select
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Any</option>
              <option value="short">Short term (< 1 month)</option>
              <option value="medium">Medium term (1-3 months)</option>
              <option value="long">Long term (3+ months)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Type
            </label>
            <input
              type="text"
              value={projectType}
              onChange={(e) => setProjectType(e.target.value)}
              placeholder="e.g., Web Development, Mobile App"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      )}

      {/* Candidate-specific filters */}
      {searchType === 'candidates' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Experience Level
            </label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Any</option>
              <option value="entry">Entry Level</option>
              <option value="mid">Mid Level</option>
              <option value="senior">Senior Level</option>
              <option value="lead">Lead/Principal</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Availability
            </label>
            <select
              value={availability}
              onChange={(e) => setAvailability(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Any</option>
              <option value="immediate">Immediately</option>
              <option value="within-2-weeks">Within 2 weeks</option>
              <option value="within-1-month">Within 1 month</option>
              <option value="within-3-months">Within 3 months</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Remote Preference
            </label>
            <select
              value={remotePreference}
              onChange={(e) => setRemotePreference(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Any</option>
              <option value="remote">Remote only</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">On-site only</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Min Salary Expectation ($)
            </label>
            <input
              type="number"
              value={salaryExpectationMin}
              onChange={(e) => setSalaryExpectationMin(e.target.value ? Number(e.target.value) : '')}
              placeholder="60000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Salary Expectation ($)
            </label>
            <input
              type="number"
              value={salaryExpectationMax}
              onChange={(e) => setSalaryExpectationMax(e.target.value ? Number(e.target.value) : '')}
              placeholder="120000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      )}

      {/* Search Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSearch}
          disabled={isSearching}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
        >
          {isSearching && (
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>
    </div>
  );
} 