'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../contexts/AuthContext';
import { enhancedRecommendationsApi } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '../components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { 
  Briefcase, 
  MapPin, 
  DollarSign, 
  Calendar, 
  Star, 
  Heart,
  Bookmark,
  Search,
  Filter,
  TrendingUp,
  Building,
  Clock,
  Target,
  ThumbsUp,
  ThumbsDown,
  MessageSquare
} from 'lucide-react';

interface JobRecommendation {
  id: string;
  title: string;
  company: string;
  location: string;
  compensation?: string;
  employment_type: string;
  experience_level: string;
  description: string;
  required_skills: string[];
  match_score: number;
  posted_date: string;
  applications_count?: number;
  saved?: boolean;
  viewed?: boolean;
}

export default function CandidateRecommendationsPage() {
  const { user, token } = useAuth();
  const [recommendations, setRecommendations] = useState<JobRecommendation[]>([]);
  const [filteredRecommendations, setFilteredRecommendations] = useState<JobRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [experienceFilter, setExperienceFilter] = useState('');
  const [employmentTypeFilter, setEmploymentTypeFilter] = useState('');
  const [minMatchScore, setMinMatchScore] = useState(50);
  const [sortBy, setSortBy] = useState('match_score');

  // Feedback state
  const [feedbackModal, setFeedbackModal] = useState<{open: boolean, jobId: string | null}>({
    open: false,
    jobId: null
  });

  useEffect(() => {
    console.log('useEffect triggered - user:', user ? 'User present' : 'No user', 'token:', token ? 'Token present' : 'No token');
    
    if (token) {
      console.log('Token available, fetching recommendations...');
      fetchRecommendations();
    } else {
      console.log('No token available, setting mock data and stopping loading');
      // If no token, use mock data and stop loading
      const mockData = getMockRecommendations();
      console.log('Setting mock data due to no token:', mockData);
      setRecommendations(mockData);
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    console.log('Filter useEffect triggered - recommendations length:', (recommendations || []).length);
    applyFilters();
  }, [recommendations, searchTerm, locationFilter, experienceFilter, employmentTypeFilter, minMatchScore, sortBy]);

  const fetchRecommendations = async () => {
    if (!token) {
      console.log('No token available for fetching recommendations');
      return;
    }
    
    console.log('Starting to fetch recommendations with token:', token ? 'Token present' : 'No token');
    
    try {
      setLoading(true);
      console.log('Calling enhancedRecommendationsApi.getJobRecommendations...');
      
      const data = await enhancedRecommendationsApi.getJobRecommendations(token, {
        limit: 50,
        min_match_score: minMatchScore
      });
      
      console.log('API response received:', data);
      
      // Handle both array and object responses
      const jobs = Array.isArray(data) ? data : data.items || data.recommendations || [];
      console.log('Processed jobs array:', jobs);
      console.log('Number of jobs:', jobs.length);
      
      // Use same logic as dashboard - if no jobs from API, use mock data
      if (jobs.length > 0) {
        setRecommendations(jobs);
      } else {
        console.log('API returned empty results, using mock data');
        const mockData = getMockRecommendations();
        console.log('Mock data:', mockData);
        setRecommendations(mockData);
      }
    } catch (err: any) {
      console.error('Error fetching recommendations:', err);
      setError('Failed to load job recommendations');
      
      // Fallback to mock data
      console.log('Falling back to mock data due to error');
      const mockData = getMockRecommendations();
      console.log('Mock data:', mockData);
      setRecommendations(mockData);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    console.log('Starting applyFilters with recommendations:', (recommendations || []).length);
    let filtered = [...(recommendations || [])];
    console.log('Initial filtered count:', filtered.length);

    // Search filter
    if (searchTerm) {
      console.log('Applying search filter for term:', searchTerm);
      filtered = filtered.filter(job => 
        job.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (job.required_skills || []).some(skill => skill?.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      console.log('After search filter:', filtered.length);
    }

    // Location filter
    if (locationFilter) {
      console.log('Applying location filter for:', locationFilter);
      filtered = filtered.filter(job => 
        job.location?.toLowerCase().includes(locationFilter.toLowerCase())
      );
      console.log('After location filter:', filtered.length);
    }

    // Experience filter
    if (experienceFilter && experienceFilter !== 'all') {
      console.log('Applying experience filter for:', experienceFilter);
      filtered = filtered.filter(job => job.experience_level === experienceFilter);
      console.log('After experience filter:', filtered.length);
    }

    // Employment type filter
    if (employmentTypeFilter && employmentTypeFilter !== 'all') {
      console.log('Applying employment type filter for:', employmentTypeFilter);
      filtered = filtered.filter(job => job.employment_type === employmentTypeFilter);
      console.log('After employment type filter:', filtered.length);
    }

    // Match score filter
    console.log('Applying match score filter - minimum:', minMatchScore);
    filtered = filtered.filter(job => (job.match_score || 0) >= minMatchScore);
    console.log('After match score filter:', filtered.length);

    // Sort
    console.log('Applying sort by:', sortBy);
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'match_score':
          return (b.match_score || 0) - (a.match_score || 0);
        case 'posted_date':
          return new Date(b.posted_date || 0).getTime() - new Date(a.posted_date || 0).getTime();
        case 'company':
          return (a.company || '').localeCompare(b.company || '');
        default:
          return (b.match_score || 0) - (a.match_score || 0);
      }
    });

    console.log('Final filtered recommendations count:', filtered.length);
    setFilteredRecommendations(filtered);
  };

  const handleSaveJob = async (jobId: string) => {
    // Implement save job functionality
    setRecommendations(prev => 
      prev.map(job => 
        job.id === jobId ? { ...job, saved: !job.saved } : job
      )
    );
  };

  const handleJobFeedback = async (jobId: string, rating: 'positive' | 'negative', comment?: string) => {
    if (!token) return;
    
    try {
      await enhancedRecommendationsApi.submitFeedback(token, {
        recommendation_id: jobId,
        recommendation_type: 'job',
        rating: rating === 'positive' ? 5 : 1,
        comment: comment,
        user_action: rating === 'positive' ? 'liked' : 'dismissed'
      });
      
      setFeedbackModal({ open: false, jobId: null });
      // Optionally refresh recommendations
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 80) return 'text-blue-600 bg-blue-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-gray-600 bg-gray-100';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  const getMockRecommendations = (): JobRecommendation[] => [
    {
      id: '1',
      title: 'Senior Learning Experience Designer',
      company: 'TechCorp Inc.',
      location: 'San Francisco, CA',
      compensation: '$120,000 - $150,000',
      employment_type: 'Full-time',
      experience_level: 'Senior',
      description: 'We are seeking an experienced Learning Experience Designer to create innovative training programs...',
      required_skills: ['Instructional Design', 'LMS', 'Content Development', 'Project Management'],
      match_score: 92,
      posted_date: '2024-01-15',
      applications_count: 23,
    },
    {
      id: '2',
      title: 'Corporate Training Consultant',
      company: 'Global Learning Corp',
      location: 'Remote',
      compensation: '$80,000 - $100,000',
      employment_type: 'Contract',
      experience_level: 'Mid-level',
      description: 'Join our team as a Corporate Training Consultant to help organizations develop their talent...',
      required_skills: ['Training', 'Curriculum Design', 'Leadership Development', 'Analytics'],
      match_score: 85,
      posted_date: '2024-01-12',
      applications_count: 45,
    }
  ];

  if (loading) {
    console.log('Rendering loading state...');
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-10 bg-gray-200 rounded"></div>
              ))}
            </div>
            <div className="space-y-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white rounded-lg shadow p-6">
                  <div className="h-6 bg-gray-200 rounded mb-4"></div>
                  <div className="space-y-3">
                    <div className="h-4 bg-gray-200 rounded"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!user || !token) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please log in to see your job recommendations</h1>
          <Button asChild>
            <Link href="/login">Log In</Link>
          </Button>
        </div>
      </div>
    );
  }

  console.log('Rendering main page with state:', {
    loading,
    error,
    recommendationsCount: (recommendations || []).length,
    filteredCount: (filteredRecommendations || []).length,
    user: user ? 'Present' : 'Missing',
    token: token ? 'Present' : 'Missing'
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Job Recommendations</h1>
          <p className="text-lg text-gray-600">
            Personalized job matches based on your skills, experience, and preferences.
          </p>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search jobs, skills, companies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              <Input
                placeholder="Location"
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
              />
              
              <Select value={experienceFilter} onValueChange={setExperienceFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Experience Level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="Entry-level">Entry Level</SelectItem>
                  <SelectItem value="Mid-level">Mid Level</SelectItem>
                  <SelectItem value="Senior">Senior</SelectItem>
                  <SelectItem value="Executive">Executive</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={employmentTypeFilter} onValueChange={setEmploymentTypeFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Employment Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="Full-time">Full-time</SelectItem>
                  <SelectItem value="Part-time">Part-time</SelectItem>
                  <SelectItem value="Contract">Contract</SelectItem>
                  <SelectItem value="Freelance">Freelance</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium">Min Match Score:</label>
                <Select value={minMatchScore.toString()} onValueChange={(value) => setMinMatchScore(parseInt(value))}>
                  <SelectTrigger className="w-20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="50">50%</SelectItem>
                    <SelectItem value="60">60%</SelectItem>
                    <SelectItem value="70">70%</SelectItem>
                    <SelectItem value="80">80%</SelectItem>
                    <SelectItem value="90">90%</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium">Sort by:</label>
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="match_score">Match Score</SelectItem>
                    <SelectItem value="posted_date">Posted Date</SelectItem>
                    <SelectItem value="company">Company</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Summary */}
        <div className="mb-6">
          <p className="text-gray-600">
            Showing {filteredRecommendations.length} job recommendations
          </p>
        </div>

        {/* Job Recommendations */}
        <div className="space-y-6">
          {(filteredRecommendations || []).map((job, jobIndex) => (
            <Card key={job.id || `job-${jobIndex}`} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-semibold text-gray-900">{job.title}</h3>
                      <Badge className={`${getMatchScoreColor(job.match_score || 0)} text-xs font-medium px-2 py-1`}>
                        {job.match_score || 0}% Match
                      </Badge>
                    </div>
                    
                    <div className="flex items-center gap-4 text-gray-600 mb-3">
                      <div className="flex items-center gap-1">
                        <Building className="h-4 w-4" />
                        <span>{job.company}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        <span>{job.location}</span>
                      </div>
                      {job.compensation && (
                        <div className="flex items-center gap-1">
                          <DollarSign className="h-4 w-4" />
                          <span>{job.compensation}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>{formatDate(job.posted_date)}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleSaveJob(job.id)}
                      className={job.saved ? 'text-blue-600' : ''}
                    >
                      <Bookmark className={`h-4 w-4 ${job.saved ? 'fill-current' : ''}`} />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setFeedbackModal({ open: true, jobId: job.id })}
                    >
                      <MessageSquare className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                
                <p className="text-gray-700 mb-4 line-clamp-2">{job.description}</p>
                
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Required Skills:</h4>
                  <div className="flex flex-wrap gap-2">
                    {(job.required_skills || []).map((skill, skillIndex) => (
                      <Badge key={`${job.id || jobIndex}-skill-${skillIndex}-${skill?.toLowerCase().replace(/\s+/g, '-') || 'unknown'}`} variant="outline" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span className="capitalize">{job.employment_type}</span>
                    <span>{job.experience_level}</span>
                    {job.applications_count && (
                      <span>{job.applications_count} applications</span>
                    )}
                  </div>
                  
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleJobFeedback(job.id, 'negative')}
                    >
                      <ThumbsDown className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleJobFeedback(job.id, 'positive')}
                    >
                      <ThumbsUp className="h-4 w-4" />
                    </Button>
                    <Button asChild>
                      <Link href={`/jobs/${job.id || 'unknown'}`}>
                        View Details
                      </Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {(filteredRecommendations || []).length === 0 && !loading && (
          <div className="text-center py-12">
            <Briefcase className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No job recommendations found</h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your filters or updating your profile to get better matches.
            </p>
            <Button asChild>
              <Link href="/candidate-profile">
                Update Profile
              </Link>
            </Button>
          </div>
        )}
      </div>
    </div>
  );
} 