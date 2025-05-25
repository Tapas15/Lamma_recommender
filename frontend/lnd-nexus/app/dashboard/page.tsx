'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';
import { jobsApi } from '../services/api';

export default function Dashboard() {
  const { isAuthenticated, isLoading, user, token, logout } = useAuth();
  const [jobs, setJobs] = useState<any[]>([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();
  
  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);
  
  // Fetch jobs when authenticated
  useEffect(() => {
    const fetchJobs = async () => {
      if (isAuthenticated && token) {
        try {
          setJobsLoading(true);
          const jobsData = await jobsApi.getJobs(token);
          setJobs(jobsData);
          setError(null);
        } catch (err) {
          console.error('Error fetching jobs:', err);
          setError('Failed to load jobs. Please try again later.');
        } finally {
          setJobsLoading(false);
        }
      }
    };
    
    fetchJobs();
  }, [isAuthenticated, token]);
  
  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3">Loading your dashboard...</p>
        </div>
      </div>
    );
  }
  
  // Show dashboard content
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <button
            onClick={logout}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
        
        {user && (
          <div className="mb-6">
            <h2 className="text-lg font-medium text-gray-900 mb-2">Your Profile</h2>
            <div className="bg-gray-50 p-4 rounded">
              <p><strong>Name:</strong> {user.full_name || 'Not provided'}</p>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Account Type:</strong> {user.user_type === 'candidate' ? 'Job Seeker' : 'Employer'}</p>
            </div>
          </div>
        )}
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Jobs</h2>
        
        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded mb-4">
            {error}
          </div>
        )}
        
        {jobsLoading ? (
          <p>Loading jobs...</p>
        ) : jobs.length > 0 ? (
          <div className="space-y-4">
            {jobs.slice(0, 5).map((job) => (
              <div key={job.id} className="border rounded p-4 hover:bg-gray-50">
                <h3 className="font-medium">{job.title}</h3>
                <p className="text-sm text-gray-500">{job.company}</p>
                <p className="mt-2 text-sm">{job.description.substring(0, 150)}...</p>
              </div>
            ))}
          </div>
        ) : (
          <p>No jobs found. Check back later for new opportunities.</p>
        )}
      </div>
    </div>
  );
} 