'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { jobsApi, projectsApi, candidatesApi, enhancedRecommendationsApi } from '../services/api';
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Users, 
  Briefcase, 
  FolderOpen, 
  Star,
  MapPin,
  Mail,
  Phone,
  Award,
  Search,
  Filter,
  Download,
  Eye,
  MessageCircle,
  Calendar,
  TrendingUp,
  Target,
  Clock
} from 'lucide-react';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  type: string;
  posted_date: string;
  applications_count?: number;
}

interface Project {
  id: string;
  title: string;
  client: string;
  budget: string;
  duration: string;
  skills_required: string[];
  status: string;
}

interface CandidateRecommendation {
  id: string;
  candidate_id: string;
  full_name: string;
  email: string;
  phone?: string;
  location: string;
  experience_years: string;
  skills: {
    languages_frameworks?: string[];
    ai_ml_data?: string[];
    tools_platforms?: string[];
    soft_skills?: string[];
  };
  match_score: number;
  availability: string;
  salary_expectation?: string;
  bio: string;
  education?: string;
  last_active?: string;
}

export default function EmployerCandidatesPage() {
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Data states
  const [jobs, setJobs] = useState<Job[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [candidates, setCandidates] = useState<CandidateRecommendation[]>([]);
  
  // Filter states
  const [activeTab, setActiveTab] = useState<'jobs' | 'projects'>('jobs');
  const [selectedJobId, setSelectedJobId] = useState<string>('');
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [minMatchScore, setMinMatchScore] = useState(70);
  const [experienceFilter, setExperienceFilter] = useState('any');
  const [locationFilter, setLocationFilter] = useState('');

  useEffect(() => {
    if (user?.user_type === 'employer' && token) {
      fetchEmployerData();
    }
  }, [user, token]);

  useEffect(() => {
    if (activeTab === 'jobs' && selectedJobId) {
      fetchCandidatesForJob(selectedJobId);
    } else if (activeTab === 'projects' && selectedProjectId) {
      fetchCandidatesForProject(selectedProjectId);
    }
  }, [selectedJobId, selectedProjectId, activeTab]);

  const fetchEmployerData = async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      setError(null);

      // Fetch employer's jobs
      try {
        const jobsData = await jobsApi.getJobs(token);
        setJobs(Array.isArray(jobsData) ? jobsData : []);
        if (jobsData.length > 0) {
          setSelectedJobId(jobsData[0].id);
        }
      } catch (err) {
        console.log('No jobs found, using mock data');
        const mockJobs = getMockJobs();
        setJobs(mockJobs);
        setSelectedJobId(mockJobs[0].id);
      }

      // Fetch employer's projects
      try {
        const projectsData = await projectsApi.getProjects(token);
        setProjects(Array.isArray(projectsData) ? projectsData : []);
      } catch (err) {
        console.log('No projects found, using mock data');
        setProjects(getMockProjects());
      }

    } catch (err) {
      console.error('Failed to fetch employer data:', err);
      setError('Failed to load employer data');
    } finally {
      setLoading(false);
    }
  };

  const fetchCandidatesForJob = async (jobId: string) => {
    if (!token) return;
    
    try {
      setLoading(true);
      // This would be the actual API call for job-specific candidate recommendations
      const candidatesData = await enhancedRecommendationsApi.getCandidatesForJob(token, jobId);
      // Backend returns an object with candidates array
      const candidates = (candidatesData as any)?.candidates || candidatesData || [];
      setCandidates(Array.isArray(candidates) ? candidates : []);
    } catch (err) {
      console.error('Failed to fetch candidates for job:', err);
      setCandidates(getMockCandidatesForJob(jobId));
    } finally {
      setLoading(false);
    }
  };

  const fetchCandidatesForProject = async (projectId: string) => {
    if (!token) return;
    
    try {
      setLoading(true);
      // This would be the actual API call for project-specific candidate recommendations
      const candidatesData = await enhancedRecommendationsApi.getCandidatesForProject(token, projectId);
      // Backend returns an object with candidates array
      const candidates = (candidatesData as any)?.candidates || candidatesData || [];
      setCandidates(Array.isArray(candidates) ? candidates : []);
    } catch (err) {
      console.error('Failed to fetch candidates for project:', err);
      setCandidates(getMockCandidatesForProject(projectId));
    } finally {
      setLoading(false);
    }
  };

  const getMockJobs = (): Job[] => [
    {
      id: 'job-1',
      title: 'Senior Learning Technology Specialist',
      company: 'TechCorp Inc.',
      location: 'San Francisco, CA',
      type: 'Full-time',
      posted_date: '2024-01-15',
      applications_count: 23
    },
    {
      id: 'job-2',
      title: 'Instructional Designer',
      company: 'TechCorp Inc.',
      location: 'Remote',
      type: 'Contract',
      posted_date: '2024-01-10',
      applications_count: 18
    },
    {
      id: 'job-3',
      title: 'E-Learning Developer',
      company: 'TechCorp Inc.',
      location: 'Austin, TX',
      type: 'Full-time',
      posted_date: '2024-01-08',
      applications_count: 31
    }
  ];

  const getMockProjects = (): Project[] => [
    {
      id: 'proj-1',
      title: 'Corporate Training Platform',
      client: 'Global Enterprise',
      budget: '$15,000 - $25,000',
      duration: '4 months',
      skills_required: ['React', 'Node.js', 'LMS', 'SCORM'],
      status: 'Active'
    },
    {
      id: 'proj-2',
      title: 'Learning Analytics Dashboard',
      client: 'Education Startup',
      budget: '$8,000 - $12,000',
      duration: '2 months',
      skills_required: ['Python', 'Data Visualization', 'Machine Learning'],
      status: 'Planning'
    }
  ];

  const getMockCandidatesForJob = (jobId: string): CandidateRecommendation[] => [
    {
      id: 'rec-1',
      candidate_id: 'cand-1',
      full_name: 'Sarah Chen',
      email: 'sarah.chen@email.com',
      phone: '+1-555-0123',
      location: 'San Francisco, CA',
      experience_years: '5+ years',
      skills: {
        languages_frameworks: ['React', 'JavaScript', 'Python'],
        ai_ml_data: ['Machine Learning', 'Data Analysis'],
        tools_platforms: ['Adobe Creative', 'LMS', 'SCORM'],
        soft_skills: ['Leadership', 'Communication', 'Project Management']
      },
      match_score: 92,
      availability: 'Available',
      salary_expectation: '$85,000 - $95,000',
      bio: 'Experienced Learning Technology Specialist with expertise in e-learning development and instructional design.',
      education: 'MS in Educational Technology, Stanford University',
      last_active: '2 hours ago'
    },
    {
      id: 'rec-2',
      candidate_id: 'cand-2',
      full_name: 'Michael Rodriguez',
      email: 'michael.r@email.com',
      phone: '+1-555-0456',
      location: 'Austin, TX',
      experience_years: '7+ years',
      skills: {
        languages_frameworks: ['Vue.js', 'Node.js', 'PHP'],
        ai_ml_data: ['Learning Analytics', 'Data Visualization'],
        tools_platforms: ['Moodle', 'Canvas', 'Articulate'],
        soft_skills: ['Team Collaboration', 'Problem Solving', 'Mentoring']
      },
      match_score: 88,
      availability: 'Available in 2 weeks',
      salary_expectation: '$90,000 - $100,000',
      bio: 'Senior instructional designer and developer with focus on corporate training solutions.',
      education: 'MBA in Learning & Development, UT Austin',
      last_active: '1 day ago'
    },
    {
      id: 'rec-3',
      candidate_id: 'cand-3',
      full_name: 'Emily Thompson',
      email: 'emily.thompson@email.com',
      location: 'Remote (US)',
      experience_years: '4+ years',
      skills: {
        languages_frameworks: ['Angular', 'TypeScript', 'HTML5'],
        ai_ml_data: ['Learning Pathways', 'User Analytics'],
        tools_platforms: ['Salesforce', 'HubSpot', 'Google Analytics'],
        soft_skills: ['Creative Thinking', 'User Experience', 'Agile Development']
      },
      match_score: 85,
      availability: 'Available',
      salary_expectation: '$75,000 - $85,000',
      bio: 'Creative e-learning developer with strong UX/UI design skills and experience in gamification.',
      education: 'BA in Interactive Media Design, UCLA',
      last_active: '5 hours ago'
    }
  ];

  const getMockCandidatesForProject = (projectId: string): CandidateRecommendation[] => [
    {
      id: 'rec-p1',
      candidate_id: 'cand-p1',
      full_name: 'David Kim',
      email: 'david.kim@email.com',
      phone: '+1-555-0789',
      location: 'Seattle, WA',
      experience_years: '6+ years',
      skills: {
        languages_frameworks: ['React', 'Node.js', 'Python'],
        ai_ml_data: ['Machine Learning', 'Data Science', 'Analytics'],
        tools_platforms: ['AWS', 'Docker', 'MongoDB'],
        soft_skills: ['Problem Solving', 'Innovation', 'Technical Leadership']
      },
      match_score: 94,
      availability: 'Available',
      salary_expectation: 'Project: $120/hour',
      bio: 'Full-stack developer specializing in learning analytics and data-driven educational platforms.',
      education: 'MS in Computer Science, University of Washington',
      last_active: '30 minutes ago'
    }
  ];

  const filteredCandidates = candidates.filter(candidate => {
    const matchesSearch = searchTerm === '' || 
      candidate.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      candidate.bio.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesScore = candidate.match_score >= minMatchScore;
    
    const matchesLocation = locationFilter === '' || 
      candidate.location.toLowerCase().includes(locationFilter.toLowerCase());
    
    const matchesExperience = experienceFilter === 'any' || experienceFilter === '' || 
      candidate.experience_years.includes(experienceFilter);

    return matchesSearch && matchesScore && matchesLocation && matchesExperience;
  });

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'bg-green-100 text-green-800';
    if (score >= 80) return 'bg-blue-100 text-blue-800';
    if (score >= 70) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  if (!user || user.user_type !== 'employer') {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
          <p className="text-gray-600">This page is only accessible to employers.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-4"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Candidate Recommendations</h1>
            <p className="text-gray-600 mt-2">
              Find the perfect candidates for your jobs and projects
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export List
            </Button>
            <Button variant="outline" size="sm">
              <Filter className="h-4 w-4 mr-2" />
              Advanced Filters
            </Button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Tabs for Jobs and Projects */}
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'jobs' | 'projects')} className="mb-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="jobs" className="flex items-center gap-2">
              <Briefcase className="h-4 w-4" />
              Job Positions ({jobs.length})
            </TabsTrigger>
            <TabsTrigger value="projects" className="flex items-center gap-2">
              <FolderOpen className="h-4 w-4" />
              Projects ({projects.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="jobs" className="space-y-6">
            {/* Job Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Briefcase className="h-5 w-5" />
                  Select Job Position
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={selectedJobId} onValueChange={setSelectedJobId}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Choose a job to see candidate recommendations" />
                  </SelectTrigger>
                  <SelectContent>
                    {jobs.map((job) => (
                      <SelectItem key={job.id} value={job.id}>
                        <div className="flex flex-col">
                          <span className="font-medium">{job.title}</span>
                          <span className="text-sm text-gray-500">{job.location} • {job.applications_count} applications</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="projects" className="space-y-6">
            {/* Project Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FolderOpen className="h-5 w-5" />
                  Select Project
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={selectedProjectId} onValueChange={setSelectedProjectId}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Choose a project to see candidate recommendations" />
                  </SelectTrigger>
                  <SelectContent>
                    {projects.map((project) => (
                      <SelectItem key={project.id} value={project.id}>
                        <div className="flex flex-col">
                          <span className="font-medium">{project.title}</span>
                          <span className="text-sm text-gray-500">{project.client} • {project.budget}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Filters */}
        {(selectedJobId || selectedProjectId) && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Filter Candidates
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Search
                  </label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search candidates..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Min. Match Score
                  </label>
                  <Select value={minMatchScore.toString()} onValueChange={(value) => setMinMatchScore(parseInt(value))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="60">60%+</SelectItem>
                      <SelectItem value="70">70%+</SelectItem>
                      <SelectItem value="80">80%+</SelectItem>
                      <SelectItem value="90">90%+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Experience
                  </label>
                  <Select value={experienceFilter} onValueChange={setExperienceFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any experience" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any experience</SelectItem>
                      <SelectItem value="2+">2+ years</SelectItem>
                      <SelectItem value="5+">5+ years</SelectItem>
                      <SelectItem value="7+">7+ years</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location
                  </label>
                  <Input
                    placeholder="Filter by location..."
                    value={locationFilter}
                    onChange={(e) => setLocationFilter(e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Candidates List */}
        {(selectedJobId || selectedProjectId) && (
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Recommended Candidates ({filteredCandidates.length})
                </CardTitle>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Sort by Match
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredCandidates.map((candidate) => (
                  <div key={candidate.id} className="border rounded-lg p-6 hover:bg-gray-50">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">{candidate.full_name}</h3>
                          <Badge className={getMatchScoreColor(candidate.match_score)}>
                            {candidate.match_score}% Match
                          </Badge>
                          <Badge variant="outline" className="text-green-600">
                            <Clock className="h-3 w-3 mr-1" />
                            {candidate.availability}
                          </Badge>
                        </div>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {candidate.location}
                          </span>
                          <span className="flex items-center gap-1">
                            <Award className="h-3 w-3" />
                            {candidate.experience_years}
                          </span>
                          {candidate.salary_expectation && (
                            <span className="flex items-center gap-1">
                              <Target className="h-3 w-3" />
                              {candidate.salary_expectation}
                            </span>
                          )}
                          {candidate.last_active && (
                            <span className="text-xs">
                              Last active: {candidate.last_active}
                            </span>
                          )}
                        </div>
                        
                        <p className="text-gray-700 mb-3">{candidate.bio}</p>
                        
                        {candidate.education && (
                          <p className="text-sm text-gray-600 mb-3">
                            <span className="font-medium">Education:</span> {candidate.education}
                          </p>
                        )}
                        
                        {/* Skills */}
                        <div className="space-y-2">
                          {candidate.skills.languages_frameworks && candidate.skills.languages_frameworks.length > 0 && (
                            <div>
                              <span className="text-sm font-medium text-gray-700">Technical Skills: </span>
                              <div className="inline-flex flex-wrap gap-1 mt-1">
                                {candidate.skills.languages_frameworks.map((skill, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {skill}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {candidate.skills.soft_skills && candidate.skills.soft_skills.length > 0 && (
                            <div>
                              <span className="text-sm font-medium text-gray-700">Soft Skills: </span>
                              <div className="inline-flex flex-wrap gap-1 mt-1">
                                {candidate.skills.soft_skills.map((skill, index) => (
                                  <Badge key={index} variant="outline" className="text-xs">
                                    {skill}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex flex-col gap-2 ml-6">
                        <Button size="sm" className="flex items-center gap-2">
                          <Eye className="h-4 w-4" />
                          View Profile
                        </Button>
                        <Button size="sm" variant="outline" className="flex items-center gap-2">
                          <MessageCircle className="h-4 w-4" />
                          Contact
                        </Button>
                        <Button size="sm" variant="outline" className="flex items-center gap-2">
                          <Star className="h-4 w-4" />
                          Shortlist
                        </Button>
                      </div>
                    </div>
                    
                    {/* Contact Information */}
                    <div className="border-t pt-3 mt-3">
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <Mail className="h-3 w-3" />
                          {candidate.email}
                        </span>
                        {candidate.phone && (
                          <span className="flex items-center gap-1">
                            <Phone className="h-3 w-3" />
                            {candidate.phone}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {filteredCandidates.length === 0 && (
                  <div className="text-center py-8">
                    <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No candidates found</h3>
                    <p className="text-gray-600">
                      Try adjusting your filters or check back later for new recommendations.
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* No Selection State */}
        {!selectedJobId && !selectedProjectId && (
          <Card>
            <CardContent className="text-center py-8">
              <div className="flex justify-center mb-4">
                {activeTab === 'jobs' ? (
                  <Briefcase className="h-12 w-12 text-gray-400" />
                ) : (
                  <FolderOpen className="h-12 w-12 text-gray-400" />
                )}
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Select a {activeTab === 'jobs' ? 'job position' : 'project'} to view recommendations
              </h3>
              <p className="text-gray-600">
                Choose from your {activeTab === 'jobs' ? 'job postings' : 'active projects'} above to see matched candidates.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
} 