import { ArrowRight, FolderOpen, Calendar, Users, DollarSign } from "lucide-react";
import Link from "next/link";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";

const FEATURED_PROJECTS = [
  {
    id: "1",
    title: "Digital Learning Platform Development",
    clientName: "TechCorp Solutions",
    clientLogo: "https://logo.clearbit.com/microsoft.com",
    location: "Remote",
    projectType: "development" as const,
    duration: "6 months",
    budget: "$50,000 - $75,000",
    postedDate: "2 days ago",
    description: "Develop a comprehensive digital learning platform with interactive modules, progress tracking, and analytics dashboard for enterprise clients.",
    skills: ["React/Next.js", "Learning Management Systems", "UI/UX Design", "Database Design"],
    status: "open"
  },
  {
    id: "2",
    title: "Corporate Training Content Creation",
    clientName: "Global Enterprises Inc",
    clientLogo: "https://logo.clearbit.com/google.com",
    location: "New York, NY",
    projectType: "content" as const,
    duration: "3 months",
    budget: "$25,000 - $40,000",
    postedDate: "1 week ago",
    description: "Create engaging training content for leadership development program including videos, interactive modules, and comprehensive assessments.",
    skills: ["Instructional Design", "Video Production", "Content Writing", "Assessment Design"],
    status: "open"
  }
];

export default function FeaturedProjects() {
  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex justify-between items-center mb-12">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Featured L&D Projects
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl">
              Discover exciting Learning & Development projects from organizations worldwide. 
              Find opportunities that match your expertise.
            </p>
          </div>
          <Link 
            href="/projects" 
            className="hidden md:flex items-center text-blue-600 hover:text-blue-700 font-medium"
          >
            View all
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {FEATURED_PROJECTS.map((project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow border-0 shadow-md">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <FolderOpen className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 text-lg mb-1">
                        {project.title}
                      </h3>
                      <p className="text-sm text-slate-600">{project.clientName}</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="flex items-center text-sm text-slate-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    {project.duration}
                  </div>
                  <div className="flex items-center text-sm text-slate-600">
                    <Users className="h-4 w-4 mr-2" />
                    {project.location}
                  </div>
                  <div className="flex items-center text-sm font-medium text-green-600">
                    <DollarSign className="h-4 w-4 mr-1" />
                    {project.budget}
                  </div>
                  <div className="text-sm text-slate-500">
                    Posted {project.postedDate}
                  </div>
                </div>

                <p className="text-sm text-slate-600 mb-4 line-clamp-2">
                  {project.description}
                </p>

                <div className="flex flex-wrap gap-2 mb-6">
                  {project.skills.slice(0, 3).map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-50 text-blue-700 text-xs rounded-full font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                  {project.skills.length > 3 && (
                    <span className="px-3 py-1 bg-slate-100 text-slate-600 text-xs rounded-full">
                      +{project.skills.length - 3} more
                    </span>
                  )}
                </div>

                <div className="flex space-x-3">
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

        <div className="mt-8 text-center md:hidden">
          <Link 
            href="/projects" 
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