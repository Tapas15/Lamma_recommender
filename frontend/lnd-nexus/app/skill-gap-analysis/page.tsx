'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { enhancedRecommendationsApi, jobsApi } from '../services/api';
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
import { Progress } from '../components/ui/progress';
import { 
  Target, 
  TrendingUp, 
  BookOpen, 
  CheckCircle, 
  AlertCircle,
  Star,
  Clock,
  Award,
  BarChart3,
  Brain,
  Lightbulb
} from 'lucide-react';

interface SkillGapAnalysis {
  target_role: string;
  target_job_id?: string;
  overall_match_percentage: number;
  matching_skills: string[];
  missing_skills: string[];
  partially_matching_skills: Array<{
    skill: string;
    current_level: string;
    required_level: string;
    gap_score: number;
  }>;
  recommended_learning: Array<{
    skill: string;
    priority: 'high' | 'medium' | 'low';
    estimated_time: string;
    learning_resources: Array<{
      type: string;
      title: string;
      url?: string;
      duration?: string;
    }>;
  }>;
  salary_impact: {
    current_estimate: string;
    potential_increase: string;
    percentage_increase: number;
  };
}

interface Job {
  id: string;
  title: string;
  company: string;
  required_skills: string[];
}

export default function SkillGapAnalysisPage() {
  const { user, token } = useAuth();
  const [analysis, setAnalysis] = useState<SkillGapAnalysis | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form inputs
  const [selectedJobId, setSelectedJobId] = useState<string>('');
  const [targetRole, setTargetRole] = useState<string>('');
  const [analysisType, setAnalysisType] = useState<'job' | 'role'>('role');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    if (!token) return;
    
    try {
      const data = await jobsApi.getJobs(token);
      const jobsList = Array.isArray(data) ? data : (data as any)?.items || [];
      setJobs(jobsList.slice(0, 20)); // Limit to first 20 jobs
    } catch (err) {
      console.error('Failed to load jobs:', err);
      // Set mock jobs for demo
      setJobs([
        {
          id: '1',
          title: 'Senior Learning Experience Designer',
          company: 'TechCorp Inc.',
          required_skills: ['Instructional Design', 'LMS', 'Content Development', 'Project Management']
        },
        {
          id: '2',
          title: 'Corporate Training Manager',
          company: 'Global Learning Corp',
          required_skills: ['Training', 'Leadership', 'Curriculum Design', 'Analytics']
        }
      ]);
    }
  };

  const performAnalysis = async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      setError(null);
      
      let data;
      if (analysisType === 'job' && selectedJobId) {
        data = await enhancedRecommendationsApi.getSkillGapAnalysis(token, selectedJobId);
      } else if (analysisType === 'role' && targetRole) {
        data = await enhancedRecommendationsApi.getSkillGapAnalysis(token, undefined, targetRole);
      } else {
        setError('Please select a job or enter a target role');
        return;
      }
      
      setAnalysis(data);
    } catch (err) {
      setError('Failed to perform skill gap analysis');
      // Set mock data for demo
      setAnalysis(getMockAnalysis());
    } finally {
      setLoading(false);
    }
  };

  const getMockAnalysis = (): SkillGapAnalysis => ({
    target_role: targetRole || jobs.find(j => j.id === selectedJobId)?.title || 'Learning Experience Designer',
    target_job_id: selectedJobId,
    overall_match_percentage: 75,
    matching_skills: ['Project Management', 'Communication', 'Problem Solving'],
    missing_skills: ['Articulate Storyline', 'Learning Analytics', 'Instructional Video Production'],
    partially_matching_skills: [
      {
        skill: 'Instructional Design',
        current_level: 'intermediate',
        required_level: 'advanced',
        gap_score: 25
      },
      {
        skill: 'LMS Administration',
        current_level: 'beginner',
        required_level: 'intermediate',
        gap_score: 40
      }
    ],
    recommended_learning: [
      {
        skill: 'Articulate Storyline',
        priority: 'high',
        estimated_time: '4-6 weeks',
        learning_resources: [
          {
            type: 'course',
            title: 'Articulate Storyline Masterclass',
            url: 'https://example.com',
            duration: '20 hours'
          },
          {
            type: 'certification',
            title: 'Articulate Certified Professional',
            duration: '3 months'
          }
        ]
      },
      {
        skill: 'Learning Analytics',
        priority: 'medium',
        estimated_time: '3-4 weeks',
        learning_resources: [
          {
            type: 'course',
            title: 'Data-Driven Learning Design',
            duration: '15 hours'
          }
        ]
      }
    ],
    salary_impact: {
      current_estimate: '$85,000',
      potential_increase: '$15,000',
      percentage_increase: 18
    }
  });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSkillLevelColor = (level: string) => {
    switch (level) {
      case 'expert': return 'text-purple-600';
      case 'advanced': return 'text-blue-600';
      case 'intermediate': return 'text-yellow-600';
      case 'beginner': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Skill Gap Analysis</h1>
          <p className="text-lg text-gray-600">
            Identify skill gaps and get personalized learning recommendations to advance your career.
          </p>
        </div>

        {/* Analysis Setup */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Analysis Setup
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4 mb-4">
              <Button
                variant={analysisType === 'role' ? 'default' : 'outline'}
                onClick={() => setAnalysisType('role')}
              >
                Analyze by Role
              </Button>
              <Button
                variant={analysisType === 'job' ? 'default' : 'outline'}
                onClick={() => setAnalysisType('job')}
              >
                Analyze by Job Posting
              </Button>
            </div>
            
            {analysisType === 'role' ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Role
                </label>
                <Input
                  placeholder="e.g., Senior Learning Experience Designer"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                />
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Job Posting
                </label>
                <Select value={selectedJobId} onValueChange={setSelectedJobId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a job posting" />
                  </SelectTrigger>
                  <SelectContent>
                    {jobs.map((job) => (
                      <SelectItem key={job.id} value={job.id}>
                        {job.title} - {job.company}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            
            <Button 
              onClick={performAnalysis} 
              disabled={loading || (analysisType === 'role' ? !targetRole : !selectedJobId)}
              className="flex items-center gap-2"
            >
              <BarChart3 className="h-4 w-4" />
              {loading ? 'Analyzing...' : 'Perform Analysis'}
            </Button>
          </CardContent>
        </Card>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Analysis Results */}
        {analysis && (
          <div className="space-y-6">
            {/* Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Analysis Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {analysis.overall_match_percentage}%
                    </div>
                    <p className="text-gray-600">Overall Match</p>
                    <Progress value={analysis.overall_match_percentage} className="mt-2" />
                  </div>
                  
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600 mb-2">
                      {(analysis.matching_skills || []).length}
                    </div>
                    <p className="text-gray-600">Matching Skills</p>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-3xl font-bold text-red-600 mb-2">
                      {(analysis.missing_skills || []).length}
                    </div>
                    <p className="text-gray-600">Missing Skills</p>
                  </div>
                </div>
                
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2">Target Role: {analysis.target_role}</h3>
                  <p className="text-gray-600">
                    Based on this analysis, you're a {analysis.overall_match_percentage}% match for this role. 
                    Focus on the missing skills and improving partially matching skills to increase your qualification.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Skills Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Matching Skills */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-600">
                    <CheckCircle className="h-5 w-5" />
                    Matching Skills ({(analysis.matching_skills || []).length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {(analysis.matching_skills || []).map((skill, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-green-50 rounded">
                        <span className="font-medium text-green-800">{skill}</span>
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Missing Skills */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-red-600">
                    <AlertCircle className="h-5 w-5" />
                    Missing Skills ({(analysis.missing_skills || []).length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {(analysis.missing_skills || []).map((skill, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-red-50 rounded">
                        <span className="font-medium text-red-800">{skill}</span>
                        <AlertCircle className="h-4 w-4 text-red-600" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Partially Matching Skills */}
            {(analysis.partially_matching_skills || []).length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-yellow-600">
                    <TrendingUp className="h-5 w-5" />
                    Skills to Improve ({(analysis.partially_matching_skills || []).length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {(analysis.partially_matching_skills || []).map((skill, index) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="font-semibold">{skill.skill}</h4>
                          <span className="text-sm text-gray-500">{100 - skill.gap_score}% Match</span>
                        </div>
                        <div className="flex justify-between text-sm mb-2">
                          <span className={`font-medium ${getSkillLevelColor(skill.current_level)}`}>
                            Current: {skill.current_level}
                          </span>
                          <span className={`font-medium ${getSkillLevelColor(skill.required_level)}`}>
                            Required: {skill.required_level}
                          </span>
                        </div>
                        <Progress value={100 - skill.gap_score} className="h-2" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Learning Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5" />
                  Learning Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {(analysis.recommended_learning || []).map((learning, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex justify-between items-center mb-3">
                        <h4 className="font-semibold text-lg">{learning.skill}</h4>
                        <div className="flex gap-2">
                          <Badge className={getPriorityColor(learning.priority)}>
                            {learning.priority} priority
                          </Badge>
                          <Badge variant="outline" className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {learning.estimated_time}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        {(learning.learning_resources || []).map((resource, resourceIndex) => (
                          <div key={resourceIndex} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <div className="flex items-center gap-2">
                              <BookOpen className="h-4 w-4 text-blue-600" />
                              <span className="font-medium">{resource.title}</span>
                              <Badge variant="outline" className="text-xs">
                                {resource.type}
                              </Badge>
                            </div>
                            {resource.duration && (
                              <span className="text-sm text-gray-500">{resource.duration}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Salary Impact */}
            {analysis.salary_impact && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5" />
                    Potential Career Impact
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900 mb-1">
                        {analysis.salary_impact.current_estimate}
                      </div>
                      <p className="text-gray-600">Current Estimated Salary</p>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600 mb-1">
                        +{analysis.salary_impact.potential_increase}
                      </div>
                      <p className="text-gray-600">Potential Increase</p>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600 mb-1">
                        +{analysis.salary_impact.percentage_increase}%
                      </div>
                      <p className="text-gray-600">Percentage Increase</p>
                    </div>
                  </div>
                  
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <p className="text-blue-800">
                      By addressing the identified skill gaps, you could potentially increase your earning 
                      potential by {analysis.salary_impact.percentage_increase}% and become more competitive 
                      for {analysis.target_role} positions.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 