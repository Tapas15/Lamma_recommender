"use client";

import { useState } from "react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { Search, Filter, FolderOpen, Calendar, Users } from "lucide-react";
import { useI18n } from "../providers/i18n-provider";

// Mock data for projects
const MOCK_PROJECTS = [
  {
    id: "1",
    title: "Digital Learning Platform Development",
    clientName: "TechCorp Solutions",
    clientLogo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&auto=format&fit=crop",
    location: "Remote",
    projectType: "development" as const,
    duration: "6 months",
    budget: "$50,000 - $75,000",
    postedDate: "2 days ago",
    description: "Develop a comprehensive digital learning platform with interactive modules, progress tracking, and analytics dashboard...",
    skills: [
      "React/Next.js",
      "Learning Management Systems",
      "UI/UX Design",
      "Database Design"
    ],
    status: "open"
  },
  {
    id: "2",
    title: "Corporate Training Content Creation",
    clientName: "Global Enterprises Inc",
    clientLogo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&auto=format&fit=crop",
    location: "New York, NY",
    projectType: "content" as const,
    duration: "3 months",
    budget: "$25,000 - $40,000",
    postedDate: "1 week ago",
    description: "Create engaging training content for leadership development program including videos, interactive modules, and assessments...",
    skills: [
      "Instructional Design",
      "Video Production",
      "Content Writing",
      "Assessment Design"
    ],
    status: "open"
  },
  {
    id: "3",
    title: "Learning Analytics Dashboard",
    clientName: "EduTech Innovations",
    clientLogo: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&auto=format&fit=crop",
    location: "Remote",
    projectType: "analytics" as const,
    duration: "4 months",
    budget: "$30,000 - $50,000",
    postedDate: "3 days ago",
    description: "Build comprehensive analytics dashboard for tracking learner progress, engagement metrics, and performance insights...",
    skills: [
      "Data Analytics",
      "Dashboard Development",
      "Python/R",
      "Data Visualization"
    ],
    status: "open"
  }
];

export default function Projects() {
  const { t } = useI18n();
  const [searchTerm, setSearchTerm] = useState("");
  const [projectType, setProjectType] = useState("all");
  const [remoteOnly, setRemoteOnly] = useState(false);
  
  // Filter projects based on search and filters
  const filteredProjects = MOCK_PROJECTS.filter(project => {
    const matchesSearch = !searchTerm || 
      project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.skills.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesType = projectType === "all" || project.projectType === projectType;
    const matchesRemote = !remoteOnly || project.location.toLowerCase().includes("remote");
    
    return matchesSearch && matchesType && matchesRemote;
  });

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            L&D Projects
          </h1>
          <p className="text-lg text-slate-600 max-w-3xl">
            Discover exciting Learning & Development projects from organizations worldwide. 
            Find opportunities that match your expertise and grow your portfolio.
          </p>
        </div>

        {/* Search and Filters */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="md:col-span-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
                  <Input
                    placeholder="Search projects, skills, or keywords..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Project Type Filter */}
              <div>
                <Select value={projectType} onValueChange={setProjectType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Project Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="development">Development</SelectItem>
                    <SelectItem value="content">Content Creation</SelectItem>
                    <SelectItem value="analytics">Analytics</SelectItem>
                    <SelectItem value="consulting">Consulting</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Remote Filter */}
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="remote"
                  checked={remoteOnly}
                  onCheckedChange={(checked) => setRemoteOnly(checked === true)}
                />
                <label htmlFor="remote" className="text-sm font-medium">
                  Remote Only
                </label>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <FolderOpen className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 line-clamp-2">
                        {project.title}
                      </h3>
                      <p className="text-sm text-slate-600">{project.clientName}</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3 mb-4">
                  <div className="flex items-center text-sm text-slate-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    {project.duration} • {project.postedDate}
                  </div>
                  <div className="flex items-center text-sm text-slate-600">
                    <Users className="h-4 w-4 mr-2" />
                    {project.location}
                  </div>
                  <div className="text-sm font-medium text-green-600">
                    {project.budget}
                  </div>
                </div>

                <p className="text-sm text-slate-600 mb-4 line-clamp-3">
                  {project.description}
                </p>

                <div className="flex flex-wrap gap-2 mb-4">
                  {project.skills.slice(0, 3).map((skill, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                  {project.skills.length > 3 && (
                    <span className="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded-full">
                      +{project.skills.length - 3} more
                    </span>
                  )}
                </div>

                <div className="flex space-x-2">
                  <Button className="flex-1" size="sm">
                    Apply Now
                  </Button>
                  <Button variant="outline" size="sm">
                    Save
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* No results */}
        {filteredProjects.length === 0 && (
          <div className="text-center py-12">
            <FolderOpen className="h-16 w-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">
              No projects found
            </h3>
            <p className="text-slate-600">
              Try adjusting your search criteria or check back later for new projects.
            </p>
          </div>
        )}

        {/* Pagination */}
        {filteredProjects.length > 0 && (
          <div className="flex justify-center mt-8">
            <Button variant="outline" className="mx-1">1</Button>
            <Button variant="outline" className="mx-1">2</Button>
            <Button variant="outline" className="mx-1">3</Button>
            <Button variant="outline" className="mx-1">Next</Button>
          </div>
        )}
      </div>
    </div>
  );
} 