"use client";

import { useState, useEffect } from "react";
import { ArrowRight } from "lucide-react";
import Link from "next/link";
import JobCard from "./JobCard";
import { jobsApi } from "../services/api";

export default function FeaturedJobs() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const jobsData = await jobsApi.getJobsPublic();
        // Take only the first 2 jobs for featured section
        setJobs(jobsData.slice(0, 2));
        setError(null);
      } catch (err) {
        console.error('Error fetching jobs:', err);
        setError('Failed to load jobs');
        // Fallback to empty array if API fails
        setJobs([]);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  // Transform job data to match JobCard expectations
  const transformJobData = (job: any) => {
    return {
      id: job.id,
      title: job.title,
      companyName: job.company,
      companyLogo: "https://logo.clearbit.com/microsoft.com", // Default logo
      location: job.location || "Remote",
      jobType: job.employment_type || "full-time",
      remote: job.remote_option || job.location?.toLowerCase().includes('remote') || false,
      compensation: formatSalaryRange(job.salary_range),
      postedDate: formatPostedDate(job.posted_date || job.created_at),
      description: job.description,
      requirements: job.requirements || []
    };
  };

  const formatSalaryRange = (salaryRange: any) => {
    if (!salaryRange) return "Competitive salary";
    
    if (typeof salaryRange === 'string') return salaryRange;
    
    if (typeof salaryRange === 'object' && salaryRange.min && salaryRange.max) {
      const currency = salaryRange.currency || 'USD';
      return `$${salaryRange.min.toLocaleString()} - $${salaryRange.max.toLocaleString()}/${currency === 'USD' ? 'year' : 'year'}`;
    }
    
    return "Competitive salary";
  };

  const formatPostedDate = (date: any) => {
    if (!date) return "Recently posted";
    
    try {
      const postDate = new Date(date);
      const now = new Date();
      const diffTime = Math.abs(now.getTime() - postDate.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) return "1 day ago";
      if (diffDays < 7) return `${diffDays} days ago`;
      if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
      return `${Math.ceil(diffDays / 30)} months ago`;
    } catch {
      return "Recently posted";
    }
  };

  if (loading) {
    return (
      <section className="py-20 bg-slate-50">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
                Featured L&D Opportunities
              </h2>
              <p className="text-lg text-slate-600 max-w-2xl">
                Discover the latest Learning & Development positions from top organizations worldwide.
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Loading skeletons */}
            {[1, 2].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div className="h-6 bg-gray-200 rounded mb-4"></div>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded mb-4 w-3/4"></div>
                <div className="flex space-x-2 mb-4">
                  <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                  <div className="h-6 bg-gray-200 rounded-full w-20"></div>
                </div>
                <div className="h-10 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="py-20 bg-slate-50">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
                Featured L&D Opportunities
              </h2>
              <p className="text-lg text-slate-600 max-w-2xl">
                Discover the latest Learning & Development positions from top organizations worldwide.
              </p>
            </div>
          </div>
          <div className="text-center py-12">
            <p className="text-slate-600 mb-4">{error}</p>
            <Link 
              href="/jobs" 
              className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
            >
              Browse all jobs
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-20 bg-slate-50">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex justify-between items-center mb-12">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Featured L&D Opportunities
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl">
              Discover the latest Learning & Development positions from top organizations worldwide.
            </p>
          </div>
          <Link 
            href="/jobs" 
            className="hidden md:flex items-center text-blue-600 hover:text-blue-700 font-medium"
          >
            View all
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>

        {jobs.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {jobs.map((job) => (
              <JobCard key={job.id} job={transformJobData(job)} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-slate-600 mb-4">No featured jobs available at the moment.</p>
            <Link 
              href="/jobs" 
              className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
            >
              Browse all jobs
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        )}

        <div className="mt-8 text-center md:hidden">
          <Link 
            href="/jobs" 
            className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
          >
            View all
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </div>
    </section>
  );
} 