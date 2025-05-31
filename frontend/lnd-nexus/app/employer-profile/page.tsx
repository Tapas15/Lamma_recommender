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
  Building, 
  MapPin, 
  Mail, 
  Phone, 
  Globe, 
  Users, 
  Star,
  Plus,
  Edit,
  Save,
  X,
  Target,
  Briefcase,
  Award,
  DollarSign,
  Calendar,
  LinkIcon
} from 'lucide-react';

interface CompanyDetails {
  company_name?: string;
  company_description?: string;
  company_website?: string;
  company_location?: string;
  company_size?: string;
  industry?: string;
  founded_year?: number;
  company_logo?: string;
  company_socials?: {
    linkedin?: string;
    twitter?: string;
    glassdoor?: string;
  };
  values?: string[];
  mission?: string;
  vision?: string;
}

interface HiringPreferences {
  job_roles_hiring?: string[];
  employment_types?: string[];
  locations_hiring?: string[];
  salary_range_usd?: {
    min?: number;
    max?: number;
  };
  remote_friendly?: boolean;
  tech_stack?: string[];
}

interface EmployerProfile {
  full_name?: string;
  email: string;
  position?: string;
  bio?: string;
  about?: string;
  contact_email?: string;
  contact_phone?: string;
  location?: string;
  company_details?: CompanyDetails;
  hiring_preferences?: HiringPreferences;
  user_type?: string;
  [key: string]: any;
}

const companySizeOptions = [
  '1-10 employees',
  '11-50 employees',
  '51-100 employees',
  '101-500 employees',
  '501-1000 employees',
  '1000+ employees'
];

const industryOptions = [
  'Technology',
  'Healthcare',
  'Finance',
  'Education',
  'Manufacturing',
  'Retail',
  'Consulting',
  'Media & Entertainment',
  'Non-profit',
  'Government',
  'Other'
];

const employmentTypeOptions = [
  'Full-time',
  'Part-time',
  'Contract',
  'Remote',
  'Hybrid',
  'Internship'
];

export default function EmployerProfilePage() {
  const { token } = useAuth();
  const [profile, setProfile] = useState<EmployerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form states
  const [editedProfile, setEditedProfile] = useState<Partial<EmployerProfile>>({});
  const [newValue, setNewValue] = useState('');
  const [newRole, setNewRole] = useState('');
  const [newLocation, setNewLocation] = useState('');
  const [newEmploymentType, setNewEmploymentType] = useState('');
  const [newTech, setNewTech] = useState('');

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

  // Derived data for easy access
  const companyDetails = profile?.company_details;
  const hiringPrefs = profile?.hiring_preferences;
  const socials = companyDetails?.company_socials;
  const salaryRange = hiringPrefs?.salary_range_usd;

  const handleSave = async () => {
    if (!token || !editedProfile) return;
    
    try {
      setSaving(true);
      setError(null);
      
      await authApi.updateProfile(token, editedProfile);
      setProfile({ ...profile, ...editedProfile } as EmployerProfile);
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

  const updateCompanyDetails = (field: string, value: any) => {
    const companyDetails = editedProfile.company_details || {};
    setEditedProfile({
      ...editedProfile,
      company_details: {
        ...companyDetails,
        [field]: value
      }
    });
  };

  const updateHiringPreferences = (field: string, value: any) => {
    const hiringPrefs = editedProfile.hiring_preferences || {};
    setEditedProfile({
      ...editedProfile,
      hiring_preferences: {
        ...hiringPrefs,
        [field]: value
      }
    });
  };

  const updateCompanySocials = (platform: string, value: string) => {
    const companyDetails = editedProfile.company_details || {};
    const socials = companyDetails.company_socials || {};
    setEditedProfile({
      ...editedProfile,
      company_details: {
        ...companyDetails,
        company_socials: {
          ...socials,
          [platform]: value
        }
      }
    });
  };

  const addValue = () => {
    if (!newValue.trim()) return;
    const companyDetails = editedProfile.company_details || {};
    const currentValues = companyDetails.values || [];
    updateCompanyDetails('values', [...currentValues, newValue.trim()]);
    setNewValue('');
  };

  const removeValue = (index: number) => {
    const companyDetails = editedProfile.company_details || {};
    const currentValues = companyDetails.values || [];
    updateCompanyDetails('values', currentValues.filter((_, i) => i !== index));
  };

  const addRole = () => {
    if (!newRole.trim()) return;
    const hiringPrefs = editedProfile.hiring_preferences || {};
    const currentRoles = hiringPrefs.job_roles_hiring || [];
    updateHiringPreferences('job_roles_hiring', [...currentRoles, newRole.trim()]);
    setNewRole('');
  };

  const removeRole = (index: number) => {
    const hiringPrefs = editedProfile.hiring_preferences || {};
    const currentRoles = hiringPrefs.job_roles_hiring || [];
    updateHiringPreferences('job_roles_hiring', currentRoles.filter((_, i) => i !== index));
  };

  const addLocation = () => {
    if (!newLocation.trim()) return;
    const hiringPrefs = editedProfile.hiring_preferences || {};
    const currentLocations = hiringPrefs.locations_hiring || [];
    updateHiringPreferences('locations_hiring', [...currentLocations, newLocation.trim()]);
    setNewLocation('');
  };

  const removeLocation = (index: number) => {
    const hiringPrefs = editedProfile.hiring_preferences || {};
    const currentLocations = hiringPrefs.locations_hiring || [];
    updateHiringPreferences('locations_hiring', currentLocations.filter((_, i) => i !== index));
  };

  const addEmploymentType = () => {
    if (!newEmploymentType.trim()) return;
    const hiringPrefs = editedProfile.hiring_preferences || {};
    const currentTypes = hiringPrefs.employment_types || [];
    if (!currentTypes.includes(newEmploymentType)) {
      updateHiringPreferences('employment_types', [...currentTypes, newEmploymentType]);
    }
    setNewEmploymentType('');
  };

  const removeEmploymentType = (index: number) => {
    const hiringPrefs = editedProfile.hiring_preferences || {};
    const currentTypes = hiringPrefs.employment_types || [];
    updateHiringPreferences('employment_types', currentTypes.filter((_, i) => i !== index));
  };

  const addTech = () => {
    if (!newTech.trim()) return;
    const hiringPrefs = editedProfile.hiring_preferences || {};
    const currentTech = hiringPrefs.tech_stack || [];
    updateHiringPreferences('tech_stack', [...currentTech, newTech.trim()]);
    setNewTech('');
  };

  const removeTech = (index: number) => {
    const hiringPrefs = editedProfile.hiring_preferences || {};
    const currentTech = hiringPrefs.tech_stack || [];
    updateHiringPreferences('tech_stack', currentTech.filter((_, i) => i !== index));
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

  if (!profile) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Profile Not Found</h1>
          <p className="text-gray-600">Unable to load your employer profile.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Employer Profile</h1>
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

        {/* Personal Information */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building className="h-5 w-5" />
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
                  Position/Title
                </label>
                {editing ? (
                  <Input
                    value={editedProfile.position || ''}
                    onChange={(e) => setEditedProfile({ ...editedProfile, position: e.target.value })}
                    placeholder="Your job title"
                  />
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <Briefcase className="h-4 w-4" />
                    {profile?.position || 'Not provided'}
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Email
                </label>
                {editing ? (
                  <Input
                    value={editedProfile.contact_email || ''}
                    onChange={(e) => setEditedProfile({ ...editedProfile, contact_email: e.target.value })}
                    placeholder="Business contact email"
                    type="email"
                  />
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    {profile?.contact_email || 'Not provided'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Phone
                </label>
                {editing ? (
                  <Input
                    value={editedProfile.contact_phone || ''}
                    onChange={(e) => setEditedProfile({ ...editedProfile, contact_phone: e.target.value })}
                    placeholder="Business phone number"
                  />
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <Phone className="h-4 w-4" />
                    {profile?.contact_phone || 'Not provided'}
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
                  placeholder="Brief professional introduction..."
                  rows={3}
                />
              ) : (
                <p className="text-gray-900">{profile?.bio || 'No bio provided'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                About
              </label>
              {editing ? (
                <Textarea
                  value={editedProfile.about || ''}
                  onChange={(e) => setEditedProfile({ ...editedProfile, about: e.target.value })}
                  placeholder="Detailed information about your professional background..."
                  rows={4}
                />
              ) : (
                <p className="text-gray-900">{profile?.about || 'No detailed information provided'}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Company Information */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building className="h-5 w-5" />
              Company Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Name
                </label>
                {editing ? (
                  <Input
                    value={(editedProfile.company_details?.company_name) || ''}
                    onChange={(e) => updateCompanyDetails('company_name', e.target.value)}
                    placeholder="Your company name"
                  />
                ) : (
                  <p className="text-gray-900">{companyDetails?.company_name || 'Not provided'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Industry
                </label>
                {editing ? (
                  <Select 
                    value={(editedProfile.company_details?.industry) || ''} 
                    onValueChange={(value) => updateCompanyDetails('industry', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select industry" />
                    </SelectTrigger>
                    <SelectContent>
                      {industryOptions.map((industry) => (
                        <SelectItem key={industry} value={industry}>{industry}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <p className="text-gray-900">{companyDetails?.industry || 'Not specified'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Size
                </label>
                {editing ? (
                  <Select 
                    value={(editedProfile.company_details?.company_size) || ''} 
                    onValueChange={(value) => updateCompanyDetails('company_size', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select company size" />
                    </SelectTrigger>
                    <SelectContent>
                      {companySizeOptions.map((size) => (
                        <SelectItem key={size} value={size}>{size}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    {companyDetails?.company_size || 'Not specified'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Founded Year
                </label>
                {editing ? (
                  <Input
                    type="number"
                    min="1800"
                    max={new Date().getFullYear()}
                    value={(editedProfile.company_details?.founded_year) || ''}
                    onChange={(e) => updateCompanyDetails('founded_year', parseInt(e.target.value))}
                    placeholder="Year founded"
                  />
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    {companyDetails?.founded_year || 'Not specified'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Location
                </label>
                {editing ? (
                  <Input
                    value={(editedProfile.company_details?.company_location) || ''}
                    onChange={(e) => updateCompanyDetails('company_location', e.target.value)}
                    placeholder="Company headquarters location"
                  />
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    {companyDetails?.company_location || 'Not provided'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Website
                </label>
                {editing ? (
                  <Input
                    value={(editedProfile.company_details?.company_website) || ''}
                    onChange={(e) => updateCompanyDetails('company_website', e.target.value)}
                    placeholder="https://company.com"
                    type="url"
                  />
                ) : (
                  <p className="text-gray-900 flex items-center gap-2">
                    <Globe className="h-4 w-4" />
                    {companyDetails?.company_website ? (
                      <a href={companyDetails.company_website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {companyDetails.company_website}
                      </a>
                    ) : 'Not provided'}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company Description
              </label>
              {editing ? (
                <Textarea
                  value={(editedProfile.company_details?.company_description) || ''}
                  onChange={(e) => updateCompanyDetails('company_description', e.target.value)}
                  placeholder="Describe your company, its mission, and what it does..."
                  rows={4}
                />
              ) : (
                <p className="text-gray-900">{companyDetails?.company_description || 'No company description provided'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mission Statement
              </label>
              {editing ? (
                <Textarea
                  value={(editedProfile.company_details?.mission) || ''}
                  onChange={(e) => updateCompanyDetails('mission', e.target.value)}
                  placeholder="Your company's mission statement..."
                  rows={2}
                />
              ) : (
                <p className="text-gray-900">{companyDetails?.mission || 'No mission statement provided'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Vision Statement
              </label>
              {editing ? (
                <Textarea
                  value={(editedProfile.company_details?.vision) || ''}
                  onChange={(e) => updateCompanyDetails('vision', e.target.value)}
                  placeholder="Your company's vision statement..."
                  rows={2}
                />
              ) : (
                <p className="text-gray-900">{companyDetails?.vision || 'No vision statement provided'}</p>
              )}
            </div>

            {/* Company Values */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company Values
              </label>
              {editing && (
                <div className="flex gap-2 mb-2">
                  <Input
                    value={newValue}
                    onChange={(e) => setNewValue(e.target.value)}
                    placeholder="Add a company value..."
                    onKeyPress={(e) => e.key === 'Enter' && addValue()}
                  />
                  <Button onClick={addValue} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              )}
              <div className="flex flex-wrap gap-2">
                {((editing ? editedProfile.company_details?.values : companyDetails?.values) || []).map((value, index) => (
                  <Badge key={index} variant="outline" className="flex items-center gap-1">
                    {value}
                    {editing && (
                      <button onClick={() => removeValue(index)} className="ml-1 text-red-500 hover:text-red-700">
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Social Links */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <LinkIcon className="h-5 w-5" />
              Company Social Links
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  LinkedIn
                </label>
                {editing ? (
                  <Input
                    value={(editedProfile.company_details?.company_socials?.linkedin) || ''}
                    onChange={(e) => updateCompanySocials('linkedin', e.target.value)}
                    placeholder="https://linkedin.com/company/..."
                    type="url"
                  />
                ) : (
                  <p className="text-gray-900">
                    {socials?.linkedin ? (
                      <a href={socials.linkedin} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {socials.linkedin}
                      </a>
                    ) : 'Not provided'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Twitter
                </label>
                {editing ? (
                  <Input
                    value={(editedProfile.company_details?.company_socials?.twitter) || ''}
                    onChange={(e) => updateCompanySocials('twitter', e.target.value)}
                    placeholder="https://twitter.com/..."
                    type="url"
                  />
                ) : (
                  <p className="text-gray-900">
                    {socials?.twitter ? (
                      <a href={socials.twitter} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {socials.twitter}
                      </a>
                    ) : 'Not provided'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Glassdoor
                </label>
                {editing ? (
                  <Input
                    value={(editedProfile.company_details?.company_socials?.glassdoor) || ''}
                    onChange={(e) => updateCompanySocials('glassdoor', e.target.value)}
                    placeholder="https://glassdoor.com/..."
                    type="url"
                  />
                ) : (
                  <p className="text-gray-900">
                    {socials?.glassdoor ? (
                      <a href={socials.glassdoor} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {socials.glassdoor}
                      </a>
                    ) : 'Not provided'}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Hiring Preferences */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Hiring Preferences
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Remote Friendly */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Remote Work Friendly
              </label>
              {editing ? (
                <Select 
                  value={(editedProfile.hiring_preferences?.remote_friendly) ? 'true' : 'false'} 
                  onValueChange={(value) => updateHiringPreferences('remote_friendly', value === 'true')}
                >
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="true">Yes</SelectItem>
                    <SelectItem value="false">No</SelectItem>
                  </SelectContent>
                </Select>
              ) : (
                <p className="text-gray-900">{hiringPrefs?.remote_friendly ? 'Yes' : 'No'}</p>
              )}
            </div>

            {/* Salary Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Salary Range (USD)
              </label>
              {editing ? (
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    type="number"
                    min="0"
                    value={(editedProfile.hiring_preferences?.salary_range_usd?.min) || ''}
                    onChange={(e) => {
                      const currentRange = editedProfile.hiring_preferences?.salary_range_usd || {};
                      updateHiringPreferences('salary_range_usd', {
                        ...currentRange,
                        min: parseInt(e.target.value)
                      });
                    }}
                    placeholder="Minimum salary"
                  />
                  <Input
                    type="number"
                    min="0"
                    value={(editedProfile.hiring_preferences?.salary_range_usd?.max) || ''}
                    onChange={(e) => {
                      const currentRange = editedProfile.hiring_preferences?.salary_range_usd || {};
                      updateHiringPreferences('salary_range_usd', {
                        ...currentRange,
                        max: parseInt(e.target.value)
                      });
                    }}
                    placeholder="Maximum salary"
                  />
                </div>
              ) : (
                <p className="text-gray-900 flex items-center gap-2">
                  <DollarSign className="h-4 w-4" />
                  {salaryRange?.min && salaryRange?.max 
                    ? `$${salaryRange.min?.toLocaleString()} - $${salaryRange.max?.toLocaleString()}`
                    : 'Not specified'
                  }
                </p>
              )}
            </div>

            {/* Job Roles Hiring */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Roles Currently Hiring
              </label>
              {editing && (
                <div className="flex gap-2 mb-2">
                  <Input
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    placeholder="Add a job role..."
                    onKeyPress={(e) => e.key === 'Enter' && addRole()}
                  />
                  <Button onClick={addRole} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              )}
              <div className="flex flex-wrap gap-2">
                {((editing ? editedProfile.hiring_preferences?.job_roles_hiring : hiringPrefs?.job_roles_hiring) || []).map((role, index) => (
                  <Badge key={index} variant="outline" className="flex items-center gap-1">
                    {role}
                    {editing && (
                      <button onClick={() => removeRole(index)} className="ml-1 text-red-500 hover:text-red-700">
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Employment Types */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Employment Types
              </label>
              {editing && (
                <div className="flex gap-2 mb-2">
                  <Select value={newEmploymentType} onValueChange={setNewEmploymentType}>
                    <SelectTrigger className="w-48">
                      <SelectValue placeholder="Select employment type" />
                    </SelectTrigger>
                    <SelectContent>
                      {employmentTypeOptions.map((type) => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button onClick={addEmploymentType} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              )}
              <div className="flex flex-wrap gap-2">
                {((editing ? editedProfile.hiring_preferences?.employment_types : hiringPrefs?.employment_types) || []).map((type, index) => (
                  <Badge key={index} variant="outline" className="flex items-center gap-1">
                    {type}
                    {editing && (
                      <button onClick={() => removeEmploymentType(index)} className="ml-1 text-red-500 hover:text-red-700">
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Hiring Locations */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hiring Locations
              </label>
              {editing && (
                <div className="flex gap-2 mb-2">
                  <Input
                    value={newLocation}
                    onChange={(e) => setNewLocation(e.target.value)}
                    placeholder="Add a hiring location..."
                    onKeyPress={(e) => e.key === 'Enter' && addLocation()}
                  />
                  <Button onClick={addLocation} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              )}
              <div className="flex flex-wrap gap-2">
                {((editing ? editedProfile.hiring_preferences?.locations_hiring : hiringPrefs?.locations_hiring) || []).map((location, index) => (
                  <Badge key={index} variant="outline" className="flex items-center gap-1">
                    {location}
                    {editing && (
                      <button onClick={() => removeLocation(index)} className="ml-1 text-red-500 hover:text-red-700">
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Tech Stack */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tech Stack
              </label>
              {editing && (
                <div className="flex gap-2 mb-2">
                  <Input
                    value={newTech}
                    onChange={(e) => setNewTech(e.target.value)}
                    placeholder="Add a technology..."
                    onKeyPress={(e) => e.key === 'Enter' && addTech()}
                  />
                  <Button onClick={addTech} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              )}
              <div className="flex flex-wrap gap-2">
                {((editing ? editedProfile.hiring_preferences?.tech_stack : hiringPrefs?.tech_stack) || []).map((tech, index) => (
                  <Badge key={index} variant="outline" className="flex items-center gap-1">
                    {tech}
                    {editing && (
                      <button onClick={() => removeTech(index)} className="ml-1 text-red-500 hover:text-red-700">
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="cursor-pointer hover:shadow-md transition-shadow">
            <CardContent className="p-6 text-center">
              <Briefcase className="h-8 w-8 mx-auto mb-3 text-blue-600" />
              <h3 className="font-semibold mb-2">Post New Job</h3>
              <p className="text-sm text-gray-600">Create and publish job openings</p>
            </CardContent>
          </Card>
          
          <Card className="cursor-pointer hover:shadow-md transition-shadow">
            <CardContent className="p-6 text-center">
              <Users className="h-8 w-8 mx-auto mb-3 text-green-600" />
              <h3 className="font-semibold mb-2">Browse Candidates</h3>
              <p className="text-sm text-gray-600">Find qualified candidates</p>
            </CardContent>
          </Card>
          
          <Card className="cursor-pointer hover:shadow-md transition-shadow">
            <CardContent className="p-6 text-center">
              <Award className="h-8 w-8 mx-auto mb-3 text-purple-600" />
              <h3 className="font-semibold mb-2">Hiring Analytics</h3>
              <p className="text-sm text-gray-600">View recruitment insights</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 