/**
 * ProjectCard Component
 * Displays individual project information in a card format
 */

import { ProjectListItem } from '@/lib/api/projects';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, Folder } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface ProjectCardProps {
  project: ProjectListItem;
  onOpen: (projectId: number) => void;
  onDelete?: (projectId: number) => void;
}

const STATUS_COLORS = {
  draft: 'bg-gray-500',
  active: 'bg-blue-500',
  completed: 'bg-green-500',
  archived: 'bg-gray-400',
} as const;

const STATUS_LABELS = {
  draft: 'Draft',
  active: 'Active',
  completed: 'Completed',
  archived: 'Archived',
} as const;

export function ProjectCard({ project, onOpen, onDelete }: ProjectCardProps) {
  const handleOpen = () => {
    onOpen(project.id);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete && confirm('Are you sure you want to delete this project?')) {
      onDelete(project.id);
    }
  };

  const getStatusColor = (status: string) => {
    return STATUS_COLORS[status as keyof typeof STATUS_COLORS] || 'bg-gray-500';
  };

  const getStatusLabel = (status: string) => {
    return STATUS_LABELS[status as keyof typeof STATUS_LABELS] || status;
  };

  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer group" onClick={handleOpen}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/20">
              <Folder className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-lg truncate">{project.name}</CardTitle>
              <CardDescription className="mt-1 line-clamp-2">
                {project.description || 'No description provided'}
              </CardDescription>
            </div>
          </div>
          <Badge className={`${getStatusColor(project.status)} text-white`}>
            {getStatusLabel(project.status)}
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            <span>
              Created {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground mt-2">
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>
              Updated {formatDistanceToNow(new Date(project.updated_at), { addSuffix: true })}
            </span>
          </div>
        </div>
      </CardContent>

      <CardFooter className="flex justify-between">
        <Button variant="outline" size="sm" onClick={handleOpen}>
          Open Project
        </Button>
        {onDelete && (
          <Button
            variant="ghost"
            size="sm"
            className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
            onClick={handleDelete}
          >
            Delete
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
