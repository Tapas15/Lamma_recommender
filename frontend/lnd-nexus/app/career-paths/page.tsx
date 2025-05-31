'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../contexts/AuthContext';
import { enhancedCareerPathsApi } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { 
  TrendingUp, 
  MapPin, 
  Clock, 
  DollarSign,
  Award,
  ChevronRight,
  Target,
  BookOpen,
  Users,
  BarChart3,
  Briefcase,
  Star,
  ArrowRight,
  Building
} from 'lucide-react';

interface CareerStep {
  title: string;
  level: string;
  experience_required: string;
  skills_required: string[];
  skills_to_develop: string[];
  average_salary: string;
  growth_rate: string;
  companies: string[];
  estimated_timeframe: string;
}

interface CareerPath {
  id: string;
  title: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  current_match_percentage: number;
  steps: CareerStep[];
  total_duration: string;
  salary_progression: {
    entry: string;
    mid: string;
    senior: string;
    expert: string;
  };
  key_skills: string[];
  growth_outlook: 'excellent' | 'good' | 'average';
  remote_friendly: boolean;
}

export default function CareerPathsPage() {
  const { user, token } = useAuth();
  const [careerPaths, setCareerPaths] = useState<CareerPath[]>([]);
  const [filteredPaths, setFilteredPaths] = useState<CareerPath[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentRole, setCurrentRole] = useState('');
  const [selectedPath, setSelectedPath] = useState<CareerPath | null>(null);
  
  // Filters
  const [difficultyFilter, setDifficultyFilter] = useState<string>('');
  const [remoteFilter, setRemoteFilter] = useState<boolean | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchCareerPaths();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [careerPaths, difficultyFilter, remoteFilter, searchTerm]);

  const fetchCareerPaths = async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      const data = await enhancedCareerPathsApi.getCareerPaths(token, currentRole);
      const paths = Array.isArray(data) ? data : [];
      setCareerPaths(paths);
    } catch (err) {
      setError('Failed to load career paths');
      // Set mock data for demo
      setCareerPaths(getMockCareerPaths());
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...careerPaths];

    if (searchTerm) {
      filtered = filtered.filter(path => 
        path.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        path.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        path.key_skills.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    if (difficultyFilter) {
      filtered = filtered.filter(path => path.difficulty === difficultyFilter);
    }

    if (remoteFilter !== null) {
      filtered = filtered.filter(path => path.remote_friendly === remoteFilter);
    }

    setFilteredPaths(filtered);
  };

  const getMockCareerPaths = (): CareerPath[] => [
    {
      id: '1',
      title: 'Learning Experience Designer Career Path',
      description: 'Progress from entry-level instructional designer to senior learning strategist',
      difficulty: 'medium',
      current_match_percentage: 75,
      total_duration: '5-7 years',
      remote_friendly: true,
      growth_outlook: 'excellent',
      key_skills: ['Instructional Design', 'UX Design', 'Learning Technologies', 'Data Analysis'],
      salary_progression: {
        entry: '$55,000',
        mid: '$75,000',
        senior: '$95,000',
        expert: '$120,000'
      },
      steps: [
        {
          title: 'Instructional Designer',
          level: 'Entry',
          experience_required: '0-2 years',
          skills_required: ['Basic Instructional Design', 'Content Creation', 'Communication'],
          skills_to_develop: ['Advanced ID Models', 'E-learning Development', 'LMS'],
          average_salary: '$55,000',
          growth_rate: '8%',
          companies: ['Corporate Training Cos', 'EdTech Startups', 'Universities'],
          estimated_timeframe: '1-2 years'
        },
        {
          title: 'Senior Instructional Designer',
          level: 'Mid',
          experience_required: '2-4 years',
          skills_required: ['Advanced ID', 'E-learning Tools', 'Project Management'],
          skills_to_develop: ['UX Design', 'Learning Analytics', 'Strategic Thinking'],
          average_salary: '$75,000',
          growth_rate: '10%',
          companies: ['Enterprise Companies', 'Consulting Firms', 'Tech Companies'],
          estimated_timeframe: '2-3 years'
        },
        {
          title: 'Learning Experience Designer',
          level: 'Senior',
          experience_required: '4-6 years',
          skills_required: ['UX/UI Design', 'Learning Science', 'Data Analysis'],
          skills_to_develop: ['Leadership', 'Strategic Planning', 'Innovation'],
          average_salary: '$95,000',
          growth_rate: '12%',
          companies: ['Fortune 500', 'Design Agencies', 'Learning Platforms'],
          estimated_timeframe: '2-3 years'
        },
        {
          title: 'Chief Learning Officer',
          level: 'Expert',
          experience_required: '6+ years',
          skills_required: ['Strategic Leadership', 'Business Acumen', 'Innovation'],
          skills_to_develop: ['Executive Presence', 'Change Management'],
          average_salary: '$120,000+',
          growth_rate: '15%',
          companies: ['Fortune 500', 'Consulting Firms', 'Global Enterprises'],
          estimated_timeframe: 'Ongoing'
        }
      ]
    },
    {
      id: '2',
      title: 'Learning Technology Specialist Path',
      description: 'Specialize in learning technologies and become a technical leader',
      difficulty: 'hard',
      current_match_percentage: 60,
      total_duration: '4-6 years',
      remote_friendly: true,
      growth_outlook: 'excellent',
      key_skills: ['Technical Skills', 'LMS Administration', 'Programming', 'Integration'],
      salary_progression: {
        entry: '$60,000',
        mid: '$80,000',
        senior: '$105,000',
        expert: '$130,000'
      },
      steps: [
        {
          title: 'LMS Administrator',
          level: 'Entry',
          experience_required: '0-2 years',
          skills_required: ['LMS Basics', 'Technical Support', 'User Training'],
          skills_to_develop: ['Advanced LMS', 'APIs', 'Data Management'],
          average_salary: '$60,000',
          growth_rate: '9%',
          companies: ['EdTech Companies', 'Corporations', 'Government'],
          estimated_timeframe: '1-2 years'
        },
        {
          title: 'Learning Technology Specialist',
          level: 'Mid',
          experience_required: '2-4 years',
          skills_required: ['Multiple LMS Platforms', 'Integration', 'Programming'],
          skills_to_develop: ['AI/ML', 'Analytics', 'Architecture'],
          average_salary: '$80,000',
          growth_rate: '11%',
          companies: ['Tech Companies', 'Consulting', 'Enterprise'],
          estimated_timeframe: '2-3 years'
        }
      ]
    }
  ];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getGrowthColor = (outlook: string) => {
    switch (outlook) {
      case 'excellent': return 'text-green-600';
      case 'good': return 'text-blue-600';
      case 'average': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[1, 2].map((i) => (
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

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Career Paths</h1>
          <p className="text-lg text-gray-600">
            Explore potential career progression routes tailored to your skills and experience.
          </p>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Input
                placeholder="Search career paths..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              
              <select 
                className="px-3 py-2 border border-gray-300 rounded-md"
                value={difficultyFilter}
                onChange={(e) => setDifficultyFilter(e.target.value)}
              >
                <option value="">All Difficulties</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
              
              <select 
                className="px-3 py-2 border border-gray-300 rounded-md"
                value={remoteFilter === null ? '' : remoteFilter.toString()}
                onChange={(e) => setRemoteFilter(e.target.value === '' ? null : e.target.value === 'true')}
              >
                <option value="">All Work Types</option>
                <option value="true">Remote Friendly</option>
                <option value="false">On-site</option>
              </select>
              
              <Button onClick={fetchCareerPaths} variant="outline">
                Refresh Paths
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Career Paths Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {filteredPaths.map((path) => (
            <Card key={path.id} className="hover:shadow-lg transition-shadow cursor-pointer" 
                  onClick={() => setSelectedPath(path)}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg">{path.title}</CardTitle>
                  <div className="flex gap-2">
                    <Badge className={getDifficultyColor(path.difficulty)}>
                      {path.difficulty}
                    </Badge>
                    {path.remote_friendly && (
                      <Badge variant="outline">Remote</Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">{path.description}</p>
                
                <div className="space-y-3 mb-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Current Match</span>
                    <span className="text-sm font-bold">{path.current_match_percentage}%</span>
                  </div>
                  <Progress value={path.current_match_percentage} className="h-2" />
                </div>
                
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <Clock className="h-4 w-4" />
                    <span>{path.total_duration}</span>
                  </div>
                  <div className="flex items-center gap-1 text-sm">
                    <TrendingUp className={`h-4 w-4 ${getGrowthColor(path.growth_outlook)}`} />
                    <span className={getGrowthColor(path.growth_outlook)}>
                      {path.growth_outlook} growth
                    </span>
                  </div>
                </div>
                
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Salary Range:</h4>
                  <div className="flex justify-between text-sm">
                    <span>{path.salary_progression.entry}</span>
                    <ArrowRight className="h-4 w-4 text-gray-400" />
                    <span className="font-semibold">{path.salary_progression.expert}</span>
                  </div>
                </div>
                
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Key Skills:</h4>
                  <div className="flex flex-wrap gap-1">
                    {path.key_skills.slice(0, 3).map((skill, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                    {path.key_skills.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{path.key_skills.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>
                
                <Button className="w-full" onClick={() => setSelectedPath(path)}>
                  View Career Path <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Detailed Career Path View */}
        {selectedPath && (
          <Card className="mb-8">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-xl">{selectedPath.title}</CardTitle>
                <Button variant="outline" onClick={() => setSelectedPath(null)}>
                  Close
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-6">{selectedPath.description}</p>
              
              {/* Career Steps */}
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Career Progression</h3>
                
                {selectedPath.steps.map((step, index) => (
                  <div key={index} className="relative">
                    {/* Connection Line */}
                    {index < selectedPath.steps.length - 1 && (
                      <div className="absolute left-6 top-12 w-0.5 h-16 bg-gray-300"></div>
                    )}
                    
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-semibold">{index + 1}</span>
                      </div>
                      
                      <div className="flex-1 border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h4 className="font-semibold text-lg">{step.title}</h4>
                            <div className="flex gap-4 text-sm text-gray-600">
                              <span>{step.level} Level</span>
                              <span>{step.experience_required}</span>
                              <span className="flex items-center gap-1">
                                <DollarSign className="h-3 w-3" />
                                {step.average_salary}
                              </span>
                            </div>
                          </div>
                          <Badge variant="outline" className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {step.estimated_timeframe}
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h5 className="font-medium text-sm mb-2 text-green-700">Required Skills</h5>
                            <div className="flex flex-wrap gap-1">
                              {step.skills_required.map((skill, skillIndex) => (
                                <Badge key={skillIndex} variant="outline" className="text-xs bg-green-50">
                                  {skill}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <h5 className="font-medium text-sm mb-2 text-blue-700">Skills to Develop</h5>
                            <div className="flex flex-wrap gap-1">
                              {step.skills_to_develop.map((skill, skillIndex) => (
                                <Badge key={skillIndex} variant="outline" className="text-xs bg-blue-50">
                                  {skill}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                        
                        <div className="mt-3 pt-3 border-t">
                          <div className="flex justify-between items-center text-sm">
                            <div className="flex items-center gap-2 text-gray-600">
                              <TrendingUp className="h-4 w-4" />
                              <span>{step.growth_rate} growth rate</span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-600">
                              <Building className="h-4 w-4" />
                              <span>Top companies: {step.companies.slice(0, 2).join(', ')}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Action Buttons */}
              <div className="flex gap-4 mt-8">
                <Button asChild>
                  <Link href="/skill-gap-analysis">
                    Analyze Skill Gaps
                  </Link>
                </Button>
                <Button variant="outline" asChild>
                  <Link href="/candidate-recommendations">
                    Find Jobs in This Path
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {filteredPaths.length === 0 && !loading && (
          <div className="text-center py-12">
            <Target className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No career paths found</h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your filters or update your profile to get better path recommendations.
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