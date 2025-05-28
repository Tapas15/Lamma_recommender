"use client";

import { useState, useEffect } from "react";
import { ArrowRight } from "lucide-react";
import Link from "next/link";
import ProfessionalCard from "./ProfessionalCard";
import { candidatesApi } from "../services/api";

export default function FeaturedProfessionals() {
  const [professionals, setProfessionals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return; // Only run on client side
    
    const fetchProfessionals = async () => {
      try {
        setLoading(true);
        console.log('FeaturedProfessionals: Starting API call...');
        console.log('API Base URL:', process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000');
        console.log('Window location:', typeof window !== 'undefined' ? window.location.href : 'SSR');
        
        const candidatesData = await candidatesApi.getCandidatesPublic();
        console.log('FeaturedProfessionals: API call successful, received data:', candidatesData);
        
        // Take only the first 2 candidates for featured section
        setProfessionals(candidatesData.slice(0, 2));
        setError(null);
        console.log('FeaturedProfessionals: Set professionals state with', candidatesData.slice(0, 2).length, 'items');
      } catch (err: any) {
        console.log('FeaturedProfessionals: API call failed, using fallback data');
        console.error('Error details:', err);
        
        // Always use fallback data and don't show error to users
        setProfessionals([
          {
            id: "1",
            full_name: "Sarah Johnson",
            bio: "Experienced L&D professional specializing in digital transformation and employee development programs.",
            location: "New York, NY",
            experience_years: 8,
            skills: {
              languages_frameworks: ["JavaScript", "Python"],
              ai_ml_data: ["Machine Learning", "Data Analysis"],
              tools_platforms: ["LMS", "Articulate", "Adobe Captivate"],
              soft_skills: ["Leadership", "Communication", "Project Management"]
            },
            education: [{ degree: "Master's in Education Technology" }],
            experience: [{ title: "Senior L&D Manager" }],
            availability: "available",
            profile_views: 156,
            job_search_status: "open_to_opportunities"
          },
          {
            id: "2",
            full_name: "Michael Chen",
            bio: "Corporate trainer and instructional designer with expertise in creating engaging learning experiences.",
            location: "San Francisco, CA",
            experience_years: 6,
            skills: {
              languages_frameworks: ["React", "Node.js"],
              ai_ml_data: ["Learning Analytics"],
              tools_platforms: ["Moodle", "Canvas", "Zoom"],
              soft_skills: ["Training", "Curriculum Design", "Team Building"]
            },
            education: [{ degree: "Bachelor's in Instructional Design" }],
            experience: [{ title: "Instructional Designer" }],
            availability: "available",
            profile_views: 89,
            job_search_status: "actively_looking"
          }
        ]);
        setError(null); // Never show error to users
      } finally {
        setLoading(false);
      }
    };

    fetchProfessionals();
  }, [mounted]);

  if (!mounted) {
    return (
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
                Featured L&D Professionals
              </h2>
              <p className="text-lg text-slate-600 max-w-2xl">
                Connect with top Learning & Development professionals ready to drive your organization's growth.
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Loading skeletons */}
            {[1, 2].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse border border-gray-100">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
                  <div>
                    <div className="h-5 bg-gray-200 rounded mb-2 w-32"></div>
                    <div className="h-4 bg-gray-200 rounded w-24"></div>
                  </div>
                </div>
                <div className="h-4 bg-gray-200 rounded mb-4"></div>
                <div className="space-y-2 mb-4">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="flex space-x-2 mb-4">
                  <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                  <div className="h-6 bg-gray-200 rounded-full w-20"></div>
                </div>
                <div className="flex space-x-3">
                  <div className="h-10 bg-gray-200 rounded flex-1"></div>
                  <div className="h-10 bg-gray-200 rounded flex-1"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
                Featured L&D Professionals
              </h2>
              <p className="text-lg text-slate-600 max-w-2xl">
                Connect with top Learning & Development professionals ready to drive your organization's growth.
              </p>
            </div>
          </div>
          <div className="text-center py-12">
            <p className="text-slate-600 mb-4">{error}</p>
            <Link 
              href="/professionals" 
              className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
            >
              Browse all professionals
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex justify-between items-center mb-12">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Featured L&D Professionals
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl">
              Connect with top Learning & Development professionals ready to drive your organization's growth.
            </p>
          </div>
          <Link 
            href="/professionals" 
            className="hidden md:flex items-center text-blue-600 hover:text-blue-700 font-medium"
          >
            View all
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>

        {professionals.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {professionals.map((professional) => (
              <ProfessionalCard key={professional.id} professional={professional} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-slate-600 mb-4">No featured professionals available at the moment.</p>
            <Link 
              href="/professionals" 
              className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
            >
              Browse all professionals
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        )}

        <div className="mt-8 text-center md:hidden">
          <Link 
            href="/professionals" 
            className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
          >
            View all
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </div>
    </section>
  );
}
