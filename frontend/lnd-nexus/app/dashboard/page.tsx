'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../contexts/AuthContext';
import { jobsApi, enhancedRecommendationsApi, candidateAnalyticsApi, projectsApi, applicationsApi, savedJobsApi } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { 
  User, 
  Briefcase, 
  TrendingUp, 
  Target, 
  BookOpen, 
  Award,
  Bell,
  Calendar,
  BarChart3,
  Star,
  MapPin,
  Clock,
  DollarSign,
  ChevronRight,
  Eye,
  Heart,
  Plus,
  Code,
  FolderOpen,
  Search,
  Users
} from 'lucide-react';

interface DashboardStats {
  profile_completion: number;
  job_applications: number;
  profile_views: number;
  saved_jobs: number;
  recommendation_matches: number;
}

interface RecentActivity {
  type: 'job_view' | 'application' | 'profile_update' | 'recommendation';
  title: string;
  description: string;
  timestamp: string;
  link?: string;
}

export default function CandidateDashboard() {
  const { user, token, logout } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [projectRecommendations, setProjectRecommendations] = useState<any[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    profile_completion: 75.6789,
    job_applications: 12,
    profile_views: 48,
    saved_jobs: 8,
    recommendation_matches: 15
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);

  useEffect(() => {
    if (user && token) {
      fetchDashboardData();
    }
  }, [user, token]);

  const fetchDashboardData = async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      setError(null);

      // Only fetch recommendations for candidates, not employers
      if (user?.user_type !== 'employer') {
        // Fetch job recommendations
        try {
          console.log('Fetching job recommendations...');
          const recData = await enhancedRecommendationsApi.getJobRecommendations(token!, { limit: 3 });
          console.log('Raw recommendations API response:', recData);
          
          let recommendations = Array.isArray(recData) ? recData : (recData as any)?.items || [];
          
          // Handle nested job_details structure from backend API
          if (recommendations.length > 0) {
            // Check if we have nested job_details structure
            if (recommendations[0] && recommendations[0].job_details) {
              recommendations = recommendations.map((rec: any) => ({
                id: rec.job_id || rec.id || rec.job_details?.id || rec.job_details?.job_id,
                title: rec.job_details?.title || rec.title,
                company: rec.job_details?.company || rec.company,
                location: rec.job_details?.location || rec.location,
                salary_range: rec.job_details?.salary_range || rec.salary_range,
                match_score: rec.match_score,
                ...rec.job_details
              }));
            }
            
            // Additional check for missing title/company
            if (recommendations[0] && (!recommendations[0].title || !recommendations[0].company)) {
              recommendations = recommendations.map((rec: any) => ({
                ...rec,
                id: rec.id || rec.job_id || rec.job_details?.id || rec.job_details?.job_id || rec._id,
                title: rec.title || rec.job_title || rec.position || rec.name || 'Position Not Specified',
                company: rec.company || rec.employer || rec.company_name || rec.organization || 'Company Not Specified',
                location: rec.location || rec.job_location || rec.city || 'Location TBD',
                match_score: rec.match_score || rec.score || 0
              }));
            }
          }
          
          if (recommendations.length > 0 && recommendations[0].title && recommendations[0].company) {
            setRecommendations(recommendations);
          } else {
            const mockRecs = getMockRecommendations();
            setRecommendations(mockRecs);
          }
        } catch (err) {
          console.log('Job recommendations API error:', err);
          const mockRecs = getMockRecommendations();
          setRecommendations(mockRecs);
        }

        // Fetch project recommendations
        try {
          console.log('Fetching project recommendations...');
          // First try to get actual recommendations with real match scores
          try {
            const projectData = await enhancedRecommendationsApi.getProjectRecommendations(token!, { limit: 3 });
            console.log('Raw project recommendations API response:', projectData);
            
            let projects = Array.isArray(projectData) ? projectData : (projectData as any)?.items || [];
            
            // Handle nested project structure from backend API
            if (projects.length > 0) {
              projects = projects.map((proj: any) => ({
                id: proj.project_id || proj.id || proj._id || 'unknown',
                title: proj.project_details?.title || proj.title || 'Project Title Not Available',
                client: proj.project_details?.company || proj.project_details?.client || proj.company || proj.client || 'Client Not Specified',
                budget: proj.project_details?.budget_range || proj.project_details?.budget || proj.budget_range || proj.budget || 'Budget TBD',
                duration: proj.project_details?.duration || proj.duration || 'Duration TBD',
                status: proj.project_details?.status || proj.status || 'Open',
                match_score: proj.match_score || proj.score || 0,
                skills_required: proj.project_details?.skills_required || proj.skills_required || []
              }));
            }
            
            if (projects.length > 0 && projects[0].title && projects[0].title !== 'Project Title Not Available' && projects[0].match_score > 0) {
              console.log('Using actual project recommendations with real match scores');
              setProjectRecommendations(projects);
            } else {
              throw new Error('Invalid recommendation data');
            }
          } catch (recError) {
            console.log('Project recommendations API failed, trying public projects with basic matching:', recError);
            
            // Fallback: Use public projects API but calculate basic match scores
            const projectData = await projectsApi.getProjectsPublic();
            let projects = Array.isArray(projectData) ? projectData.slice(0, 3) : [];
            
            if (projects.length > 0) {
              // Get candidate skills for matching
              let candidateSkills: string[] = [];
              try {
                if (user?.skills) {
                  const userSkills = user.skills;
                  if (Array.isArray(userSkills)) {
                    candidateSkills = userSkills.map((skill: any) => 
                      typeof skill === 'string' ? skill : skill.name || skill.skill || ''
                    ).filter(Boolean);
                  } else if (typeof userSkills === 'object') {
                    candidateSkills = [
                      ...(userSkills.languages_frameworks || []),
                      ...(userSkills.ai_ml_data || []),
                      ...(userSkills.tools_platforms || []),
                      ...(userSkills.soft_skills || []),
                      ...(userSkills.technical || []),
                      ...(userSkills.programming || [])
                    ].filter(Boolean);
                  }
                }
              } catch (err) {
                console.log('Could not fetch candidate skills for matching:', err);
              }
              
              // Calculate match scores based on skills
              projects = projects.map((proj: any) => {
                const projectSkills = proj.skills_required || [];
                let matchScore = 75;
                
                if (candidateSkills.length > 0 && projectSkills.length > 0) {
                  // Find exact matches
                  const exactMatches = projectSkills.filter((skill: string) => 
                    candidateSkills.some(candidateSkill => 
                      candidateSkill.toLowerCase() === skill.toLowerCase()
                    )
                  );
                  
                  // Find partial matches
                  const partialMatches = projectSkills.filter((skill: string) => 
                    !exactMatches.includes(skill) && candidateSkills.some(candidateSkill => 
                      candidateSkill.toLowerCase().includes(skill.toLowerCase()) || 
                      skill.toLowerCase().includes(candidateSkill.toLowerCase()) ||
                      (skill.toLowerCase().includes('react') && candidateSkill.toLowerCase().includes('javascript')) ||
                      (skill.toLowerCase().includes('node') && candidateSkill.toLowerCase().includes('javascript')) ||
                      (skill.toLowerCase().includes('python') && candidateSkill.toLowerCase().includes('django')) ||
                      (skill.toLowerCase().includes('python') && candidateSkill.toLowerCase().includes('flask'))
                    )
                  );
                  
                  // Calculate score
                  const exactMatchWeight = 1.0;
                  const partialMatchWeight = 0.6;
                  const totalScore = (exactMatches.length * exactMatchWeight) + (partialMatches.length * partialMatchWeight);
                  const maxPossibleScore = projectSkills.length * exactMatchWeight;
                  const skillMatchPercentage = Math.min(100, (totalScore / maxPossibleScore) * 100);
                  
                  const baseScore = 65;
                  const skillContribution = (skillMatchPercentage / 100) * 25;
                  const randomVariation = (Math.random() - 0.5) * 6;
                  matchScore = Math.max(60, Math.min(95, baseScore + skillContribution + randomVariation));
                } else if (candidateSkills.length > 0) {
                  matchScore = 78 + (Math.random() - 0.5) * 12;
                } else {
                  const projectComplexity = projectSkills.length;
                  const baseVariation = Math.random() * 16 - 8;
                  matchScore = Math.max(65, Math.min(88, 74 + baseVariation + (projectComplexity * 1.5)));
                }
                
                return {
                  id: proj.id || proj._id || 'unknown',
                  title: proj.title || 'Project Title Not Available',
                  client: proj.company || proj.client || 'Client Not Specified',
                  budget: proj.budget_range || proj.budget || 'Budget TBD',
                  duration: proj.duration || 'Duration TBD',
                  status: proj.status || 'Open',
                  match_score: Math.round(matchScore * 100) / 100,
                  skills_required: projectSkills
                };
              });
            }
            
            if (projects.length > 0 && projects[0].title && projects[0].title !== 'Project Title Not Available') {
              setProjectRecommendations(projects);
            } else {
              const mockProjects = getMockProjectRecommendations();
              setProjectRecommendations(mockProjects);
            }
          }
        } catch (err) {
          console.log('All project APIs failed:', err);
          const mockProjects = getMockProjectRecommendations();
          setProjectRecommendations(mockProjects);
        }
      } else {
        // For employers, set empty recommendations
        setRecommendations([]);
        setProjectRecommendations([]);
      }
      
      // Fetch dashboard statistics
      const realStats = { ...stats };
      
      try {
        if (user?.user_type === 'employer') {
          const jobs = await jobsApi.getJobs(token!);
          realStats.job_applications = Array.isArray(jobs) ? jobs.length : 0;
        } else {
          const applications = await applicationsApi.getApplications(token!);
          realStats.job_applications = Array.isArray(applications) ? applications.length : 0;
        }
      } catch (err) {
        console.log('Failed to fetch job-related data, using fallback');
      }

      try {
        if (user?.user_type === 'employer') {
          realStats.saved_jobs = 0;
        } else {
          const savedJobs = await savedJobsApi.getSavedJobs(token!);
          realStats.saved_jobs = Array.isArray(savedJobs) ? savedJobs.length : 0;
        }
      } catch (err) {
        console.log('Failed to fetch saved jobs data, using fallback');
      }

      if (user?.user_type !== 'employer') {
        try {
          const allRecs = await enhancedRecommendationsApi.getJobRecommendations(token!, { min_match_score: 70 });
          const matches = Array.isArray(allRecs) ? allRecs : (allRecs as any)?.items || [];
          realStats.recommendation_matches = matches.length;
        } catch (err) {
          console.log('Failed to fetch recommendation matches, using fallback');
        }
      } else {
        realStats.recommendation_matches = 0;
      }

      try {
        const analyticsData = await candidateAnalyticsApi.getProfileAnalytics(token!);
        if (analyticsData) {
          if (analyticsData.profile_completion !== undefined) {
            realStats.profile_completion = analyticsData.profile_completion;
          }
          if (analyticsData.profile_views !== undefined) {
            realStats.profile_views = analyticsData.profile_views;
          }
          if (analyticsData.job_applications !== undefined) {
            realStats.job_applications = analyticsData.job_applications;
          }
          if (analyticsData.saved_jobs !== undefined) {
            realStats.saved_jobs = analyticsData.saved_jobs;
          }
          if (analyticsData.recommendation_matches !== undefined) {
            realStats.recommendation_matches = analyticsData.recommendation_matches;
          }
        }
      } catch (err) {
        console.log('Analytics not available, using computed stats');
      }

      setStats(realStats);
      setRecentActivity(getMockActivity());
      
    } finally {
      setLoading(false);
    }
  };

  const getMockRecommendations = () => [
    {
      id: 'rec-1',
      title: 'Learning Technology Specialist',
      company: 'EdTech Solutions',
      match_score: 88.75,
      location: 'Austin, TX',
      salary_range: '$75,000 - $95,000'
    },
    {
      id: 'rec-2',
      title: 'Instructional Designer',
      company: 'Digital Learning Co',
      match_score: 82.33,
      location: 'Remote',
      salary_range: '$65,000 - $85,000'
    },
    {
      id: 'rec-3',
      title: 'Training Program Manager',
      company: 'Global Corp',
      match_score: 79.89,
      location: 'New York, NY',
      salary_range: '$85,000 - $110,000'
    }
  ];

  const getMockProjectRecommendations = () => [
    {
      id: 'proj-1',
      title: 'E-Learning Platform Development',
      client: 'EduTech Startup',
      match_score: 85.67,
      budget: '$5,000 - $8,000',
      duration: '3 months',
      status: 'Open',
      skills_required: ['React', 'Node.js', 'LMS', 'UI/UX']
    },
    {
      id: 'proj-2',
      title: 'Corporate Training Module Design',
      client: 'Fortune 500 Company',
      match_score: 78.42,
      budget: '$3,000 - $5,000',
      duration: '6 weeks',
      status: 'Urgent',
      skills_required: ['Instructional Design', 'Adobe Creative', 'SCORM']
    },
    {
      id: 'proj-3',
      title: 'Learning Analytics Dashboard',
      client: 'University Research Lab',
      match_score: 81.95,
      budget: '$4,000 - $7,000',
      duration: '2 months',
      status: 'Open',
      skills_required: ['Data Visualization', 'Python', 'Tableau', 'Learning Analytics']
    }
  ];

  const getMockActivity = (): RecentActivity[] => [
    {
      type: 'recommendation',
      title: 'New Job Recommendations',
      description: '3 new job matches found based on your profile',
      timestamp: '2 hours ago',
      link: '/candidate-recommendations'
    },
    {
      type: 'job_view',
      title: 'Profile Viewed',
      description: 'TechCorp Inc. viewed your profile',
      timestamp: '1 day ago'
    },
    {
      type: 'application',
      title: 'Application Sent',
      description: 'Applied to Senior Learning Designer at Global Corp',
      timestamp: '2 days ago'
    }
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'job_view': return <Eye className="h-4 w-4 text-blue-600" />;
      case 'application': return <Briefcase className="h-4 w-4 text-green-600" />;
      case 'profile_update': return <User className="h-4 w-4 text-purple-600" />;
      case 'recommendation': return <Star className="h-4 w-4 text-yellow-600" />;
      default: return <Bell className="h-4 w-4 text-gray-600" />;
    }
  };

  const formatSalaryRange = (salaryRange: any): string => {
    if (!salaryRange) return '';
    
    if (typeof salaryRange === 'string') {
      return salaryRange;
    }
    
    if (typeof salaryRange === 'object' && salaryRange.min !== undefined && salaryRange.max !== undefined) {
      const currency = salaryRange.currency || '$';
      return `${currency}${salaryRange.min} - ${currency}${salaryRange.max}`;
    }
    
    return String(salaryRange);
  };

  const roundToTwo = (num: number): number => {
    return Math.round((num + Number.EPSILON) * 100) / 100;
  };

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please log in to access your dashboard</h1>
          <Button asChild>
            <Link href="/login">Log In</Link>
          </Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user.full_name?.split(' ')[0] || 'Candidate'}!
            </h1>
            <p className="text-gray-600 mt-2">
              Here's your career development overview
            </p>
          </div>
          <Button onClick={logout} variant="outline">
            Logout
          </Button>
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          {(() => {
            const statsConfig = user?.user_type === 'employer' ? [
              {
                id: 'profile',
                icon: User,
                label: 'Profile',
                value: `${roundToTwo(stats.profile_completion)}%`,
                bgColor: 'bg-blue-100',
                textColor: 'text-blue-600',
                showProgress: true,
                progressValue: stats.profile_completion
              },
              {
                id: 'posted-jobs',
                icon: Briefcase,
                label: 'Posted Jobs',
                value: stats.job_applications,
                bgColor: 'bg-green-100',
                textColor: 'text-green-600'
              },
              {
                id: 'candidates-viewed',
                icon: Eye,
                label: 'Candidates Viewed',
                value: stats.profile_views,
                bgColor: 'bg-purple-100',
                textColor: 'text-purple-600'
              },
              {
                id: 'shortlisted',
                icon: Heart,
                label: 'Shortlisted',
                value: stats.saved_jobs,
                bgColor: 'bg-yellow-100',
                textColor: 'text-yellow-600'
              },
              {
                id: 'matches',
                icon: Star,
                label: 'Top Matches',
                value: stats.recommendation_matches,
                bgColor: 'bg-indigo-100',
                textColor: 'text-indigo-600'
              }
            ] : [
              {
                id: 'profile',
                icon: User,
                label: 'Profile',
                value: `${roundToTwo(stats.profile_completion)}%`,
                bgColor: 'bg-blue-100',
                textColor: 'text-blue-600',
                showProgress: true,
                progressValue: stats.profile_completion
              },
              {
                id: 'applications',
                icon: Briefcase,
                label: 'Applications',
                value: stats.job_applications,
                bgColor: 'bg-green-100',
                textColor: 'text-green-600'
              },
              {
                id: 'views',
                icon: Eye,
                label: 'Profile Views',
                value: stats.profile_views,
                bgColor: 'bg-purple-100',
                textColor: 'text-purple-600'
              },
              {
                id: 'saved',
                icon: Heart,
                label: 'Saved Jobs',
                value: stats.saved_jobs,
                bgColor: 'bg-yellow-100',
                textColor: 'text-yellow-600'
              },
              {
                id: 'matches',
                icon: Star,
                label: 'Matches',
                value: stats.recommendation_matches,
                bgColor: 'bg-indigo-100',
                textColor: 'text-indigo-600'
              }
            ];

            return statsConfig.map((stat) => (
              <Card key={stat.id}>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className={`p-2 ${stat.bgColor} rounded-lg`}>
                      <stat.icon className={`h-6 w-6 ${stat.textColor}`} />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                      <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                    </div>
                  </div>
                  {stat.showProgress && (
                    <Progress value={stat.progressValue} className="mt-3" />
                  )}
                </CardContent>
              </Card>
            ));
          })()}
        </div>
      
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {(() => {
                    const actionsConfig = user?.user_type === 'employer' ? [
                      {
                        id: 'candidate-recommendations',
                        href: '/employer-candidates',
                        icon: Users,
                        label: 'Find Candidates'
                      },
                      {
                        id: 'post-job',
                        href: '/jobs/create',
                        icon: Plus,
                        label: 'Post Job'
                      },
                      {
                        id: 'analytics',
                        href: '/employer-analytics',
                        icon: BarChart3,
                        label: 'Analytics'
                      },
                      {
                        id: 'edit-profile',
                        href: '/employer-profile',
                        icon: User,
                        label: 'Edit Profile'
                      }
                    ] : [
                      {
                        id: 'job-search',
                        href: '/jobs',
                        icon: Search,
                        label: 'Search Jobs'
                      },
                      {
                        id: 'skill-analysis',
                        href: '/skill-gap-analysis',
                        icon: BarChart3,
                        label: 'Skill Analysis'
                      },
                      {
                        id: 'career-paths',
                        href: '/career-paths',
                        icon: TrendingUp,
                        label: 'Career Paths'
                      },
                      {
                        id: 'edit-profile',
                        href: '/candidate-profile',
                        icon: User,
                        label: 'Edit Profile'
                      }
                    ];

                    return actionsConfig.map((action) => (
                      <Button key={action.id} asChild variant="outline" className="h-auto p-4 flex flex-col gap-2">
                        <Link href={action.href}>
                          <action.icon className="h-6 w-6" />
                          <span className="text-sm">{action.label}</span>
                        </Link>
                      </Button>
                    ));
                  })()}
                </div>
              </CardContent>
            </Card>

            {/* Job Recommendations - Only show for candidates */}
            {user?.user_type !== 'employer' && (
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle className="flex items-center gap-2">
                      <Star className="h-5 w-5" />
                      Recommended for You
                    </CardTitle>
                    <Button asChild variant="outline" size="sm">
                      <Link href="/candidate-recommendations">
                        View All <ChevronRight className="h-4 w-4 ml-1" />
                      </Link>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {(recommendations || []).map((job, index) => (
                      <div key={`rec-${job.id || `idx-${index}`}`} className="flex justify-between items-center p-4 border rounded-lg hover:bg-gray-50">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{job.title || 'No Title Available'}</h3>
                          <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                            <span className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              {job.company || 'Unknown Company'}
                            </span>
                            <span>{job.location || 'Location TBD'}</span>
                            {job.salary_range && (
                              <span className="flex items-center gap-1">
                                <DollarSign className="h-3 w-3" />
                                {formatSalaryRange(job.salary_range)}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge variant="secondary" className="bg-green-100 text-green-800">
                            {roundToTwo(job.match_score || 0)}% Match
                          </Badge>
                          {job.id && job.id !== 'unknown' ? (
                            <Button size="sm" asChild>
                              <Link href={`/jobs/${job.id}`}>View</Link>
                            </Button>
                          ) : (
                            <Button 
                              size="sm" 
                              variant="outline"
                              asChild
                            >
                              <Link href="/candidate-recommendations">Browse Jobs</Link>
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Project Recommendations - Only show for candidates */}
            {user?.user_type !== 'employer' && (
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle className="flex items-center gap-2">
                      <Code className="h-5 w-5" />
                      Recommended Projects
                    </CardTitle>
                    <Button asChild variant="outline" size="sm">
                      <Link href="/project-recommendations">
                        View All <ChevronRight className="h-4 w-4 ml-1" />
                      </Link>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {(projectRecommendations || []).map((project, index) => (
                      <div key={`proj-${project.id || `idx-${index}`}`} className="flex justify-between items-center p-4 border rounded-lg hover:bg-gray-50">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{project.title || 'Project Title Not Available'}</h3>
                          <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                            <span className="flex items-center gap-1">
                              <FolderOpen className="h-3 w-3" />
                              {project.client || 'Client Not Specified'}
                            </span>
                            {project.budget && project.budget !== 'Budget TBD' && (
                              <span className="flex items-center gap-1">
                                <DollarSign className="h-3 w-3" />
                                {project.budget}
                              </span>
                            )}
                            {project.duration && project.duration !== 'Duration TBD' && (
                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {project.duration}
                              </span>
                            )}
                          </div>
                          {project.skills_required && Array.isArray(project.skills_required) && project.skills_required.length > 0 && (
                            <div className="flex items-center gap-2 mt-2">
                              <span className="text-xs text-gray-500">Skills:</span>
                              <div className="flex flex-wrap gap-1">
                                {project.skills_required.slice(0, 3).map((skill: string, skillIndex: number) => (
                                  <Badge key={skillIndex} variant="outline" className="text-xs py-0 px-1">
                                    {skill}
                                  </Badge>
                                ))}
                                {project.skills_required.length > 3 && (
                                  <Badge variant="outline" className="text-xs py-0 px-1">
                                    +{project.skills_required.length - 3} more
                                  </Badge>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                        <div className="flex items-center gap-3">
                          {project.status && project.status !== 'Open' && (
                            <Badge 
                              variant={project.status === 'Urgent' ? 'destructive' : 'secondary'} 
                              className="text-xs"
                            >
                              {project.status}
                            </Badge>
                          )}
                          <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                            {roundToTwo(project.match_score || 0)}% Match
                          </Badge>
                          <Button size="sm" asChild>
                            <Link href={`/projects/${project.id || 'unknown'}`}>View</Link>
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Profile Completion */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Complete Your Profile</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Profile Completion</span>
                    <span className="text-sm font-semibold">{roundToTwo(stats.profile_completion)}%</span>
                  </div>
                  <Progress value={stats.profile_completion} />
                  
                  {stats.profile_completion < 100 && (
                    <div className="space-y-2">
                      <p className="text-sm text-gray-600">Add these to improve your profile:</p>
                      <ul className="text-sm space-y-1">
                        {[
                          { id: 'experience', text: 'Work experience details' },
                          { id: 'skills', text: 'Skill proficiency levels' },
                          { id: 'goals', text: 'Career goals' }
                        ].map((item) => (
                          <li key={item.id} className="flex items-center gap-2">
                            <Plus className="h-3 w-3 text-gray-400" />
                            {item.text}
                          </li>
                        ))}
                      </ul>
                      <Button asChild size="sm" className="w-full mt-3">
                        <Link href={user?.user_type === 'employer' ? '/employer-profile' : '/candidate-profile'}>Complete Profile</Link>
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {(recentActivity || []).map((activity, index) => (
                    <div key={`activity-${activity.type}-${index}-${activity.timestamp.replace(/\s+/g, '')}`} className="flex gap-3">
                      <div className="flex-shrink-0 mt-1">
                        {getActivityIcon(activity.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">
                          {activity.title}
                        </p>
                        <p className="text-sm text-gray-600">{activity.description}</p>
                        <p className="text-xs text-gray-500 mt-1">{activity.timestamp}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Career Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Award className="h-5 w-5" />
                  Career Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    {
                      id: 'skill-trend',
                      type: 'skill',
                      bgColor: 'bg-blue-50',
                      titleColor: 'text-blue-900',
                      textColor: 'text-blue-700',
                      title: 'Skill Trend Alert',
                      content: 'Learning Analytics skills are in high demand (↑23%)'
                    },
                    {
                      id: 'market-opportunity',
                      type: 'market',
                      bgColor: 'bg-green-50',
                      titleColor: 'text-green-900',
                      textColor: 'text-green-700',
                      title: 'Market Opportunity',
                      content: '5 new L&D positions match your profile this week'
                    }
                  ].map((insight) => (
                    <div key={insight.id} className={`p-3 ${insight.bgColor} rounded-lg`}>
                      <p className={`text-sm font-medium ${insight.titleColor}`}>{insight.title}</p>
                      <p className={`text-sm ${insight.textColor} mt-1`}>
                        {insight.content}
                      </p>
                    </div>
                  ))}
                  
                  <Button asChild variant="outline" size="sm" className="w-full">
                    <Link href="/career-paths">
                      Explore Career Paths <ChevronRight className="h-4 w-4 ml-1" />
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
} 