"use client";

import { useState, useEffect } from "react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { Search, Filter } from "lucide-react";
import JobCard from "../components/JobCard";
import { jobsApi } from "../services/api";

export default function Jobs() {
  const [allJobs, setAllJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [jobType, setJobType] = useState("all");
  const [remoteOnly, setRemoteOnly] = useState(false);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const jobsData = await jobsApi.getJobsPublic();
        setAllJobs(jobsData);
        setError(null);
      } catch (err) {
        console.error('Error fetching jobs:', err);
        setError('Failed to load jobs');
        setAllJobs([]);
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
  
  // Filter jobs based on search and filters
  const filteredJobs = allJobs.filter(job => {
    const matchesSearch = !searchTerm || 
      job.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.location?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.requirements?.some((req: string) => req.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesType = jobType === "all" || job.employment_type === jobType;
    const matchesRemote = !remoteOnly || job.remote_option || job.location?.toLowerCase().includes('remote');
    
    return matchesSearch && matchesType && matchesRemote;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 py-8">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              L&D Jobs
            </h1>
            <p className="text-lg text-slate-600 max-w-3xl">
              Discover exciting Learning & Development opportunities from organizations worldwide.
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {/* Loading skeletons */}
            {[1, 2, 3, 4, 5, 6].map((i) => (
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
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 py-8">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              L&D Jobs
            </h1>
            <p className="text-lg text-slate-600 max-w-3xl">
              Discover exciting Learning & Development opportunities from organizations worldwide.
            </p>
          </div>
          
          <div className="text-center py-12">
            <p className="text-slate-600 mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            L&D Jobs
          </h1>
          <p className="text-lg text-slate-600 max-w-3xl">
            Discover exciting Learning & Development opportunities from organizations worldwide. 
            Find your next career move in the L&D industry.
          </p>
        </div>

        {/* Search and Filters */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="md:col-span-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
                  <Input
                    placeholder="Search jobs, companies, or skills..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Job Type Filter */}
              <div>
                <Select value={jobType} onValueChange={setJobType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Job Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="full-time">Full-time</SelectItem>
                    <SelectItem value="part-time">Part-time</SelectItem>
                    <SelectItem value="contract">Contract</SelectItem>
                    <SelectItem value="freelance">Freelance</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Remote Filter */}
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="remote"
                  checked={remoteOnly}
                  onCheckedChange={(checked) => setRemoteOnly(checked === true)}
                />
                <label htmlFor="remote" className="text-sm font-medium">
                  Remote Only
                </label>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="mb-6">
          <p className="text-slate-600">
            Showing {filteredJobs.length} of {allJobs.length} jobs
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredJobs.map((job) => (
            <JobCard key={job.id} job={transformJobData(job)} />
          ))}
        </div>

        {/* No results */}
        {filteredJobs.length === 0 && !loading && (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-slate-900 mb-2">
              No jobs found
            </h3>
            <p className="text-slate-600">
              Try adjusting your search criteria or check back later for new opportunities.
            </p>
          </div>
        )}

        {/* Pagination */}
        {filteredJobs.length > 0 && (
          <div className="flex justify-center mt-8">
            <Button variant="outline" className="mx-1">1</Button>
            <Button variant="outline" className="mx-1">2</Button>
            <Button variant="outline" className="mx-1">3</Button>
            <Button variant="outline" className="mx-1">Next</Button>
          </div>
        )}
      </div>
    </div>
  );
} 