"use client";

import { useState, useEffect } from "react";
import { ArrowRight, FolderOpen, Calendar, Users, DollarSign } from "lucide-react";
import Link from "next/link";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { projectsApi } from "../services/api";

export default function FeaturedProjects() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const projectsData = await projectsApi.getProjectsPublic();
        // Take only the first 2 projects for featured section
        setProjects(projectsData.slice(0, 2));
        setError(null);
      } catch (err) {
        console.error('Error fetching projects:', err);
        setError('Failed to load projects');
        setProjects([]); // Fallback to empty array
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  if (loading) {
    return (
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Featured L&D Projects
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Discover exciting learning and development projects from top organizations
            </p>
          </div>
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading projects...</p>
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Featured L&D Projects
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Discover exciting learning and development projects from top organizations
            </p>
          </div>
          <div className="text-center">
            <p className="text-red-600">{error}</p>
            <p className="text-gray-500 mt-2">Please try again later</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Featured L&D Projects
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Discover exciting learning and development projects from top organizations
          </p>
        </div>

        {projects.length === 0 ? (
          <div className="text-center">
            <p className="text-gray-600">No projects available at the moment</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-8 mb-12">
            {projects.map((project) => (
              <Card key={project.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                        <FolderOpen className="h-6 w-6 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg text-gray-900">
                          {project.title}
                        </h3>
                        <p className="text-gray-600">{project.company}</p>
                      </div>
                    </div>
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                      {project.status || 'Open'}
                    </span>
                  </div>

                  <p className="text-gray-700 mb-4 line-clamp-3">
                    {project.description}
                  </p>

                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-1" />
                      <span>{project.duration || 'Flexible'}</span>
                    </div>
                    <div className="flex items-center">
                      <DollarSign className="h-4 w-4 mr-1" />
                      <span>{project.budget_range || 'Negotiable'}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {project.skills_required && project.skills_required.slice(0, 3).map((skill: string, index: number) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
                      >
                        {skill}
                      </span>
                    ))}
                    {project.skills_required && project.skills_required.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                        +{project.skills_required.length - 3} more
                      </span>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-sm text-gray-500">
                      <Users className="h-4 w-4 mr-1" />
                      <span>{project.project_type || 'Development'}</span>
                    </div>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        <div className="text-center">
          <Link href="/projects">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
              View All Projects
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
} 