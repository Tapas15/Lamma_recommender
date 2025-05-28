"use client";

import { useState, useEffect } from "react";
import { Search, Filter, MapPin, Briefcase, GraduationCap } from "lucide-react";
import ProfessionalCard from "../components/ProfessionalCard";
import { candidatesApi } from "../services/api";

export default function ProfessionalsPage() {
  const [professionals, setProfessionals] = useState<any[]>([]);
  const [filteredProfessionals, setFilteredProfessionals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [locationFilter, setLocationFilter] = useState("");
  const [experienceFilter, setExperienceFilter] = useState("");
  const [availabilityFilter, setAvailabilityFilter] = useState("");

  useEffect(() => {
    const fetchProfessionals = async () => {
      try {
        setLoading(true);
        const candidatesData = await candidatesApi.getCandidatesPublic();
        setProfessionals(candidatesData);
        setFilteredProfessionals(candidatesData);
        setError(null);
      } catch (err) {
        console.error('Error fetching professionals:', err);
        setError('Failed to load professionals');
        // Fallback to mock data if API fails
        const mockData = [
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
          },
          {
            id: "3",
            full_name: "Emily Rodriguez",
            bio: "Learning technology specialist focused on implementing innovative solutions for corporate training.",
            location: "Austin, TX",
            experience_years: 5,
            skills: {
              languages_frameworks: ["Vue.js", "PHP"],
              ai_ml_data: ["Educational Data Mining"],
              tools_platforms: ["Blackboard", "TalentLMS", "Slack"],
              soft_skills: ["Innovation", "Problem Solving", "Mentoring"]
            },
            education: [{ degree: "Master's in Learning Technologies" }],
            experience: [{ title: "Learning Technology Specialist" }],
            availability: "available",
            profile_views: 134,
            job_search_status: "actively_looking"
          },
          {
            id: "4",
            full_name: "David Kim",
            bio: "Senior training manager with expertise in leadership development and organizational change management.",
            location: "Seattle, WA",
            experience_years: 12,
            skills: {
              languages_frameworks: ["Angular", "Java"],
              ai_ml_data: ["Performance Analytics"],
              tools_platforms: ["SAP SuccessFactors", "Cornerstone", "Workday"],
              soft_skills: ["Leadership Development", "Change Management", "Strategic Planning"]
            },
            education: [{ degree: "MBA in Organizational Development" }],
            experience: [{ title: "Senior Training Manager" }],
            availability: "available",
            profile_views: 203,
            job_search_status: "open_to_opportunities"
          }
        ];
        setProfessionals(mockData);
        setFilteredProfessionals(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchProfessionals();
  }, []);

  useEffect(() => {
    let filtered = professionals;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(professional =>
        professional.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        professional.bio?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        professional.skills?.languages_frameworks?.some((skill: string) => 
          skill.toLowerCase().includes(searchTerm.toLowerCase())
        ) ||
        professional.skills?.ai_ml_data?.some((skill: string) => 
          skill.toLowerCase().includes(searchTerm.toLowerCase())
        ) ||
        professional.skills?.tools_platforms?.some((skill: string) => 
          skill.toLowerCase().includes(searchTerm.toLowerCase())
        ) ||
        professional.skills?.soft_skills?.some((skill: string) => 
          skill.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Location filter
    if (locationFilter) {
      filtered = filtered.filter(professional =>
        professional.location?.toLowerCase().includes(locationFilter.toLowerCase())
      );
    }

    // Experience filter
    if (experienceFilter) {
      filtered = filtered.filter(professional => {
        const years = professional.experience_years || 0;
        switch (experienceFilter) {
          case "entry": return years <= 2;
          case "mid": return years >= 3 && years <= 7;
          case "senior": return years >= 8;
          default: return true;
        }
      });
    }

    // Availability filter
    if (availabilityFilter) {
      filtered = filtered.filter(professional => {
        if (availabilityFilter === "available") {
          return professional.job_search_status === "actively_looking" || 
                 professional.availability === "available";
        }
        if (availabilityFilter === "open") {
          return professional.job_search_status === "open_to_opportunities";
        }
        return true;
      });
    }

    setFilteredProfessionals(filtered);
  }, [searchTerm, locationFilter, experienceFilter, availabilityFilter, professionals]);

  const clearFilters = () => {
    setSearchTerm("");
    setLocationFilter("");
    setExperienceFilter("");
    setAvailabilityFilter("");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              L&D Professionals
            </h1>
            <p className="text-lg text-slate-600">
              Connect with talented Learning & Development professionals
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
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
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            L&D Professionals
          </h1>
          <p className="text-lg text-slate-600">
            Connect with talented Learning & Development professionals
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="text"
                  placeholder="Search professionals, skills..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Location Filter */}
            <div>
              <select
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Locations</option>
                <option value="new york">New York</option>
                <option value="san francisco">San Francisco</option>
                <option value="austin">Austin</option>
                <option value="seattle">Seattle</option>
                <option value="remote">Remote</option>
              </select>
            </div>

            {/* Experience Filter */}
            <div>
              <select
                value={experienceFilter}
                onChange={(e) => setExperienceFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Experience</option>
                <option value="entry">Entry Level (0-2 years)</option>
                <option value="mid">Mid Level (3-7 years)</option>
                <option value="senior">Senior Level (8+ years)</option>
              </select>
            </div>

            {/* Availability Filter */}
            <div>
              <select
                value={availabilityFilter}
                onChange={(e) => setAvailabilityFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Availability</option>
                <option value="available">Available Now</option>
                <option value="open">Open to Offers</option>
              </select>
            </div>
          </div>

          {/* Clear Filters */}
          {(searchTerm || locationFilter || experienceFilter || availabilityFilter) && (
            <div className="mt-4">
              <button
                onClick={clearFilters}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="mb-6">
          <p className="text-slate-600">
            Showing {filteredProfessionals.length} of {professionals.length} professionals
          </p>
        </div>

        {/* Professionals Grid */}
        {error ? (
          <div className="text-center py-12">
            <p className="text-slate-600 mb-4">{error}</p>
            <p className="text-slate-500">Please try again later</p>
          </div>
        ) : filteredProfessionals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProfessionals.map((professional) => (
              <ProfessionalCard key={professional.id} professional={professional} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-slate-600 mb-4">No professionals found matching your criteria.</p>
            <button
              onClick={clearFilters}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Clear filters to see all professionals
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
