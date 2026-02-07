/**
 * Dashboard Page - Main workspace for selected project
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '@/hooks/useProjects';
import AgentsGrid from "@/components/dashboard/AgentsGrid";
import PostGenerationBlock from "@/components/dashboard/PostGenerationBlock";
import ChatPanel from "@/components/dashboard/ChatPanel";
import ChatInput from "@/components/dashboard/ChatInput";
import ThemeToggle from "@/components/dashboard/ThemeToggle";
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, Settings } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const Dashboard = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { data: project, isLoading, error } = useProject(projectId ? parseInt(projectId) : null);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-muted-foreground">Loading project...</p>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 font-semibold mb-4">Failed to load project</p>
          <Button onClick={() => navigate('/')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Button>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    const colors = {
      draft: 'bg-gray-500',
      active: 'bg-blue-500',
      completed: 'bg-green-500',
      archived: 'bg-gray-400',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-500';
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-3 bg-card shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Projects
          </Button>
          <div className="h-6 w-px bg-border" />
          <div className="flex items-center gap-3">
            <h1 className="text-base font-bold tracking-tight text-foreground">
              {project.name}
            </h1>
            <Badge className={`${getStatusColor(project.status)} text-white text-xs`}>
              {project.status}
            </Badge>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/setting')}
            className="h-8 w-8 rounded-lg"
          >
            <Settings className="h-4 w-4" />
          </Button>
          <ThemeToggle />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 min-h-0">
        {/* Left Column – 50% */}
        <div className="flex flex-col w-1/2 p-5 gap-5 min-h-0">
          <div className="flex-[0_0_auto]">
            <AgentsGrid />
          </div>
          <div className="flex-1 min-h-0">
            <PostGenerationBlock />
          </div>
        </div>

        {/* Right Column – Chat – 50% */}
        <div className="flex flex-col w-1/2 p-5 pl-0 min-h-0">
          <div className="flex flex-col flex-1 min-h-0 rounded-lg bg-card shadow-[0_1px_3px_rgba(0,0,0,0.05)] p-5">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
              Agent Activity - Project: {project.name}
            </h2>
            <div className="w-full h-px bg-border/60 mb-3" />
            <ChatPanel />
            <ChatInput />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
