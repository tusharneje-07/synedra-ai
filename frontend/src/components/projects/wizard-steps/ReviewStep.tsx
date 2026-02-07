/**
 * ReviewStep - Final step showing project summary
 */

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, CheckCircle, Rocket } from 'lucide-react';
import type { Questionnaire } from '@/lib/api/projects';

interface BasicInfo {
  name: string;
  description: string;
  post_topic: string;
}

interface ReviewStepProps {
  basicInfo: BasicInfo;
  responses: Record<string, any>;
  questionnaire: Questionnaire | null;
  onFinish: () => void;
  onBack: () => void;
}

export function ReviewStep({ basicInfo, responses, questionnaire, onFinish, onBack }: ReviewStepProps) {
  const formatResponseValue = (value: any): string => {
    if (Array.isArray(value)) {
      return value.join(', ');
    }
    return String(value);
  };

  return (
    <div className="space-y-6">
      {/* Success Message */}
      <div className="flex flex-col items-center text-center py-6">
        <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center mb-4">
          <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
        </div>
        <h3 className="text-2xl font-bold mb-2">Project Created Successfully!</h3>
        <p className="text-muted-foreground">
          Your marketing project is ready. Review the details below and start your campaign.
        </p>
      </div>

      {/* Basic Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Project Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <div className="text-sm font-semibold text-muted-foreground">Name</div>
            <div className="text-base">{basicInfo.name}</div>
          </div>
          <div>
            <div className="text-sm font-semibold text-muted-foreground">Description</div>
            <div className="text-base">{basicInfo.description}</div>
          </div>
          {basicInfo.post_topic && (
            <div>
              <div className="text-sm font-semibold text-muted-foreground">Campaign Topic</div>
              <div className="text-base">{basicInfo.post_topic}</div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Questionnaire Responses Summary */}
      {questionnaire && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Your Responses</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {questionnaire.sections.map((section) => (
                <div key={section.id}>
                  <h4 className="font-semibold text-sm text-muted-foreground mb-2">
                    {section.title}
                  </h4>
                  <div className="space-y-2 ml-4">
                    {section.questions
                      .filter((q) => responses[q.id])
                      .map((question) => (
                        <div key={question.id} className="text-sm">
                          <span className="font-medium">{question.question}:</span>{' '}
                          <span className="text-muted-foreground">
                            {formatResponseValue(responses[question.id])}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Next Steps */}
      <Card className="border-blue-200 dark:border-blue-900 bg-blue-50 dark:bg-blue-950/20">
        <CardContent className="pt-6">
          <h4 className="font-semibold mb-2 flex items-center gap-2">
            <Rocket className="h-5 w-5 text-blue-600" />
            What's Next?
          </h4>
          <ul className="space-y-2 text-sm text-muted-foreground ml-7">
            <li>• Open your project to start the AI marketing council</li>
            <li>• Collaborate with specialized AI agents for campaign strategy</li>
            <li>• Review and refine the AI-generated marketing content</li>
            <li>• Track your campaign progress and results</li>
          </ul>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-between pt-4 border-t">
        <Button variant="outline" onClick={onBack}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <Button size="lg" onClick={onFinish}>
          <Rocket className="mr-2 h-5 w-5" />
          Open Project
        </Button>
      </div>
    </div>
  );
}
