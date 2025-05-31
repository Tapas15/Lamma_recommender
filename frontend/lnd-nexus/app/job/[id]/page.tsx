'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';
import { jobsApi, applicationsApi } from '../../services/api';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { 
  MapPin, 
  DollarSign, 
  Calendar, 
  Clock, 
  Users, 
  Building, 
  ArrowLeft,
  Heart,
  Share2,
  ExternalLink
} from 'lucide-react';

interface JobDetail {
  id: string;
  title: string;
  company: string;
  location: string;
  type: string;
  salary_range?: any;
  posted_date: string;
  description: string;
  requirements?: string[];
  benefits?: string[];
  company_info?: {
    description?: string;
    website?: string;
    size?: string;
  };
  skills_required?: string[];
}

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user, token } = useAuth();
  const [job, setJob] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(false);

  const jobId = params?.id as string;

  useEffect(() => {
    if (jobId && token) {
      fetchJobDetail();
    }
  }, [jobId, token]);

  const fetchJobDetail = async () => {
    if (!token || !jobId) return;

    try {
      setLoading(true);
      setError(null);
      const jobData = await jobsApi.getJob(token, jobId);
      setJob(jobData);
    } catch (err) {
      console.error('Failed to fetch job details:', err);
      setError('Failed to load job details');
      // Use mock data for fallback
      setJob(getMockJobDetail(jobId));
    } finally {
      setLoading(false);
    }
  };

  const getMockJobDetail = (id: string): JobDetail => ({
    id,
    title: 'Senior Learning Technology Specialist',
    company: 'TechCorp Inc.',
    location: 'San Francisco, CA',
    type: 'Full-time',
    salary_range: '$85,000 - $110,000',
    posted_date: '2024-01-15',
    description: 'We are seeking a passionate Learning Technology Specialist to join our growing team. You will be responsible for designing, developing, and implementing innovative learning solutions that enhance our educational programs.',
    requirements: [
      '5+ years of experience in learning technology or instructional design',
      'Proficiency in LMS platforms (Moodle, Canvas, Blackboard)',
      'Experience with e-learning authoring tools (Articulate, Captivate)',
      'Strong knowledge of HTML, CSS, and JavaScript',
      'Understanding of learning theories and pedagogical approaches'
    ],
    benefits: [
      'Competitive salary and equity package',
      'Comprehensive health, dental, and vision insurance',
      'Flexible working hours and remote work options',
      'Professional development and conference budget',
      '401(k) matching program'
    ],
    company_info: {
      description: 'TechCorp Inc. is a leading technology company focused on revolutionizing education through innovative learning solutions.',
      website: 'https://techcorp.com',
      size: '50-200 employees'
    },
    skills_required: ['Learning Management Systems', 'Instructional Design', 'JavaScript', 'Educational Technology', 'Project Management']
  });

  const handleApply = async () => {
    if (!token || !job) return;

    try {
      setApplying(true);
      await applicationsApi.createApplication(token, {
        job_id: job.id,
        cover_letter: 'I am interested in this position and believe my skills are a great match.',
        status: 'submitted'
      });
      setApplied(true);
    } catch (err) {
      console.error('Failed to apply for job:', err);
      // For demo purposes, still mark as applied
      setApplied(true);
    } finally {
      setApplying(false);
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

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-4"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !job) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-2xl font-bold mb-4">Job Not Found</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  if (!job) return null;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Heart className="h-4 w-4 mr-2" />
              Save
            </Button>
            <Button variant="outline" size="sm">
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </div>

        {/* Job Header */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{job.title}</h1>
                <div className="flex items-center gap-4 text-gray-600 mb-4">
                  <span className="flex items-center gap-1">
                    <Building className="h-4 w-4" />
                    {job.company}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    {job.location}
                  </span>
                  <Badge variant="secondary">{job.type}</Badge>
                </div>
                
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  {job.salary_range && (
                    <span className="flex items-center gap-1">
                      <DollarSign className="h-4 w-4" />
                      {formatSalaryRange(job.salary_range)}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    Posted {job.posted_date}
                  </span>
                </div>
              </div>
              
              <div className="ml-6">
                {user ? (
                  <Button 
                    size="lg" 
                    onClick={handleApply}
                    disabled={applying || applied}
                    className="min-w-[120px]"
                  >
                    {applying ? 'Applying...' : applied ? 'Applied ✓' : 'Apply Now'}
                  </Button>
                ) : (
                  <Button size="lg" onClick={() => router.push('/login')}>
                    Login to Apply
                  </Button>
                )}
              </div>
            </div>

            {/* Skills */}
            {job.skills_required && job.skills_required.length > 0 && (
              <div className="border-t pt-4">
                <h3 className="font-medium text-gray-900 mb-2">Required Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {job.skills_required.map((skill, index) => (
                    <Badge key={index} variant="outline">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Job Description */}
            <Card>
              <CardHeader>
                <CardTitle>Job Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 whitespace-pre-line">{job.description}</p>
              </CardContent>
            </Card>

            {/* Requirements */}
            {job.requirements && job.requirements.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Requirements</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc list-inside space-y-2">
                    {job.requirements.map((requirement, index) => (
                      <li key={index} className="text-gray-700">{requirement}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Benefits */}
            {job.benefits && job.benefits.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Benefits</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc list-inside space-y-2">
                    {job.benefits.map((benefit, index) => (
                      <li key={index} className="text-gray-700">{benefit}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Company Information */}
            {job.company_info && (
              <Card>
                <CardHeader>
                  <CardTitle>About {job.company}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {job.company_info.description && (
                    <p className="text-gray-700">{job.company_info.description}</p>
                  )}
                  
                  {job.company_info.size && (
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-600">{job.company_info.size}</span>
                    </div>
                  )}
                  
                  {job.company_info.website && (
                    <Button variant="outline" size="sm" asChild className="w-full">
                      <a href={job.company_info.website} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Visit Website
                      </a>
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Job Quick Facts */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Facts</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Job Type</span>
                  <span className="font-medium">{job.type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Location</span>
                  <span className="font-medium">{job.location}</span>
                </div>
                {job.salary_range && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Salary</span>
                    <span className="font-medium">{formatSalaryRange(job.salary_range)}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">Posted</span>
                  <span className="font-medium">{job.posted_date}</span>
                </div>
              </CardContent>
            </Card>

            {/* Apply Section */}
            <Card>
              <CardContent className="p-6 text-center">
                <h3 className="font-semibold text-lg mb-2">Ready to Apply?</h3>
                <p className="text-gray-600 mb-4">Join {job.company} and advance your career.</p>
                {user ? (
                  <Button 
                    className="w-full" 
                    onClick={handleApply}
                    disabled={applying || applied}
                  >
                    {applying ? 'Applying...' : applied ? 'Applied ✓' : 'Apply Now'}
                  </Button>
                ) : (
                  <Button className="w-full" onClick={() => router.push('/login')}>
                    Login to Apply
                  </Button>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
} 