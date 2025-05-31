"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { 
  Search, 
  Filter, 
  FolderOpen, 
  Calendar, 
  Users, 
  DollarSign, 
  Plus, 
  Edit, 
  Trash2, 
  Save, 
  X,
  MapPin,
  Building,
  Clock,
  Target,
  CheckCircle
} from "lucide-react";
import { projectsApi } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

interface Project {
  id: string;
  title: string;
  company: string;
  description: string;
  project_type: string;
  status: 'open' | 'in_progress' | 'completed' | 'on_hold';
  location?: string;
  budget?: {
    min: number;
    max: number;
    currency: string;
  };
  duration?: string;
  start_date?: string;
  end_date?: string;
  skills_required?: string[];
  deliverables?: string[];
  requirements?: string[];
  created_at: string;
  employer_id?: string;
  remote_option?: boolean;
}

export default function Projects() {
  const { user, token } = useAuth();
  const [allProjects, setAllProjects] = useState<Project[]>([]);
  const [myProjects, setMyProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedType, setSelectedType] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [remoteOnly, setRemoteOnly] = useState(false);

  // Project management states
  const [showProjectForm, setShowProjectForm] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [formData, setFormData] = useState<Partial<Project>>({
    title: '',
    company: '',
    description: '',
    project_type: 'development',
    status: 'open',
    location: '',
    duration: '',
    skills_required: [],
    deliverables: [],
    requirements: [],
    remote_option: false
  });
  const [saving, setSaving] = useState(false);

  const isEmployer = user?.user_type === 'employer';

  useEffect(() => {
    fetchProjects();
    if (isEmployer && token) {
      fetchMyProjects();
    }
  }, [isEmployer, token]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const projectsData = await projectsApi.getProjectsPublic();
      setAllProjects(projectsData || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to load projects');
      setAllProjects([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchMyProjects = async () => {
    if (!token) return;
    
    try {
      const projectsData = await projectsApi.getProjects(token);
      setMyProjects(projectsData || []);
    } catch (err) {
      console.error('Error fetching my projects:', err);
      setMyProjects([]);
    }
  };

  const handleCreateProject = async () => {
    if (!token || !formData.title || !formData.description) return;

    try {
      setSaving(true);
      const projectData = {
        ...formData,
        employer_id: user?.id,
        created_at: new Date().toISOString()
      };

      await projectsApi.createProject(token, projectData);
      await fetchMyProjects();
      resetForm();
      setShowProjectForm(false);
    } catch (error) {
      console.error('Failed to create project:', error);
      setError('Failed to create project');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateProject = async () => {
    if (!token || !editingProject || !formData.title || !formData.description) return;

    try {
      setSaving(true);
      await projectsApi.updateProject(token, editingProject.id, formData);
      await fetchMyProjects();
      resetForm();
      setEditingProject(null);
      setShowProjectForm(false);
    } catch (error) {
      console.error('Failed to update project:', error);
      setError('Failed to update project');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    if (!token || !confirm('Are you sure you want to delete this project?')) return;

    try {
      await projectsApi.deleteProject(token, projectId);
      await fetchMyProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
      setError('Failed to delete project');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      company: '',
      description: '',
      project_type: 'development',
      status: 'open',
      location: '',
      duration: '',
      skills_required: [],
      deliverables: [],
      requirements: [],
      remote_option: false
    });
  };

  const startEditing = (project: Project) => {
    setEditingProject(project);
    setFormData({ ...project });
    setShowProjectForm(true);
  };

  const addListItem = (field: 'skills_required' | 'deliverables' | 'requirements', value: string) => {
    if (!value.trim()) return;
    
    const currentList = formData[field] || [];
    setFormData({
      ...formData,
      [field]: [...currentList, value.trim()]
    });
  };

  const removeListItem = (field: 'skills_required' | 'deliverables' | 'requirements', index: number) => {
    const currentList = formData[field] || [];
    setFormData({
      ...formData,
      [field]: currentList.filter((_, i) => i !== index)
    });
  };

  const formatDuration = (duration: string | undefined) => {
    if (!duration) return "Not specified";
    return duration;
  };

  const formatDate = (date: string | undefined) => {
    if (!date) return "Not set";
    
    try {
      return new Date(date).toLocaleDateString();
    } catch {
      return "Invalid date";
    }
  };

  // Filter projects based on search criteria
  const filteredProjects = allProjects.filter(project => {
    const matchesSearch = !searchTerm || 
      project.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.company?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = selectedType === "all" || project.project_type === selectedType;
    const matchesStatus = selectedStatus === "all" || project.status === selectedStatus;
    const matchesRemote = !remoteOnly || project.remote_option;

    return matchesSearch && matchesType && matchesStatus && matchesRemote;
  });

  const filteredMyProjects = myProjects.filter(project => {
    const matchesSearch = !searchTerm || 
      project.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.company?.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSearch;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'on_hold': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {isEmployer ? 'Project Management' : 'L&D Projects'}
            </h1>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div className="h-6 bg-gray-200 rounded mb-4"></div>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded mb-4 w-3/4"></div>
                <div className="flex space-x-2 mb-4">
                  <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                  <div className="h-6 bg-gray-200 rounded-full w-20"></div>
                </div>
                <div className="h-10 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {isEmployer ? 'Project Management' : 'L&D Projects'}
          </h1>
          <p className="text-gray-600">
            {isEmployer 
              ? 'Manage your learning and development projects and collaborate with experts.'
              : 'Discover exciting learning and development projects from organizations worldwide.'
            }
          </p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Employer vs Candidate View */}
        {isEmployer ? (
          <Tabs defaultValue="my-projects" className="space-y-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="my-projects">My Projects ({myProjects.length})</TabsTrigger>
              <TabsTrigger value="browse">Browse All Projects</TabsTrigger>
            </TabsList>

            {/* My Projects Tab */}
            <TabsContent value="my-projects" className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">My Project Postings</h2>
                <Button 
                  onClick={() => {
                    resetForm();
                    setEditingProject(null);
                    setShowProjectForm(true);
                  }}
                  className="flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Create New Project
                </Button>
              </div>

              {/* Project Creation/Edit Form */}
              {showProjectForm && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      {editingProject ? 'Edit Project' : 'Create New Project'}
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setShowProjectForm(false);
                          setEditingProject(null);
                          resetForm();
                        }}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        placeholder="Project Title"
                        value={formData.title || ''}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      />
                      <Input
                        placeholder="Company Name"
                        value={formData.company || ''}
                        onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                      />
                      <Input
                        placeholder="Location"
                        value={formData.location || ''}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      />
                      <Input
                        placeholder="Duration (e.g., 3 months)"
                        value={formData.duration || ''}
                        onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Select 
                        value={formData.project_type || 'development'} 
                        onValueChange={(value) => setFormData({ ...formData, project_type: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="development">Development</SelectItem>
                          <SelectItem value="content">Content Creation</SelectItem>
                          <SelectItem value="consulting">Consulting</SelectItem>
                          <SelectItem value="training">Training</SelectItem>
                          <SelectItem value="research">Research</SelectItem>
                          <SelectItem value="design">Design</SelectItem>
                        </SelectContent>
                      </Select>

                      <Select 
                        value={formData.status || 'open'} 
                        onValueChange={(value) => setFormData({ ...formData, status: value as Project['status'] })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="open">Open</SelectItem>
                          <SelectItem value="in_progress">In Progress</SelectItem>
                          <SelectItem value="completed">Completed</SelectItem>
                          <SelectItem value="on_hold">On Hold</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="remote-project"
                        checked={formData.remote_option || false}
                        onCheckedChange={(checked) => setFormData({ ...formData, remote_option: checked === true })}
                      />
                      <label htmlFor="remote-project" className="text-sm font-medium">
                        Remote Work Available
                      </label>
                    </div>

                    <Textarea
                      placeholder="Project Description"
                      value={formData.description || ''}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={4}
                    />

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Skills Required</label>
                        <div className="space-y-2">
                          <div className="flex gap-2">
                            <Input 
                              placeholder="Add skill..."
                              onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  addListItem('skills_required', e.currentTarget.value);
                                  e.currentTarget.value = '';
                                }
                              }}
                            />
                            <Button 
                              size="sm"
                              onClick={(e) => {
                                const input = e.currentTarget.parentElement?.querySelector('input') as HTMLInputElement;
                                if (input) {
                                  addListItem('skills_required', input.value);
                                  input.value = '';
                                }
                              }}
                            >
                              Add
                            </Button>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {(formData.skills_required || []).map((skill, index) => (
                              <Badge key={index} variant="secondary" className="flex items-center gap-1">
                                {skill}
                                <button onClick={() => removeListItem('skills_required', index)}>
                                  <X className="h-3 w-3" />
                                </button>
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">Deliverables</label>
                        <div className="space-y-2">
                          <div className="flex gap-2">
                            <Input 
                              placeholder="Add deliverable..."
                              onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  addListItem('deliverables', e.currentTarget.value);
                                  e.currentTarget.value = '';
                                }
                              }}
                            />
                            <Button 
                              size="sm"
                              onClick={(e) => {
                                const input = e.currentTarget.parentElement?.querySelector('input') as HTMLInputElement;
                                if (input) {
                                  addListItem('deliverables', input.value);
                                  input.value = '';
                                }
                              }}
                            >
                              Add
                            </Button>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {(formData.deliverables || []).map((deliverable, index) => (
                              <Badge key={index} variant="secondary" className="flex items-center gap-1">
                                {deliverable}
                                <button onClick={() => removeListItem('deliverables', index)}>
                                  <X className="h-3 w-3" />
                                </button>
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">Requirements</label>
                        <div className="space-y-2">
                          <div className="flex gap-2">
                            <Input 
                              placeholder="Add requirement..."
                              onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  addListItem('requirements', e.currentTarget.value);
                                  e.currentTarget.value = '';
                                }
                              }}
                            />
                            <Button 
                              size="sm"
                              onClick={(e) => {
                                const input = e.currentTarget.parentElement?.querySelector('input') as HTMLInputElement;
                                if (input) {
                                  addListItem('requirements', input.value);
                                  input.value = '';
                                }
                              }}
                            >
                              Add
                            </Button>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {(formData.requirements || []).map((req, index) => (
                              <Badge key={index} variant="secondary" className="flex items-center gap-1">
                                {req}
                                <button onClick={() => removeListItem('requirements', index)}>
                                  <X className="h-3 w-3" />
                                </button>
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-end gap-2">
                      <Button 
                        variant="outline"
                        onClick={() => {
                          setShowProjectForm(false);
                          setEditingProject(null);
                          resetForm();
                        }}
                      >
                        Cancel
                      </Button>
                      <Button 
                        onClick={editingProject ? handleUpdateProject : handleCreateProject}
                        disabled={saving || !formData.title || !formData.description}
                      >
                        <Save className="h-4 w-4 mr-2" />
                        {saving ? 'Saving...' : editingProject ? 'Update Project' : 'Create Project'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* My Projects List */}
              <div className="space-y-4">
                {filteredMyProjects.length === 0 ? (
                  <Card>
                    <CardContent className="text-center py-8">
                      <FolderOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No projects created yet</h3>
                      <p className="text-gray-600 mb-4">Create your first project to start collaborating with experts</p>
                      <Button onClick={() => setShowProjectForm(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Create Your First Project
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  filteredMyProjects.map((project) => (
                    <Card key={project.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-semibold text-gray-900">{project.title}</h3>
                              <Badge className={getStatusColor(project.status)}>
                                {project.status}
                              </Badge>
                              <Badge variant="outline">{project.project_type}</Badge>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                              <span className="flex items-center gap-1">
                                <Building className="h-3 w-3" />
                                {project.company}
                              </span>
                              {project.location && (
                                <span className="flex items-center gap-1">
                                  <MapPin className="h-3 w-3" />
                                  {project.location}
                                </span>
                              )}
                              {project.duration && (
                                <span className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  {project.duration}
                                </span>
                              )}
                              {project.remote_option && (
                                <Badge variant="outline" className="text-xs">Remote</Badge>
                              )}
                            </div>
                            <p className="text-gray-700 mb-3 line-clamp-2">{project.description}</p>
                            {project.skills_required && project.skills_required.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {project.skills_required.slice(0, 4).map((skill, index) => (
                                  <Badge key={index} variant="outline" className="text-xs">
                                    {skill}
                                  </Badge>
                                ))}
                                {project.skills_required.length > 4 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{project.skills_required.length - 4} more
                                  </Badge>
                                )}
                              </div>
                            )}
                          </div>
                          
                          <div className="flex flex-col gap-2 ml-6">
                            <Button size="sm" variant="outline" onClick={() => startEditing(project)}>
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="text-red-600 hover:text-red-700"
                              onClick={() => handleDeleteProject(project.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </TabsContent>

            {/* Browse All Projects Tab */}
            <TabsContent value="browse" className="space-y-6">
              {/* Search and Filters */}
              <Card>
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                      <Input
                        placeholder="Search projects..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>

                    <Select value={selectedType} onValueChange={setSelectedType}>
                      <SelectTrigger>
                        <SelectValue placeholder="Project Type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="development">Development</SelectItem>
                        <SelectItem value="content">Content Creation</SelectItem>
                        <SelectItem value="consulting">Consulting</SelectItem>
                        <SelectItem value="training">Training</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                      <SelectTrigger>
                        <SelectValue placeholder="Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="open">Open</SelectItem>
                        <SelectItem value="in_progress">In Progress</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                      </SelectContent>
                    </Select>

                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="remote-filter"
                        checked={remoteOnly}
                        onCheckedChange={(checked) => setRemoteOnly(checked === true)}
                      />
                      <label htmlFor="remote-filter" className="text-sm font-medium">
                        Remote Only
                      </label>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Projects Grid */}
              {filteredProjects.length === 0 ? (
                <div className="text-center py-12">
                  <FolderOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
                  <p className="text-gray-600">Try adjusting your search criteria</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredProjects.map((project) => (
                    <Card key={project.id} className="hover:shadow-lg transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                              <FolderOpen className="h-5 w-5 text-blue-600" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-gray-900 line-clamp-1">
                                {project.title}
                              </h3>
                              <p className="text-sm text-gray-600">{project.company}</p>
                            </div>
                          </div>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                            {project.status}
                          </span>
                        </div>

                        <p className="text-gray-700 text-sm mb-4 line-clamp-3">
                          {project.description}
                        </p>

                        <div className="space-y-2 mb-4">
                          <div className="flex items-center text-xs text-gray-500">
                            <Calendar className="h-3 w-3 mr-1" />
                            {formatDate(project.created_at)}
                          </div>
                          {project.duration && (
                            <div className="flex items-center text-xs text-gray-500">
                              <Clock className="h-3 w-3 mr-1" />
                              {formatDuration(project.duration)}
                            </div>
                          )}
                          {project.location && (
                            <div className="flex items-center text-xs text-gray-500">
                              <MapPin className="h-3 w-3 mr-1" />
                              {project.location}
                            </div>
                          )}
                        </div>

                        {project.skills_required && project.skills_required.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-4">
                            {project.skills_required.slice(0, 3).map((skill, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {skill}
                              </Badge>
                            ))}
                            {project.skills_required.length > 3 && (
                              <Badge variant="outline" className="text-xs">
                                +{project.skills_required.length - 3} more
                              </Badge>
                            )}
                          </div>
                        )}

                        <Button className="w-full" size="sm">
                          View Details
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        ) : (
          // Candidate View (Original functionality)
          <>
            {/* Search and Filters */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search projects..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>

                <Select value={selectedType} onValueChange={setSelectedType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Project Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="development">Development</SelectItem>
                    <SelectItem value="content">Content Creation</SelectItem>
                    <SelectItem value="consulting">Consulting</SelectItem>
                    <SelectItem value="training">Training</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                  <SelectTrigger>
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="open">Open</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                  </SelectContent>
                </Select>

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

              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  {filteredProjects.length} project{filteredProjects.length !== 1 ? 's' : ''} found
                </p>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  More Filters
                </Button>
              </div>
            </div>

            {/* Projects Grid */}
            {filteredProjects.length === 0 ? (
              <div className="text-center py-12">
                <FolderOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
                <p className="text-gray-600">Try adjusting your search criteria</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredProjects.map((project) => (
                  <Card key={project.id} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                            <FolderOpen className="h-5 w-5 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 line-clamp-1">
                              {project.title}
                            </h3>
                            <p className="text-sm text-gray-600">{project.company}</p>
                          </div>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                          {project.status}
                        </span>
                      </div>

                      <p className="text-gray-700 text-sm mb-4 line-clamp-3">
                        {project.description}
                      </p>

                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-xs text-gray-500">
                          <Calendar className="h-3 w-3 mr-1" />
                          {formatDate(project.created_at)}
                        </div>
                        {project.duration && (
                          <div className="flex items-center text-xs text-gray-500">
                            <Clock className="h-3 w-3 mr-1" />
                            {formatDuration(project.duration)}
                          </div>
                        )}
                        {project.location && (
                          <div className="flex items-center text-xs text-gray-500">
                            <MapPin className="h-3 w-3 mr-1" />
                            {project.location}
                          </div>
                        )}
                      </div>

                      {project.skills_required && project.skills_required.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-4">
                          {project.skills_required.slice(0, 3).map((skill, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                          {project.skills_required.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{project.skills_required.length - 3} more
                            </Badge>
                          )}
                        </div>
                      )}

                      <Button className="w-full" size="sm">
                        View Details
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
} 