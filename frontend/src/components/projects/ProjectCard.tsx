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
    <Card className="hover:shadow-lg transition-shadow cursor-pointer group h-full flex flex-col" onClick={handleOpen}>
      <CardHeader className="pb-3">
        <div className="flex items-start gap-3 mb-3">
          <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/20 shrink-0">
            <Folder className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-2">
              <CardTitle className="text-lg leading-tight break-words pr-2">
                {project.name}
              </CardTitle>
              <Badge className={`${getStatusColor(project.status)} text-white shrink-0 text-xs`}>
                {getStatusLabel(project.status)}
              </Badge>
            </div>
            <CardDescription className="mt-1 line-clamp-2 text-sm">
              {project.description || 'No description provided'}
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0 pb-3 flex-1">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">
              Created {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Clock className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">
              Updated {formatDistanceToNow(new Date(project.updated_at), { addSuffix: true })}
            </span>
          </div>
        </div>
      </CardContent>

      <CardFooter className="flex justify-between gap-2 pt-3">
        <Button variant="outline" size="sm" onClick={handleOpen} className="flex-1">
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
