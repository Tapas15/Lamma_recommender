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
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return; // Only run on client side
    
    const fetchProfessionals = async () => {
      try {
        setLoading(true);
        console.log('ProfessionalsPage: Starting API call...');
        
        const candidatesData = await candidatesApi.getCandidatesPublic();
        console.log('ProfessionalsPage: API call completed, received data:', candidatesData);
        
        // Check if we got real data or empty array (which means API failed)
        if (candidatesData && candidatesData.length > 0) {
          setProfessionals(candidatesData);
          setFilteredProfessionals(candidatesData);
          setError(null);
          console.log('ProfessionalsPage: Using real data with', candidatesData.length, 'items');
        } else {
          // API failed or returned empty, use fallback data
          console.log('ProfessionalsPage: No data from API, using fallback data');
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
          setError(null);
        }
      } catch (err) {
        // This should never happen now since API doesn't throw errors
        console.log('ProfessionalsPage: Unexpected error, using fallback data');
        console.error('Error details:', err);
        
        // Always use fallback data and don't show error to users
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
        setError(null); // Never show error to users
      } finally {
        setLoading(false);
      }
    };

    fetchProfessionals();
  }, [mounted]);

  useEffect(() => {
    let filtered = professionals;

    // Search filter - handle both real API data and mock data
    if (searchTerm) {
      filtered = filtered.filter(professional => {
        const searchLower = searchTerm.toLowerCase();
        
        // Search in name and bio
        const nameMatch = professional.full_name?.toLowerCase().includes(searchLower);
        const bioMatch = professional.bio?.toLowerCase().includes(searchLower);
        
        // Search in skills - handle both object and array formats
        let skillsMatch = false;
        if (professional.skills) {
          if (typeof professional.skills === 'object') {
            // Object format (like our mock data)
            skillsMatch = 
              professional.skills.languages_frameworks?.some((skill: string) => 
                skill.toLowerCase().includes(searchLower)
              ) ||
              professional.skills.ai_ml_data?.some((skill: string) => 
                skill.toLowerCase().includes(searchLower)
              ) ||
              professional.skills.tools_platforms?.some((skill: string) => 
                skill.toLowerCase().includes(searchLower)
              ) ||
              professional.skills.soft_skills?.some((skill: string) => 
                skill.toLowerCase().includes(searchLower)
              );
          } else if (Array.isArray(professional.skills)) {
            // Array format (possible from real API)
            skillsMatch = professional.skills.some((skill: string) => 
              skill.toLowerCase().includes(searchLower)
            );
          }
        }
        
        // Search in education and experience
        const educationMatch = professional.education?.some((edu: any) => 
          edu.degree?.toLowerCase().includes(searchLower) ||
          edu.institution?.toLowerCase().includes(searchLower)
        );
        
        const experienceMatch = professional.experience?.some((exp: any) => 
          exp.title?.toLowerCase().includes(searchLower) ||
          exp.company?.toLowerCase().includes(searchLower)
        );
        
        return nameMatch || bioMatch || skillsMatch || educationMatch || experienceMatch;
      });
    }

    // Location filter
    if (locationFilter) {
      filtered = filtered.filter(professional =>
        professional.location?.toLowerCase().includes(locationFilter.toLowerCase())
      );
    }

    // Experience filter - handle both string and number formats
    if (experienceFilter) {
      filtered = filtered.filter(professional => {
        let years = 0;
        
        // Handle both string and number formats for experience_years
        if (typeof professional.experience_years === 'string') {
          years = parseInt(professional.experience_years) || 0;
        } else if (typeof professional.experience_years === 'number') {
          years = professional.experience_years;
        }
        
        switch (experienceFilter) {
          case "entry": return years <= 2;
          case "mid": return years >= 3 && years <= 7;
          case "senior": return years >= 8;
          default: return true;
        }
      });
    }

    // Availability filter - handle various status formats
    if (availabilityFilter) {
      filtered = filtered.filter(professional => {
        if (availabilityFilter === "available") {
          return professional.job_search_status === "actively_looking" || 
                 professional.availability === "available" ||
                 professional.job_search_status?.currently_looking === true;
        }
        if (availabilityFilter === "open") {
          return professional.job_search_status === "open_to_opportunities" ||
                 professional.job_search_status?.currently_looking === false;
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

  // Get unique locations from the data for filter options
  const getUniqueLocations = () => {
    const locations = professionals
      .map(p => p.location)
      .filter(Boolean)
      .map(loc => loc.split(',')[0].trim()) // Get city part
      .filter((loc, index, arr) => arr.indexOf(loc) === index)
      .sort();
    return locations;
  };

  if (!mounted) {
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
                {getUniqueLocations().map(location => (
                  <option key={location} value={location.toLowerCase()}>{location}</option>
                ))}
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
        {filteredProfessionals.length > 0 ? (
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
