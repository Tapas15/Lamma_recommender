"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { 
  Search, 
  Filter, 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  Save, 
  X,
  Briefcase,
  MapPin,
  Calendar,
  DollarSign,
  Users,
  Building,
  Clock
} from "lucide-react";
import JobCard from "../components/JobCard";
import { jobsApi } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  employment_type: string;
  remote_option: boolean;
  salary_range?: {
    min: number;
    max: number;
    currency: string;
  };
  description: string;
  requirements: string[];
  responsibilities?: string[];
  qualifications?: string[];
  benefits?: string[];
  posted_date: string;
  status: 'draft' | 'published' | 'closed';
  employer_id?: string;
}

export default function Jobs() {
  const { user, token } = useAuth();
  const [allJobs, setAllJobs] = useState<Job[]>([]);
  const [myJobs, setMyJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [jobType, setJobType] = useState("all");
  const [remoteOnly, setRemoteOnly] = useState(false);
  
  // Job management states
  const [showJobForm, setShowJobForm] = useState(false);
  const [editingJob, setEditingJob] = useState<Job | null>(null);
  const [formData, setFormData] = useState<Partial<Job>>({
    title: '',
    company: '',
    location: '',
    employment_type: 'full-time',
    remote_option: false,
    description: '',
    requirements: [],
    responsibilities: [],
    qualifications: [],
    benefits: [],
    status: 'draft'
  });
  const [saving, setSaving] = useState(false);

  const isEmployer = user?.user_type === 'employer';

  useEffect(() => {
    fetchJobs();
    if (isEmployer && token) {
      fetchMyJobs();
    }
  }, [isEmployer, token]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const jobsData = await jobsApi.getJobsPublic();
      setAllJobs(jobsData || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching jobs:', err);
      setError('Failed to load jobs');
      setAllJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchMyJobs = async () => {
    if (!token) return;
    
    try {
      const jobsData = await jobsApi.getJobs(token);
      setMyJobs(jobsData || []);
    } catch (err) {
      console.error('Error fetching my jobs:', err);
      // Fallback to empty array if API fails
      setMyJobs([]);
    }
  };

  const handleCreateJob = async () => {
    if (!token || !formData.title || !formData.description) return;

    try {
      setSaving(true);
      const jobData = {
        ...formData,
        employer_id: user?.id,
        posted_date: new Date().toISOString()
      };

      await jobsApi.createJob(token, jobData);
      await fetchMyJobs();
      resetForm();
      setShowJobForm(false);
    } catch (error) {
      console.error('Failed to create job:', error);
      setError('Failed to create job');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateJob = async () => {
    if (!token || !editingJob || !formData.title || !formData.description) return;

    try {
      setSaving(true);
      await jobsApi.updateJob(token, editingJob.id, formData);
      await fetchMyJobs();
      resetForm();
      setEditingJob(null);
      setShowJobForm(false);
    } catch (error) {
      console.error('Failed to update job:', error);
      setError('Failed to update job');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!token || !confirm('Are you sure you want to delete this job?')) return;

    try {
      await jobsApi.deleteJob(token, jobId);
      await fetchMyJobs();
    } catch (error) {
      console.error('Failed to delete job:', error);
      setError('Failed to delete job');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      company: '',
      location: '',
      employment_type: 'full-time',
      remote_option: false,
      description: '',
      requirements: [],
      responsibilities: [],
      qualifications: [],
      benefits: [],
      status: 'draft'
    });
  };

  const startEditing = (job: Job) => {
    setEditingJob(job);
    setFormData({ ...job });
    setShowJobForm(true);
  };

  const addListItem = (field: 'requirements' | 'responsibilities' | 'qualifications' | 'benefits', value: string) => {
    if (!value.trim()) return;
    
    const currentList = formData[field] || [];
    setFormData({
      ...formData,
      [field]: [...currentList, value.trim()]
    });
  };

  const removeListItem = (field: 'requirements' | 'responsibilities' | 'qualifications' | 'benefits', index: number) => {
    const currentList = formData[field] || [];
    setFormData({
      ...formData,
      [field]: currentList.filter((_, i) => i !== index)
    });
  };

  // Transform job data to match JobCard expectations
  const transformJobData = (job: Job) => {
    // Ensure jobType matches the expected union type
    const mapJobType = (type: string): "full-time" | "part-time" | "contract" | "freelance" => {
      switch (type) {
        case 'full-time':
          return 'full-time';
        case 'part-time':
          return 'part-time';
        case 'contract':
          return 'contract';
        case 'freelance':
          return 'freelance';
        case 'internship':
          return 'contract'; // Map internship to contract for JobCard compatibility
        default:
          return 'full-time'; // Default fallback
      }
    };

    return {
      id: job.id,
      title: job.title,
      companyName: job.company,
      companyLogo: "https://logo.clearbit.com/microsoft.com",
      location: job.location || "Remote",
      jobType: mapJobType(job.employment_type || "full-time"),
      remote: job.remote_option || false,
      compensation: formatSalaryRange(job.salary_range),
      postedDate: formatPostedDate(job.posted_date),
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
      job.company?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = jobType === "all" || job.employment_type === jobType;
    const matchesRemote = !remoteOnly || job.remote_option;
    
    return matchesSearch && matchesType && matchesRemote;
  });

  const filteredMyJobs = myJobs.filter(job => {
    const matchesSearch = !searchTerm || 
      job.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.location?.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 py-8">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              {isEmployer ? 'Job Management' : 'L&D Jobs'}
            </h1>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
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

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            {isEmployer ? 'Job Management' : 'L&D Jobs'}
          </h1>
          <p className="text-lg text-slate-600 max-w-3xl">
            {isEmployer 
              ? 'Manage your job postings and attract top L&D talent.'
              : 'Discover exciting Learning & Development opportunities from organizations worldwide.'
            }
          </p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Employer vs Candidate View */}
        {isEmployer ? (
          <Tabs defaultValue="my-jobs" className="space-y-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="my-jobs">My Jobs ({myJobs.length})</TabsTrigger>
              <TabsTrigger value="browse">Browse All Jobs</TabsTrigger>
            </TabsList>

            {/* My Jobs Tab */}
            <TabsContent value="my-jobs" className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">My Job Postings</h2>
                <Button 
                  onClick={() => {
                    resetForm();
                    setEditingJob(null);
                    setShowJobForm(true);
                  }}
                  className="flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Post New Job
                </Button>
              </div>

              {/* Job Creation/Edit Form */}
              {showJobForm && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      {editingJob ? 'Edit Job' : 'Create New Job'}
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setShowJobForm(false);
                          setEditingJob(null);
                          resetForm();
                        }}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        placeholder="Job Title"
                        value={formData.title || ''}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      />
                      <Input
                        placeholder="Company Name"
                        value={formData.company || ''}
                        onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                      />
                      <Input
                        placeholder="Location"
                        value={formData.location || ''}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      />
                      <Select 
                        value={formData.employment_type || 'full-time'} 
                        onValueChange={(value) => setFormData({ ...formData, employment_type: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="full-time">Full-time</SelectItem>
                          <SelectItem value="part-time">Part-time</SelectItem>
                          <SelectItem value="contract">Contract</SelectItem>
                          <SelectItem value="internship">Internship</SelectItem>
                          <SelectItem value="freelance">Freelance</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="remote"
                        checked={formData.remote_option || false}
                        onCheckedChange={(checked) => setFormData({ ...formData, remote_option: checked === true })}
                      />
                      <label htmlFor="remote" className="text-sm font-medium">
                        Remote Work Available
                      </label>
                    </div>

                    <Textarea
                      placeholder="Job Description"
                      value={formData.description || ''}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={4}
                    />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Requirements</label>
                        <div className="space-y-2">
                          <div className="flex gap-2">
                            <Input 
                              placeholder="Add requirement..."
                              onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  addListItem('requirements', e.currentTarget.value);
                                  e.currentTarget.value = '';
                                }
                              }}
                            />
                            <Button 
                              size="sm"
                              onClick={(e) => {
                                const input = e.currentTarget.parentElement?.querySelector('input') as HTMLInputElement;
                                if (input) {
                                  addListItem('requirements', input.value);
                                  input.value = '';
                                }
                              }}
                            >
                              Add
                            </Button>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {(formData.requirements || []).map((req, index) => (
                              <Badge key={index} variant="secondary" className="flex items-center gap-1">
                                {req}
                                <button onClick={() => removeListItem('requirements', index)}>
                                  <X className="h-3 w-3" />
                                </button>
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">Responsibilities</label>
                        <div className="space-y-2">
                          <div className="flex gap-2">
                            <Input 
                              placeholder="Add responsibility..."
                              onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  addListItem('responsibilities', e.currentTarget.value);
                                  e.currentTarget.value = '';
                                }
                              }}
                            />
                            <Button 
                              size="sm"
                              onClick={(e) => {
                                const input = e.currentTarget.parentElement?.querySelector('input') as HTMLInputElement;
                                if (input) {
                                  addListItem('responsibilities', input.value);
                                  input.value = '';
                                }
                              }}
                            >
                              Add
                            </Button>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {(formData.responsibilities || []).map((resp, index) => (
                              <Badge key={index} variant="secondary" className="flex items-center gap-1">
                                {resp}
                                <button onClick={() => removeListItem('responsibilities', index)}>
                                  <X className="h-3 w-3" />
                                </button>
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    <Select 
                      value={formData.status || 'draft'} 
                      onValueChange={(value) => setFormData({ ...formData, status: value as 'draft' | 'published' | 'closed' })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="published">Published</SelectItem>
                        <SelectItem value="closed">Closed</SelectItem>
                      </SelectContent>
                    </Select>

                    <div className="flex justify-end gap-2">
                      <Button 
                        variant="outline"
                        onClick={() => {
                          setShowJobForm(false);
                          setEditingJob(null);
                          resetForm();
                        }}
                      >
                        Cancel
                      </Button>
                      <Button 
                        onClick={editingJob ? handleUpdateJob : handleCreateJob}
                        disabled={saving || !formData.title || !formData.description}
                      >
                        <Save className="h-4 w-4 mr-2" />
                        {saving ? 'Saving...' : editingJob ? 'Update Job' : 'Create Job'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* My Jobs List */}
              <div className="space-y-4">
                {filteredMyJobs.length === 0 ? (
                  <Card>
                    <CardContent className="text-center py-8">
                      <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs posted yet</h3>
                      <p className="text-gray-600 mb-4">Create your first job posting to attract top talent</p>
                      <Button onClick={() => setShowJobForm(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Post Your First Job
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  filteredMyJobs.map((job) => (
                    <Card key={job.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                              <Badge 
                                variant={job.status === 'published' ? 'default' : job.status === 'draft' ? 'secondary' : 'outline'}
                              >
                                {job.status}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                              <span className="flex items-center gap-1">
                                <Building className="h-3 w-3" />
                                {job.company}
                              </span>
                              <span className="flex items-center gap-1">
                                <MapPin className="h-3 w-3" />
                                {job.location}
                              </span>
                              <span className="flex items-center gap-1">
                                <Calendar className="h-3 w-3" />
                                {formatPostedDate(job.posted_date)}
                              </span>
                              {job.remote_option && (
                                <Badge variant="outline" className="text-xs">Remote</Badge>
                              )}
                            </div>
                            <p className="text-gray-700 mb-3 line-clamp-2">{job.description}</p>
                            {job.requirements && job.requirements.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {job.requirements.slice(0, 3).map((req, index) => (
                                  <Badge key={index} variant="outline" className="text-xs">
                                    {req}
                                  </Badge>
                                ))}
                                {job.requirements.length > 3 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{job.requirements.length - 3} more
                                  </Badge>
                                )}
                              </div>
                            )}
                          </div>
                          
                          <div className="flex flex-col gap-2 ml-6">
                            <Button size="sm" variant="outline" onClick={() => startEditing(job)}>
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="text-red-600 hover:text-red-700"
                              onClick={() => handleDeleteJob(job.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </TabsContent>

            {/* Browse All Jobs Tab */}
            <TabsContent value="browse" className="space-y-6">
              {/* Search and Filters */}
              <Card>
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
                          <SelectItem value="internship">Internship</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="remote-filter"
                        checked={remoteOnly}
                        onCheckedChange={(checked) => setRemoteOnly(checked === true)}
                      />
                      <label htmlFor="remote-filter" className="text-sm font-medium">
                        Remote Only
                      </label>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Jobs Grid */}
              {filteredJobs.length === 0 ? (
                <div className="text-center py-12">
                  <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
                  <p className="text-gray-600">Try adjusting your search criteria</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                  {filteredJobs.map((job) => (
                    <JobCard key={job.id} job={transformJobData(job)} />
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        ) : (
          // Candidate View (Original functionality)
          <>
            {/* Search and Filters */}
            <Card className="mb-8">
              <CardContent className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
                        <SelectItem value="internship">Internship</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="remote-filter"
                      checked={remoteOnly}
                      onCheckedChange={(checked) => setRemoteOnly(checked === true)}
                    />
                    <label htmlFor="remote-filter" className="text-sm font-medium">
                      Remote Only
                    </label>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Jobs Results */}
            {filteredJobs.length === 0 ? (
              <div className="text-center py-12">
                <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
                <p className="text-gray-600">Try adjusting your search criteria</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredJobs.map((job) => (
                  <JobCard key={job.id} job={transformJobData(job)} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
} 