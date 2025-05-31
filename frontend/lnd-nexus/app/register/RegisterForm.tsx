'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, RegistrationRequest, CandidateProfileData, EmployerProfileData, ApiError } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';
import useFormValidation, { FieldRules } from './useFormValidation';
import { 
  industryOptions, 
  getFormattedErrorMessage, 
  validateEmail, 
  validateUrl 
} from './formUtils';

interface RegisterFormProps {
  userType: 'candidate' | 'employer';
}

type Step = 'account' | 'details' | 'complete';

interface AccountData {
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
}

// Form component for registration
const RegisterForm: React.FC<RegisterFormProps> = ({ userType }) => {
  const router = useRouter();
  const [step, setStep] = useState<Step>('account');
  const [token, setToken] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Account information
  const [accountData, setAccountData] = useState<AccountData>({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
  });

  // Candidate profile data
  const [candidateData, setCandidateData] = useState<Partial<CandidateProfileData>>({
    skills: [],
    education: [],
    experience: [],
    availability_hours: 40,
    remote_preference: 'hybrid',
    career_goals: '',
    location: '',
  });

  // Employer profile data
  const [employerData, setEmployerData] = useState<Partial<EmployerProfileData>>({
    company_details: {
      company_name: '',
      company_size: 'small',
      industry: '',
      company_location: '',
      company_website: '',
      company_description: '',
    }
  });

  // Define validation rules for account form
  const accountRules: FieldRules = {
    email: {
      required: true,
      customValidator: (value) => validateEmail(value) || 'Please enter a valid email address'
    },
    password: {
      required: true,
      minLength: 8,
      customValidator: (value) => 
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value) || 
        'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    },
    confirmPassword: {
      required: true,
      match: 'password'
    },
    fullName: {
      required: true,
      minLength: 3
    }
  };

  // Define validation rules for candidate form
  const candidateRules: FieldRules = {
    location: {
      required: true
    }
  };

  // Define validation rules for employer form
  const employerRules: FieldRules = {
    'company_details.company_name': {
      required: true
    },
    'company_details.industry': {
      required: true
    },
    'company_details.company_location': {
      required: true
    },
    'company_details.company_website': {
      customValidator: (value) => !value || validateUrl(value) || 'Please enter a valid URL'
    }
  };

  // Use the appropriate validation rules based on the current step
  const { errors, validateForm, clearError } = useFormValidation(
    step === 'account' ? accountRules : 
    userType === 'candidate' ? candidateRules : employerRules
  );

  // Handle account data changes
  const handleAccountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setAccountData((prev) => ({ ...prev, [name]: value }));
    clearError(name);
  };

  // Handle candidate data changes
  const handleCandidateChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setCandidateData((prev) => ({ ...prev, [name]: value }));
    clearError(name);
  };

  // Handle select value changes for candidate
  const handleCandidateSelectChange = (name: string, value: string) => {
    setCandidateData((prev) => ({ ...prev, [name]: value }));
    clearError(name);
  };

  // Handle employer data changes
  const handleEmployerChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setEmployerData((prev) => ({
      ...prev,
      company_details: {
        ...prev.company_details,
        [name]: value
      }
    }));
    clearError(`company_details.${name}`);
  };

  // Handle select value changes for employer
  const handleEmployerSelectChange = (name: string, value: string) => {
    setEmployerData((prev) => ({
      ...prev,
      company_details: {
        ...prev.company_details,
        [name]: value
      }
    }));
    clearError(`company_details.${name}`);
  };

  // Handle next step
  const handleNext = async () => {
    if (step === 'account') {
      if (!validateForm(accountData)) return;
      
      try {
        setLoading(true);
        setError(null);
        
        let registrationData;
        
        if (userType === 'candidate') {
          // Create registration data for candidate
          registrationData = {
            email: accountData.email,
            password: accountData.password,
            full_name: accountData.fullName,
            // Add minimal required fields for a candidate
            phone: null,
            location: null,
            bio: null,
            skills: {
              languages_frameworks: [],
              ai_ml_data: [],
              tools_platforms: [],
              soft_skills: []
            },
            experience: [],
            education: []
          };
        } else {
          // Create registration data for employer
          registrationData = {
            email: accountData.email,
            password: accountData.password,
            full_name: accountData.fullName,
            user_type: 'employer',
            // Company details are required for employer registration
            company_details: {
              company_name: "To be updated", // Placeholder, will be updated in profile step
              industry: "Technology",         // Placeholder, will be updated in profile step
              company_location: null,
              company_size: null,
              company_website: null,
              company_description: null
            },
            hiring_preferences: {
              job_roles_hiring: [],
              remote_friendly: true
            }
          };
        }
        
        // Register the user
        const response = await authApi.register(registrationData);
        
        // Login to get token
        const tokenResponse = await authApi.login({ 
          username: accountData.email, 
          password: accountData.password 
        });
        
        // Save token
        setToken(tokenResponse.access_token);
        localStorage.setItem('auth_token', tokenResponse.access_token);
        
        // Move to details step
        setStep('details');
      } catch (err) {
        console.error('Registration error:', err);
        setError(getFormattedErrorMessage(err));
      } finally {
        setLoading(false);
      }
    } else if (step === 'details') {
      try {
        setLoading(true);
        setError(null);
        
        if (userType === 'candidate') {
          if (!validateForm(candidateData)) return;
          
          // Since we already created a basic profile during registration,
          // we just need to update it with the additional details
          const updatedProfileData = {
            location: candidateData.location,
            remote_preference: candidateData.remote_preference,
            availability_hours: candidateData.availability_hours,
            career_goals: candidateData.career_goals,
          };
          
          try {
            // Use the profile update endpoint
            await authApi.updateProfile(token, updatedProfileData);
          } catch (profileError) {
            console.error('Profile update error:', profileError);
            // Continue to next step even if profile update fails
          }
        } else {
          if (!validateForm(employerData)) return;
          
          // Since we already created a basic profile during registration,
          // we just need to update it with the additional details
          const updatedProfileData = {
            company_details: {
              company_name: employerData.company_details?.company_name,
              industry: employerData.company_details?.industry,
              company_size: employerData.company_details?.company_size,
              company_location: employerData.company_details?.company_location,
              company_website: employerData.company_details?.company_website,
              company_description: employerData.company_details?.company_description,
            }
          };
          
          try {
            // Use the profile update endpoint
            await authApi.updateProfile(token, updatedProfileData);
          } catch (profileError) {
            console.error('Profile update error:', profileError);
            // Continue to next step even if profile update fails
          }
        }
        
        // Registration complete
        setStep('complete');
      } catch (err) {
        console.error('Profile creation error:', err);
        setError(getFormattedErrorMessage(err));
      } finally {
        setLoading(false);
      }
    } else if (step === 'complete') {
      // Redirect to dashboard
      router.push('/dashboard');
    }
  };

  // Render account form
  const renderAccountForm = () => (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-center mb-6">
        Create your account
      </h2>
      
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <Input
          id="email"
          name="email"
          type="email"
          value={accountData.email}
          onChange={handleAccountChange}
          placeholder="your@email.com"
          className={errors.email ? 'border-red-500' : ''}
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email}</p>
        )}
      </div>
      
      <div>
        <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-1">
          Full Name
        </label>
        <Input
          id="fullName"
          name="fullName"
          type="text"
          value={accountData.fullName}
          onChange={handleAccountChange}
          placeholder="John Doe"
          className={errors.fullName ? 'border-red-500' : ''}
        />
        {errors.fullName && (
          <p className="mt-1 text-sm text-red-600">{errors.fullName}</p>
        )}
      </div>
      
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
          Password
        </label>
        <Input
          id="password"
          name="password"
          type="password"
          value={accountData.password}
          onChange={handleAccountChange}
          placeholder="••••••••"
          className={errors.password ? 'border-red-500' : ''}
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          Must be at least 8 characters with uppercase, lowercase, and number
        </p>
      </div>
      
      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
          Confirm Password
        </label>
        <Input
          id="confirmPassword"
          name="confirmPassword"
          type="password"
          value={accountData.confirmPassword}
          onChange={handleAccountChange}
          placeholder="••••••••"
          className={errors.confirmPassword ? 'border-red-500' : ''}
        />
        {errors.confirmPassword && (
          <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
        )}
      </div>
    </div>
  );

  // Render candidate details form
  const renderCandidateForm = () => (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-center mb-6">
        Complete your candidate profile
      </h2>
      
      <div>
        <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
          Location
        </label>
        <Input
          id="location"
          name="location"
          type="text"
          value={candidateData.location || ''}
          onChange={handleCandidateChange}
          placeholder="City, Country"
          className={errors.location ? 'border-red-500' : ''}
        />
        {errors.location && (
          <p className="mt-1 text-sm text-red-600">{errors.location}</p>
        )}
      </div>
      
      <div>
        <label htmlFor="remote_preference" className="block text-sm font-medium text-gray-700 mb-1">
          Remote Work Preference
        </label>
        <Select 
          value={candidateData.remote_preference || 'hybrid'} 
          onValueChange={(value) => handleCandidateSelectChange('remote_preference', value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select remote work preference" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="remote">Remote Only</SelectItem>
            <SelectItem value="hybrid">Hybrid</SelectItem>
            <SelectItem value="onsite">On-site Only</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div>
        <label htmlFor="availability_hours" className="block text-sm font-medium text-gray-700 mb-1">
          Weekly Availability (hours)
        </label>
        <Input
          id="availability_hours"
          name="availability_hours"
          type="number"
          min="1"
          max="80"
          value={candidateData.availability_hours || 40}
          onChange={handleCandidateChange}
        />
      </div>
      
      <div>
        <label htmlFor="career_goals" className="block text-sm font-medium text-gray-700 mb-1">
          Career Goals
        </label>
        <Textarea
          id="career_goals"
          name="career_goals"
          value={candidateData.career_goals || ''}
          onChange={handleCandidateChange}
          placeholder="Tell us about your career aspirations..."
          rows={4}
        />
      </div>

      <p className="text-sm text-gray-500 mt-2">
        You can add your skills, education, and work experience after registration.
      </p>
    </div>
  );

  // Render employer details form
  const renderEmployerForm = () => (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-center mb-6">
        Complete your employer profile
      </h2>
      
      <div>
        <label htmlFor="company_name" className="block text-sm font-medium text-gray-700 mb-2">
          Company Name *
        </label>
        <Input
          id="company_name"
          name="company_name"
          type="text"
          value={employerData.company_details?.company_name || ''}
          onChange={handleEmployerChange}
          placeholder="Acme Inc."
          className={errors['company_details.company_name'] ? 'border-red-500' : ''}
        />
        {errors['company_details.company_name'] && (
          <p className="mt-1 text-sm text-red-600">{errors['company_details.company_name']}</p>
        )}
      </div>
      
      <div>
        <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-2">
          Industry *
        </label>
        <Select 
          value={employerData.company_details?.industry || ''} 
          onValueChange={(value) => handleEmployerSelectChange('industry', value)}
        >
          <SelectTrigger className={errors['company_details.industry'] ? 'border-red-500' : ''}>
            <SelectValue placeholder="Select your industry" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="technology">Technology</SelectItem>
            <SelectItem value="healthcare">Healthcare</SelectItem>
            <SelectItem value="finance">Finance</SelectItem>
            <SelectItem value="education">Education</SelectItem>
            <SelectItem value="manufacturing">Manufacturing</SelectItem>
            <SelectItem value="retail">Retail</SelectItem>
            <SelectItem value="consulting">Consulting</SelectItem>
            <SelectItem value="other">Other</SelectItem>
          </SelectContent>
        </Select>
        {errors['company_details.industry'] && (
          <p className="mt-1 text-sm text-red-600">{errors['company_details.industry']}</p>
        )}
      </div>
      
      <div>
        <label htmlFor="company_size" className="block text-sm font-medium text-gray-700 mb-2">
          Company Size
        </label>
        <Select 
          value={employerData.company_details?.company_size || 'small'} 
          onValueChange={(value) => handleEmployerSelectChange('company_size', value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select company size" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="startup">Startup (1-10 employees)</SelectItem>
            <SelectItem value="small">Small (11-50 employees)</SelectItem>
            <SelectItem value="medium">Medium (51-200 employees)</SelectItem>
            <SelectItem value="large">Large (201-1000 employees)</SelectItem>
            <SelectItem value="enterprise">Enterprise (1000+ employees)</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div>
        <label htmlFor="company_location" className="block text-sm font-medium text-gray-700 mb-2">
          Company Location *
        </label>
        <Input
          id="company_location"
          name="company_location"
          type="text"
          value={employerData.company_details?.company_location || ''}
          onChange={handleEmployerChange}
          placeholder="City, Country"
          className={errors['company_details.company_location'] ? 'border-red-500' : ''}
        />
        {errors['company_details.company_location'] && (
          <p className="mt-1 text-sm text-red-600">{errors['company_details.company_location']}</p>
        )}
      </div>
      
      <div>
        <label htmlFor="company_website" className="block text-sm font-medium text-gray-700 mb-2">
          Company Website
        </label>
        <Input
          id="company_website"
          name="company_website"
          type="url"
          value={employerData.company_details?.company_website || ''}
          onChange={handleEmployerChange}
          placeholder="https://yourcompany.com"
          className={errors['company_details.company_website'] ? 'border-red-500' : ''}
        />
        {errors['company_details.company_website'] && (
          <p className="mt-1 text-sm text-red-600">{errors['company_details.company_website']}</p>
        )}
      </div>
      
      <div>
        <label htmlFor="company_description" className="block text-sm font-medium text-gray-700 mb-2">
          Company Description
        </label>
        <Textarea
          id="company_description"
          name="company_description"
          value={employerData.company_details?.company_description || ''}
          onChange={handleEmployerChange}
          placeholder="Tell us about your company..."
          rows={4}
        />
      </div>
    </div>
  );

  // Render completion message
  const renderCompletion = () => (
    <div className="text-center space-y-4">
      <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      
      <h2 className="text-2xl font-semibold text-gray-800">Registration Complete!</h2>
      
      <p className="text-gray-600">
        Thank you for joining our platform. Your account has been created successfully.
      </p>
      
      {userType === 'candidate' ? (
        <p className="text-gray-600">
          You can now explore job opportunities, add more details to your profile, and receive personalized recommendations.
        </p>
      ) : (
        <p className="text-gray-600">
          You can now post jobs, search for candidates, and manage your company profile.
        </p>
      )}
    </div>
  );

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      {/* Progress indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className={`rounded-full h-8 w-8 flex items-center justify-center ${step === 'account' || step === 'details' || step === 'complete' ? 'bg-blue-600 text-white' : 'bg-gray-300'}`}>
              1
            </div>
            <div className={`h-1 w-10 ${step === 'details' || step === 'complete' ? 'bg-blue-600' : 'bg-gray-300'}`} />
          </div>
          
          <div className="flex items-center">
            <div className={`rounded-full h-8 w-8 flex items-center justify-center ${step === 'details' || step === 'complete' ? 'bg-blue-600 text-white' : 'bg-gray-300'}`}>
              2
            </div>
            <div className={`h-1 w-10 ${step === 'complete' ? 'bg-blue-600' : 'bg-gray-300'}`} />
          </div>
          
          <div className={`rounded-full h-8 w-8 flex items-center justify-center ${step === 'complete' ? 'bg-blue-600 text-white' : 'bg-gray-300'}`}>
            3
          </div>
        </div>
        
        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span>Account</span>
          <span>Profile</span>
          <span>Complete</span>
        </div>
      </div>
      
      {/* Form error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {/* Form steps */}
      {step === 'account' && renderAccountForm()}
      {step === 'details' && userType === 'candidate' && renderCandidateForm()}
      {step === 'details' && userType === 'employer' && renderEmployerForm()}
      {step === 'complete' && renderCompletion()}
      
      {/* Form actions */}
      <div className="mt-8">
        <Button
          className={`w-full ${userType === 'candidate' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-emerald-600 hover:bg-emerald-700'} text-white py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 ${userType === 'candidate' ? 'focus:ring-blue-500' : 'focus:ring-emerald-500'}`}
          onClick={handleNext}
          disabled={loading}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </div>
          ) : step === 'account' ? (
            'Continue'
          ) : step === 'details' ? (
            'Complete Registration'
          ) : (
            'Go to Dashboard'
          )}
        </Button>
      </div>
    </div>
  );
};

export default RegisterForm; 