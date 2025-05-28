"use client";

import { MapPin, Clock, Star, User, Briefcase, GraduationCap } from "lucide-react";
import Link from "next/link";

interface ProfessionalCardProps {
  professional: {
  id: string;
    full_name: string;
    bio?: string;
    location?: string;
    experience_years?: number | string;
    skills?: {
      languages_frameworks?: string[];
      ai_ml_data?: string[];
      tools_platforms?: string[];
      tools?: string[];
      soft_skills?: string[];
    };
    education?: any[];
    experience?: any[];
    availability?: string;
    profile_views?: number;
    job_search_status?: string | {
      currently_looking?: boolean;
      available_from?: string;
      desired_job_titles?: string[];
      preferred_employment_type?: string[];
    };
  };
}

export default function ProfessionalCard({ professional }: ProfessionalCardProps) {
  // Extract top skills from all skill categories
  const getAllSkills = () => {
    const allSkills: string[] = [];
    if (professional.skills) {
      if (professional.skills.languages_frameworks) allSkills.push(...professional.skills.languages_frameworks);
      if (professional.skills.ai_ml_data) allSkills.push(...professional.skills.ai_ml_data);
      if (professional.skills.tools_platforms) allSkills.push(...professional.skills.tools_platforms);
      if (professional.skills.tools) allSkills.push(...professional.skills.tools);
      if (professional.skills.soft_skills) allSkills.push(...professional.skills.soft_skills);
    }
    return allSkills.slice(0, 4); // Show top 4 skills
  };

  const topSkills = getAllSkills();

  // Get latest experience/role
  const getLatestRole = () => {
    if (professional.experience && professional.experience.length > 0) {
      const latest = professional.experience[0];
      return latest.title || latest.position || "L&D Professional";
}
    return "L&D Professional";
  };

  // Get education level
  const getEducationLevel = () => {
    if (professional.education && professional.education.length > 0) {
      const latest = professional.education[0];
      return latest.degree || latest.qualification || "Qualified Professional";
    }
    return "Qualified Professional";
  };

  const formatExperience = (years?: number | string) => {
    if (!years) return "Entry Level";
    
    // Convert string to number if needed
    const numYears = typeof years === 'string' ? parseInt(years) || 0 : years;
    
    if (numYears === 1) return "1 year";
    if (numYears < 5) return `${numYears} years`;
    if (numYears < 10) return `${numYears}+ years`;
    return "Senior Level";
  };

  const getAvailabilityStatus = () => {
    // Handle complex job_search_status object
    if (typeof professional.job_search_status === 'object' && professional.job_search_status) {
      if (professional.job_search_status.currently_looking) return "Available";
      return "Open to offers";
    }
    
    // Handle simple string status
    if (professional.job_search_status === "actively_looking") return "Available";
    if (professional.job_search_status === "open_to_opportunities") return "Open to offers";
    if (professional.availability === "available") return "Available";
    return "Open to opportunities";
  };

  const getAvailabilityColor = () => {
    const status = getAvailabilityStatus();
    if (status === "Available") return "text-green-600 bg-green-50";
    return "text-blue-600 bg-blue-50";
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border border-gray-100">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
            {professional.full_name?.charAt(0)?.toUpperCase() || "P"}
        </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900 mb-1">
              {professional.full_name || "Professional"}
          </h3>
            <p className="text-sm text-slate-600">{getLatestRole()}</p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getAvailabilityColor()}`}>
          {getAvailabilityStatus()}
        </span>
      </div>

      {/* Bio */}
      {professional.bio && (
        <p className="text-slate-600 text-sm mb-4 line-clamp-2">
          {professional.bio}
        </p>
      )}

      {/* Details */}
      <div className="space-y-2 mb-4">
        {professional.location && (
          <div className="flex items-center text-sm text-slate-600">
            <MapPin className="h-4 w-4 mr-2 text-slate-400" />
            {professional.location}
          </div>
        )}
        
        <div className="flex items-center text-sm text-slate-600">
          <Briefcase className="h-4 w-4 mr-2 text-slate-400" />
          {formatExperience(professional.experience_years)} experience
        </div>

        <div className="flex items-center text-sm text-slate-600">
          <GraduationCap className="h-4 w-4 mr-2 text-slate-400" />
          {getEducationLevel()}
        </div>

        {professional.profile_views && (
          <div className="flex items-center text-sm text-slate-600">
            <User className="h-4 w-4 mr-2 text-slate-400" />
            {professional.profile_views} profile views
          </div>
        )}
      </div>

      {/* Skills */}
      {topSkills.length > 0 && (
        <div className="mb-4">
          <div className="flex flex-wrap gap-2">
            {topSkills.map((skill, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-slate-100 text-slate-700 rounded-md text-xs font-medium"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
        <div className="flex space-x-3">
        <Link
          href={`/professionals/${professional.id}`}
          className="flex-1 bg-blue-600 text-white text-center py-2 px-4 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
        >
              View Profile
            </Link>
        <button className="flex-1 border border-slate-300 text-slate-700 py-2 px-4 rounded-md hover:bg-slate-50 transition-colors text-sm font-medium">
          Contact
        </button>
      </div>
    </div>
  );
}
