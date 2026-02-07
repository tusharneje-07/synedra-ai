/**
 * React Query hooks for project management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi, CreateProjectData, UpdateProjectData } from '@/lib/api/projects';
import { toast } from 'sonner';

/**
 * Query key factory for projects
 */
export const projectKeys = {
  all: ['projects'] as const,
  lists: () => [...projectKeys.all, 'list'] as const,
  list: (filters?: Record<string, any>) => [...projectKeys.lists(), filters] as const,
  details: () => [...projectKeys.all, 'detail'] as const,
  detail: (id: number) => [...projectKeys.details(), id] as const,
  sessions: (id: number) => [...projectKeys.detail(id), 'sessions'] as const,
  messages: (id: number, sessionId?: string) => 
    [...projectKeys.detail(id), 'messages', sessionId] as const,
};

/**
 * Hook to fetch all projects
 */
export function useProjects(params?: {
  brand_config_id?: number;
  status?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: projectKeys.list(params),
    queryFn: () => projectsApi.list(params),
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Hook to fetch a single project
 */
export function useProject(projectId: number | null) {
  return useQuery({
    queryKey: projectKeys.detail(projectId!),
    queryFn: () => projectsApi.get(projectId!),
    enabled: projectId !== null,
    staleTime: 30000,
  });
}

/**
 * Hook to create a new project
 */
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProjectData) => projectsApi.create(data),
    onSuccess: (newProject) => {
      // Invalidate and refetch projects list
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      toast.success('Project created successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create project');
    },
  });
}

/**
 * Hook to update a project
 */
export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateProjectData }) =>
      projectsApi.update(id, data),
    onSuccess: (updatedProject) => {
      // Invalidate specific project and lists
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(updatedProject.id) });
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      toast.success('Project updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update project');
    },
  });
}

/**
 * Hook to update project questionnaire
 */
export function useUpdateQuestionnaire() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Record<string, any> }) =>
      projectsApi.updateQuestionnaire(id, data),
    onSuccess: (updatedProject) => {
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(updatedProject.id) });
      toast.success('Questionnaire saved successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to save questionnaire');
    },
  });
}

/**
 * Hook to delete a project
 */
export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (projectId: number) => projectsApi.delete(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      toast.success('Project deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete project');
    },
  });
}

/**
 * Hook to generate questionnaire
 */
export function useGenerateQuestionnaire() {
  return useMutation({
    mutationFn: (params: {
      project_name: string;
      description?: string;
      product_details?: Record<string, any>;
      target_details?: Record<string, any>;
    }) => projectsApi.generateQuestionnaire(params),
    onError: (error: any) => {
      toast.error(error.message || 'Failed to generate questionnaire');
    },
  });
}

/**
 * Hook to fetch project sessions
 */
export function useProjectSessions(projectId: number | null, limit = 10) {
  return useQuery({
    queryKey: projectKeys.sessions(projectId!),
    queryFn: () => projectsApi.getSessions(projectId!, limit),
    enabled: projectId !== null,
    staleTime: 10000,
  });
}

/**
 * Hook to fetch project messages
 */
export function useProjectMessages(
  projectId: number | null,
  sessionId?: string,
  limit = 100
) {
  return useQuery({
    queryKey: projectKeys.messages(projectId!, sessionId),
    queryFn: () => projectsApi.getMessages(projectId!, sessionId, limit),
    enabled: projectId !== null,
    staleTime: 5000,
  });
}
