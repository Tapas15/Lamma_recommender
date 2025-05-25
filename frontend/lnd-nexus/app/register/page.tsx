'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '../components/ui/button';
import RegisterForm from './RegisterForm';

export default function Register() {
  const router = useRouter();
  const [selectedType, setSelectedType] = useState<'candidate' | 'employer' | null>(null);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
              Sign in
            </Link>
          </p>
        </div>
        
        {!selectedType ? (
          <>
            <div className="mt-8">
              <div className="text-center text-lg font-medium text-gray-700 mb-4">
                I want to register as:
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div 
                  className="border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-all cursor-pointer bg-white flex flex-col items-center justify-center"
                  onClick={() => setSelectedType('candidate')}
                >
                  <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">Job Seeker</h3>
                  <p className="text-gray-600 text-center">
                    Find jobs, get personalized recommendations, and build your career
                  </p>
                  <Button
                    className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    onClick={() => setSelectedType('candidate')}
                  >
                    Register as a Job Seeker
                  </Button>
                </div>
                
                <div 
                  className="border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-all cursor-pointer bg-white flex flex-col items-center justify-center"
                  onClick={() => setSelectedType('employer')}
                >
                  <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">Employer</h3>
                  <p className="text-gray-600 text-center">
                    Post jobs, find qualified candidates, and grow your team
                  </p>
                  <Button
                    className="mt-4 w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
                    onClick={() => setSelectedType('employer')}
                  >
                    Register as an Employer
                  </Button>
                </div>
              </div>
            </div>
            
            <div className="mt-8 text-center text-sm text-gray-500">
              By creating an account, you agree to our{' '}
              <Link href="/terms" className="font-medium text-blue-600 hover:text-blue-500">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="font-medium text-blue-600 hover:text-blue-500">
                Privacy Policy
              </Link>
            </div>
          </>
        ) : (
          <div className="mt-8">
            <Button
              variant="outline"
              className="mb-6"
              onClick={() => setSelectedType(null)}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to selection
            </Button>
            
            <RegisterForm userType={selectedType} />
            
            <div className="mt-8 text-center text-sm text-gray-500">
              By creating an account, you agree to our{' '}
              <Link href="/terms" className="font-medium text-blue-600 hover:text-blue-500">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="font-medium text-blue-600 hover:text-blue-500">
                Privacy Policy
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 