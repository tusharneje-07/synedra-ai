/**
 * ProjectList Component
 * Main landing page showing all projects or prompt to create new one
 */

import { useState } from 'react';
import { useProjects, useDeleteProject } from '@/hooks/useProjects';
import { ProjectCard } from './ProjectCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Search, Filter, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface ProjectListProps {
  onCreateNew: () => void;
  onOpenProject: (projectId: number) => void;
}

export function ProjectList({ onCreateNew, onOpenProject }: ProjectListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Fetch projects
  const { data: projects, isLoading, error } = useProjects({
    status: statusFilter !== 'all' ? statusFilter : undefined,
  });

  const deleteProjectMutation = useDeleteProject();

  const handleDelete = (projectId: number) => {
    deleteProjectMutation.mutate(projectId);
  };

  // Filter projects by search query
  const filteredProjects = projects?.filter((project) => {
    const matchesSearch = searchQuery
      ? project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.description?.toLowerCase().includes(searchQuery.toLowerCase())
      : true;
    return matchesSearch;
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-muted-foreground">Loading projects...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-red-600 font-semibold mb-2">Error loading projects</p>
              <p className="text-sm text-muted-foreground">
                {error instanceof Error ? error.message : 'An unexpected error occurred'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Empty state - no projects
  if (!projects || projects.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="max-w-md w-full text-center">
          <div className="mb-8">
            <div className="mx-auto w-24 h-24 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center mb-4">
              <Plus className="h-12 w-12 text-blue-600 dark:text-blue-400" />
            </div>
            <h2 className="text-2xl font-bold mb-2">No Projects Yet</h2>
            <p className="text-muted-foreground mb-6">
              Get started by creating your first marketing project. Our AI council will help you craft the perfect campaign.
            </p>
          </div>
          <Button size="lg" onClick={onCreateNew} className="w-full sm:w-auto">
            <Plus className="mr-2 h-5 w-5" />
            Create Your First Project
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Your Projects</h1>
            <p className="text-muted-foreground mt-1">
              Manage your marketing campaigns and initiatives
            </p>
          </div>
          <Button onClick={onCreateNew} size="lg">
            <Plus className="mr-2 h-5 w-5" />
            New Project
          </Button>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <div className="sm:w-48">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="archived">Archived</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Project Grid */}
      {filteredProjects && filteredProjects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onOpen={onOpenProject}
              onDelete={handleDelete}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">
              No projects found matching your filters. Try adjusting your search or filters.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Stats Footer */}
      {filteredProjects && filteredProjects.length > 0 && (
        <div className="mt-8 text-center text-sm text-muted-foreground">
          Showing {filteredProjects.length} of {projects.length} project{projects.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
}
