import { useState } from 'react';

export interface ValidationRules {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  match?: string;
  customValidator?: (value: string) => boolean | string;
}

export interface FieldRules {
  [key: string]: ValidationRules;
}

export interface ValidationErrors {
  [key: string]: string | undefined;
}

export const useFormValidation = (rules: FieldRules) => {
  const [errors, setErrors] = useState<ValidationErrors>({});

  const validateField = (name: string, value: string, formData: Record<string, any>): string | undefined => {
    const fieldRules = rules[name];
    
    if (!fieldRules) return undefined;
    
    // Required validation
    if (fieldRules.required && !value) {
      return `${name} is required`;
    }
    
    // Minimum length validation
    if (fieldRules.minLength && value.length < fieldRules.minLength) {
      return `${name} must be at least ${fieldRules.minLength} characters`;
    }
    
    // Maximum length validation
    if (fieldRules.maxLength && value.length > fieldRules.maxLength) {
      return `${name} must be less than ${fieldRules.maxLength} characters`;
    }
    
    // Pattern validation
    if (fieldRules.pattern && !fieldRules.pattern.test(value)) {
      return `${name} format is invalid`;
    }
    
    // Match validation
    if (fieldRules.match && formData[fieldRules.match] !== value) {
      return `${name} does not match ${fieldRules.match}`;
    }
    
    // Custom validator
    if (fieldRules.customValidator) {
      const result = fieldRules.customValidator(value);
      if (typeof result === 'string') {
        return result;
      } else if (result === false) {
        return `${name} is invalid`;
      }
    }
    
    return undefined;
  };
  
  const validateForm = (formData: Record<string, any>): boolean => {
    const newErrors: ValidationErrors = {};
    let isValid = true;
    
    Object.keys(rules).forEach(fieldName => {
      const error = validateField(fieldName, formData[fieldName] || '', formData);
      
      if (error) {
        newErrors[fieldName] = error;
        isValid = false;
      }
    });
    
    setErrors(newErrors);
    return isValid;
  };
  
  const clearError = (fieldName: string) => {
    if (errors[fieldName]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[fieldName];
        return newErrors;
      });
    }
  };
  
  return { errors, validateForm, validateField, clearError, setErrors };
};

export default useFormValidation; 