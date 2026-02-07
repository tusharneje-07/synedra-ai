/**
 * Index Page - Landing page showing project list
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ProjectList, CreateProjectWizard } from '@/components/projects';
import ThemeToggle from '@/components/dashboard/ThemeToggle';

const Index = () => {
  const navigate = useNavigate();
  const [showCreateWizard, setShowCreateWizard] = useState(false);

  const handleCreateNew = () => {
    setShowCreateWizard(true);
  };

  const handleOpenProject = (projectId: number) => {
    navigate(`/project/${projectId}`);
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 flex items-center justify-between px-6 py-3 bg-card shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
        <div className="flex items-center gap-3">
          <h1 className="text-base font-bold tracking-tight text-foreground">
            AI Marketing Council
          </h1>
          <span className="text-[10px] uppercase tracking-widest text-muted-foreground bg-muted rounded-full px-2.5 py-0.5 font-medium">
            Projects
          </span>
        </div>
        <ThemeToggle />
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <ProjectList 
          onCreateNew={handleCreateNew}
          onOpenProject={handleOpenProject}
        />
      </main>

      {/* Create Project Wizard */}
      <CreateProjectWizard
        open={showCreateWizard}
        onClose={() => setShowCreateWizard(false)}
        brandConfigId={1} // Using TechVision brand config
      />
    </div>
  );
};

export default Index;
