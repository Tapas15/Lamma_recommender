export const industryOptions = [
  'Technology',
  'Healthcare',
  'Finance',
  'Education',
  'Manufacturing',
  'Retail',
  'Real Estate',
  'Construction',
  'Transportation',
  'Hospitality',
  'Media & Entertainment',
  'Telecommunications',
  'Energy',
  'Agriculture',
  'Legal Services',
  'Marketing & Advertising',
  'Consulting',
  'Nonprofit',
  'Government',
  'Other'
];

export const educationLevels = [
  'High School',
  'Associate Degree',
  'Bachelor\'s Degree',
  'Master\'s Degree',
  'Doctorate',
  'Vocational Training',
  'Certification',
  'Other'
];

export const proficiencyLevels = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
  { value: 'expert', label: 'Expert' }
];

export const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

export const getFormattedErrorMessage = (error: any): string => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error?.message) {
    return error.message;
  }
  
  if (error?.data?.detail) {
    return error.data.detail;
  }
  
  return 'An unknown error occurred. Please try again.';
};

export interface Skill {
  name: string;
  proficiency: 'beginner' | 'intermediate' | 'advanced' | 'expert';
}

export interface Education {
  institution: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date?: string;
  current?: boolean;
}

export interface Experience {
  company: string;
  title: string;
  description: string;
  start_date: string;
  end_date?: string;
  current?: boolean;
}

export const createEmptySkill = (): Skill => ({
  name: '',
  proficiency: 'intermediate'
});

export const createEmptyEducation = (): Education => ({
  institution: '',
  degree: '',
  field_of_study: '',
  start_date: formatDate(new Date()),
  current: false
});

export const createEmptyExperience = (): Experience => ({
  company: '',
  title: '',
  description: '',
  start_date: formatDate(new Date()),
  current: false
});

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateUrl = (url: string): boolean => {
  if (!url) return true; // Optional URLs are valid when empty
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const capitalizeFirstLetter = (str: string): string => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}; 