/**
 * CreateProjectWizard Component
 * Multi-step wizard for creating new marketing projects
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateProject, useGenerateQuestionnaire, useUpdateQuestionnaire } from '@/hooks/useProjects';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, ArrowRight, Check, Loader2 } from 'lucide-react';
import { BasicInfoStep } from './wizard-steps/BasicInfoStep';
import { QuestionnaireStep } from './wizard-steps/QuestionnaireStep';
import { ReviewStep } from './wizard-steps/ReviewStep';
import type { Questionnaire } from '@/lib/api/projects';

interface CreateProjectWizardProps {
  open: boolean;
  onClose: () => void;
  brandConfigId: number;
}

type WizardStep = 'basic' | 'questionnaire' | 'review';

interface BasicInfo {
  name: string;
  description: string;
  post_topic: string;
  product_details: Record<string, any>;
  target_details: Record<string, any>;
}

export function CreateProjectWizard({ open, onClose, brandConfigId }: CreateProjectWizardProps) {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<WizardStep>('basic');
  const [basicInfo, setBasicInfo] = useState<BasicInfo>({
    name: '',
    description: '',
    post_topic: '',
    product_details: {},
    target_details: {},
  });
  const [questionnaire, setQuestionnaire] = useState<Questionnaire | null>(null);
  const [questionnaireResponses, setQuestionnaireResponses] = useState<Record<string, any>>({});
  const [createdProjectId, setCreatedProjectId] = useState<number | null>(null);

  const createProjectMutation = useCreateProject();
  const generateQuestionnaireMutation = useGenerateQuestionnaire();
  const updateQuestionnaireMutation = useUpdateQuestionnaire();

  const steps: { id: WizardStep; label: string; number: number }[] = [
    { id: 'basic', label: 'Basic Info', number: 1 },
    { id: 'questionnaire', label: 'Questionnaire', number: 2 },
    { id: 'review', label: 'Review', number: 3 },
  ];

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);
  const progress = ((currentStepIndex + 1) / steps.length) * 100;

  const handleBasicInfoComplete = async (data: BasicInfo) => {
    setBasicInfo(data);
    
    // Generate questionnaire based on basic info
    try {
      const generatedQuestionnaire = await generateQuestionnaireMutation.mutateAsync({
        project_name: data.name,
        description: data.description,
        product_details: data.product_details,
        target_details: data.target_details,
      });
      
      setQuestionnaire(generatedQuestionnaire);
      setCurrentStep('questionnaire');
    } catch (error) {
      console.error('Failed to generate questionnaire:', error);
    }
  };

  const handleQuestionnaireComplete = async (responses: Record<string, any>) => {
    setQuestionnaireResponses(responses);
    
    // Create the project
    try {
      const newProject = await createProjectMutation.mutateAsync({
        name: basicInfo.name,
        description: basicInfo.description,
        post_topic: basicInfo.post_topic,
        product_details: basicInfo.product_details,
        target_details: basicInfo.target_details,
        brand_config_id: brandConfigId,
      });
      
      setCreatedProjectId(newProject.id);
      
      // Save questionnaire responses
      await updateQuestionnaireMutation.mutateAsync({
        id: newProject.id,
        data: responses,
      });
      
      setCurrentStep('review');
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const handleFinish = () => {
    if (createdProjectId) {
      navigate(`/project/${createdProjectId}`);
      onClose();
    }
  };

  const handleBack = () => {
    if (currentStep === 'questionnaire') {
      setCurrentStep('basic');
    } else if (currentStep === 'review') {
      setCurrentStep('questionnaire');
    }
  };

  const handleCancel = () => {
    setCurrentStep('basic');
    setBasicInfo({
      name: '',
      description: '',
      post_topic: '',
      product_details: {},
      target_details: {},
    });
    setQuestionnaire(null);
    setQuestionnaireResponses({});
    setCreatedProjectId(null);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={(open) => !open && handleCancel()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">Create New Project</DialogTitle>
        </DialogHeader>

        {/* Progress Bar */}
        <div className="space-y-2">
          <Progress value={progress} className="h-2" />
          <div className="flex justify-between text-sm">
            {steps.map((step) => (
              <div
                key={step.id}
                className={`flex items-center gap-2 ${
                  currentStep === step.id
                    ? 'text-blue-600 font-semibold'
                    : step.number <= currentStepIndex + 1
                    ? 'text-green-600'
                    : 'text-muted-foreground'
                }`}
              >
                <div
                  className={`flex items-center justify-center w-6 h-6 rounded-full border-2 ${
                    step.number < currentStepIndex + 1
                      ? 'bg-green-600 border-green-600'
                      : currentStep === step.id
                      ? 'border-blue-600'
                      : 'border-muted-foreground'
                  }`}
                >
                  {step.number < currentStepIndex + 1 ? (
                    <Check className="h-4 w-4 text-white" />
                  ) : (
                    <span className="text-xs">{step.number}</span>
                  )}
                </div>
                <span>{step.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="py-6">
          {currentStep === 'basic' && (
            <BasicInfoStep
              initialData={basicInfo}
              onNext={handleBasicInfoComplete}
              isLoading={generateQuestionnaireMutation.isPending}
            />
          )}

          {currentStep === 'questionnaire' && questionnaire && (
            <QuestionnaireStep
              questionnaire={questionnaire}
              initialResponses={questionnaireResponses}
              onNext={handleQuestionnaireComplete}
              onBack={handleBack}
              isLoading={createProjectMutation.isPending || updateQuestionnaireMutation.isPending}
            />
          )}

          {currentStep === 'review' && (
            <ReviewStep
              basicInfo={basicInfo}
              responses={questionnaireResponses}
              questionnaire={questionnaire}
              onFinish={handleFinish}
              onBack={handleBack}
            />
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex justify-between items-center pt-4 border-t">
          <Button variant="outline" onClick={handleCancel}>
            Cancel
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
