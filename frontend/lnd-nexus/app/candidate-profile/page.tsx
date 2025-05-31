'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authApi } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
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
  User, 
  MapPin, 
  Mail, 
  Phone, 
  Briefcase, 
  GraduationCap, 
  Star,
  Plus,
  Edit,
  Save,
  X,
  Target,
  Clock,
  Award
} from 'lucide-react';

interface Experience {
  company: string;
  title: string;
  description: string;
  start_date: string;
  end_date?: string;
  current?: boolean;
}

interface Education {
  institution: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date?: string;
  current?: boolean;
}

interface CandidateProfile {
  full_name?: string;
  email: string;
  phone?: string;
  location?: string;
  bio?: string;
  skills?: {
    languages_frameworks?: string[];
    ai_ml_data?: string[];
    tools_platforms?: string[];
    soft_skills?: string[];
  };
  experience?: Experience[];
  education?: Education[];
  availability_hours?: number;
  remote_preference?: 'remote' | 'hybrid' | 'onsite';
  career_goals?: string;
  experience_years?: string;
  user_type?: string;
  [key: string]: any;
}

export default function CandidateProfilePage() {
  const { token } = useAuth();
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form states
  const [editedProfile, setEditedProfile] = useState<Partial<CandidateProfile>>({});
  const [newSkill, setNewSkill] = useState('');
  const [newSkillCategory, setNewSkillCategory] = useState<string>('languages_frameworks');

  const fetchProfile = async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      const data = await authApi.getProfile(token);
      setProfile(data);
      setEditedProfile(data);
    } catch (error) {
      console.error('Failed to load profile:', error);
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [token]);

  const handleSave = async () => {
    if (!token || !editedProfile) return;
    
    try {
      setSaving(true);
      setError(null);
      
      await authApi.updateProfile(token, editedProfile);
      setProfile({ ...profile, ...editedProfile } as CandidateProfile);
      setEditing(false);
      setSuccess('Profile updated successfully!');
      
      setTimeout(() => setSuccess(null), 3000);
    } catch (error) {
      console.error('Failed to update profile:', error);
      setError('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditedProfile(profile || {});
    setEditing(false);
    setError(null);
  };

  const addSkill = () => {
    if (!newSkill.trim()) return;
    
    const updatedSkills = { ...editedProfile.skills };
    if (!updatedSkills[newSkillCategory as keyof typeof updatedSkills]) {
      updatedSkills[newSkillCategory as keyof typeof updatedSkills] = [];
    }
    
    const skillArray = updatedSkills[newSkillCategory as keyof typeof updatedSkills] as string[];
    if (!skillArray.includes(newSkill.trim())) {
      skillArray.push(newSkill.trim());
      setEditedProfile({ ...editedProfile, skills: updatedSkills });
    }
    
    setNewSkill('');
  };

  const removeSkill = (category: string, skillToRemove: string) => {
    const updatedSkills = { ...editedProfile.skills };
    const skillArray = updatedSkills[category as keyof typeof updatedSkills] as string[];
    if (skillArray) {
      updatedSkills[category as keyof typeof updatedSkills] = skillArray.filter(
        skill => skill !== skillToRemove
      ) as any;
      setEditedProfile({ ...editedProfile, skills: updatedSkills });
    }
  };

  const getProficiencyColor = (proficiency: string) => {
    switch (proficiency) {
      case 'expert': return 'bg-green-100 text-green-800 border-green-200';
      case 'advanced': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSkillCategoryTitle = (category: string) => {
    switch (category) {
      case 'languages_frameworks': return 'Languages & Frameworks';
      case 'ai_ml_data': return 'AI/ML & Data';
      case 'tools_platforms': return 'Tools & Platforms';
      case 'soft_skills': return 'Soft Skills';
      default: return category;
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-6"></div>
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

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Candidate Profile</h1>
          {!editing ? (
            <Button onClick={() => setEditing(true)} className="flex items-center gap-2">
              <Edit className="h-4 w-4" />
              Edit Profile
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button onClick={handleSave} disabled={saving} className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                {saving ? 'Saving...' : 'Save'}
              </Button>
              <Button onClick={handleCancel} variant="outline" className="flex items-center gap-2">
                <X className="h-4 w-4" />
                Cancel
              </Button>
            </div>
          )}
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 text-green-700 p-4 rounded-lg mb-6">
            {success}
          </div>
        )}

        {/* Basic Information */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Personal Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                {editing ? (
                  <Input
                    value={editedProfile.full_name || ''}
                    onChange={(e) => setEditedProfile({ ...editedProfile, full_name: e.target.value })}
                    placeholder="Your full name"
                  />
                ) : (
                  <p className="text-gray-900">{profile?.full_name || 'Not provided'}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <p className="text-gray-900 flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  {profile?.email}
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone
                </label>
                {editing ? (
                  <Input
                    value={editedProfile.phone || ''}
                    onChange={(e) => setEditedProfile({ ...editedProfile, phone: e.target.value })}
                    placeholder="Your phone number"
                  />
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <Phone className="h-4 w-4" />
                    {profile?.phone || 'Not provided'}
                  </p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                {editing ? (
                  <Input
                    value={editedProfile.location || ''}
                    onChange={(e) => setEditedProfile({ ...editedProfile, location: e.target.value })}
                    placeholder="City, Country"
                  />
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    {profile?.location || 'Not provided'}
                  </p>
                )}
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Professional Bio
              </label>
              {editing ? (
                <Textarea
                  value={editedProfile.bio || ''}
                  onChange={(e) => setEditedProfile({ ...editedProfile, bio: e.target.value })}
                  placeholder="Tell us about your professional background and interests..."
                  rows={4}
                />
              ) : (
                <p className="text-gray-900">{profile?.bio || 'No bio provided'}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Work Preferences */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Work Preferences
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Remote Preference
                </label>
                {editing ? (
                  <Select 
                    value={editedProfile.remote_preference || 'hybrid'} 
                    onValueChange={(value) => setEditedProfile({ ...editedProfile, remote_preference: value as any })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="remote">Remote Only</SelectItem>
                      <SelectItem value="hybrid">Hybrid</SelectItem>
                      <SelectItem value="onsite">On-site Only</SelectItem>
                    </SelectContent>
                  </Select>
                ) : (
                  <p className="text-gray-900 capitalize">{profile?.remote_preference || 'Not specified'}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Availability (hours/week)
                </label>
                {editing ? (
                  <Input
                    type="number"
                    min="1"
                    max="80"
                    value={editedProfile.availability_hours || 40}
                    onChange={(e) => setEditedProfile({ ...editedProfile, availability_hours: parseInt(e.target.value) })}
                  />
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    {profile?.availability_hours || 40} hours/week
                  </p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Experience Level
                </label>
                {editing ? (
                  <Input
                    value={editedProfile.experience_years || ''}
                    onChange={(e) => setEditedProfile({ ...editedProfile, experience_years: e.target.value })}
                    placeholder="Years of experience"
                  />
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <Award className="h-4 w-4" />
                    {profile?.experience_years || 'Not specified'} years
                  </p>
                )}
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Career Goals
              </label>
              {editing ? (
                <Textarea
                  value={editedProfile.career_goals || ''}
                  onChange={(e) => setEditedProfile({ ...editedProfile, career_goals: e.target.value })}
                  placeholder="Describe your career aspirations and goals..."
                  rows={3}
                />
              ) : (
                <p className="text-gray-900">{profile?.career_goals || 'No career goals specified'}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Skills Section */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5" />
              Skills & Expertise
            </CardTitle>
          </CardHeader>
          <CardContent>
            {editing && (
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex gap-2 mb-2">
                  <Select value={newSkillCategory} onValueChange={setNewSkillCategory}>
                    <SelectTrigger className="w-48">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="languages_frameworks">Languages & Frameworks</SelectItem>
                      <SelectItem value="ai_ml_data">AI/ML & Data</SelectItem>
                      <SelectItem value="tools_platforms">Tools & Platforms</SelectItem>
                      <SelectItem value="soft_skills">Soft Skills</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    placeholder="Add a skill..."
                    onKeyPress={(e) => e.key === 'Enter' && addSkill()}
                  />
                  <Button onClick={addSkill} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
            
            <div className="space-y-6">
              {Object.entries(profile?.skills || {}).map(([category, skills]) => (
                <div key={category}>
                  <h3 className="font-semibold text-gray-900 mb-3">
                    {getSkillCategoryTitle(category)}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {(skills as string[])?.map((skill, index) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className="relative group"
                      >
                        {skill}
                        {editing && (
                          <button
                            onClick={() => removeSkill(category, skill)}
                            className="ml-2 text-red-500 hover:text-red-700"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        )}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="cursor-pointer hover:shadow-md transition-shadow">
            <CardContent className="p-6 text-center">
              <Briefcase className="h-8 w-8 mx-auto mb-3 text-blue-600" />
              <h3 className="font-semibold mb-2">Job Recommendations</h3>
              <p className="text-sm text-gray-600">Get personalized job matches</p>
            </CardContent>
          </Card>
          
          <Card className="cursor-pointer hover:shadow-md transition-shadow">
            <CardContent className="p-6 text-center">
              <Target className="h-8 w-8 mx-auto mb-3 text-green-600" />
              <h3 className="font-semibold mb-2">Skill Gap Analysis</h3>
              <p className="text-sm text-gray-600">Analyze your skill gaps</p>
            </CardContent>
          </Card>
          
          <Card className="cursor-pointer hover:shadow-md transition-shadow">
            <CardContent className="p-6 text-center">
              <GraduationCap className="h-8 w-8 mx-auto mb-3 text-purple-600" />
              <h3 className="font-semibold mb-2">Learning Path</h3>
              <p className="text-sm text-gray-600">Get learning recommendations</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 