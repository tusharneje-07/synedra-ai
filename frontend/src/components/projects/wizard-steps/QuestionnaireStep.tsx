/**
 * QuestionnaireStep - Step 2 of project creation wizard
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, ArrowRight, Loader2, Clock } from 'lucide-react';
import type { Questionnaire, QuestionnaireSection, Question } from '@/lib/api/projects';

interface QuestionnaireStepProps {
  questionnaire: Questionnaire;
  initialResponses: Record<string, any>;
  onNext: (responses: Record<string, any>) => void;
  onBack: () => void;
  isLoading: boolean;
}

export function QuestionnaireStep({
  questionnaire,
  initialResponses,
  onNext,
  onBack,
  isLoading,
}: QuestionnaireStepProps) {
  const [responses, setResponses] = useState<Record<string, any>>(initialResponses);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (questionId: string, value: any) => {
    setResponses((prev) => ({ ...prev, [questionId]: value }));
    if (errors[questionId]) {
      setErrors((prev) => ({ ...prev, [questionId]: '' }));
    }
  };

  const handleMultiSelectChange = (questionId: string, option: string, checked: boolean) => {
    const current = responses[questionId] || [];
    const updated = checked
      ? [...current, option]
      : current.filter((item: string) => item !== option);
    handleChange(questionId, updated);
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    questionnaire.sections.forEach((section) => {
      section.questions.forEach((question) => {
        if (question.required && !responses[question.id]) {
          newErrors[question.id] = 'This field is required';
        }
      });
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onNext(responses);
    }
  };

  const renderQuestion = (question: Question) => {
    const value = responses[question.id];
    const error = errors[question.id];

    switch (question.type) {
      case 'text':
        return (
          <Input
            value={value || ''}
            onChange={(e) => handleChange(question.id, e.target.value)}
            placeholder={question.placeholder}
            className={error ? 'border-red-500' : ''}
          />
        );

      case 'textarea':
        return (
          <Textarea
            value={value || ''}
            onChange={(e) => handleChange(question.id, e.target.value)}
            placeholder={question.placeholder}
            rows={3}
            className={error ? 'border-red-500' : ''}
          />
        );

      case 'select':
        return (
          <Select value={value || ''} onValueChange={(val) => handleChange(question.id, val)}>
            <SelectTrigger className={error ? 'border-red-500' : ''}>
              <SelectValue placeholder="Select an option..." />
            </SelectTrigger>
            <SelectContent>
              {question.options?.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      case 'multi-select':
        return (
          <div className="space-y-2">
            {question.options?.map((option) => (
              <div key={option} className="flex items-center space-x-2">
                <Checkbox
                  id={`${question.id}-${option}`}
                  checked={(value || []).includes(option)}
                  onCheckedChange={(checked) =>
                    handleMultiSelectChange(question.id, option, checked as boolean)
                  }
                />
                <label
                  htmlFor={`${question.id}-${option}`}
                  className="text-sm cursor-pointer"
                >
                  {option}
                </label>
              </div>
            ))}
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Header Info */}
      <div className="flex items-center justify-between pb-4 border-b">
        <div>
          <h3 className="font-semibold text-lg">{questionnaire.project_name}</h3>
          <p className="text-sm text-muted-foreground">
            {questionnaire.metadata.total_questions} questions across {questionnaire.metadata.total_sections} sections
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Clock className="h-4 w-4" />
          <span>~{questionnaire.metadata.estimated_time_minutes} min</span>
        </div>
      </div>

      {/* Sections and Questions */}
      {questionnaire.sections.map((section, sectionIndex) => (
        <div key={section.id} className="space-y-4">
          <div>
            <h4 className="font-semibold text-base flex items-center gap-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/20 text-blue-600 text-sm">
                {sectionIndex + 1}
              </span>
              {section.title}
            </h4>
            <p className="text-sm text-muted-foreground mt-1 ml-8">{section.description}</p>
          </div>

          <div className="space-y-4 ml-8">
            {section.questions.map((question) => (
              <div key={question.id} className="space-y-2">
                <Label htmlFor={question.id}>
                  {question.question}
                  {question.required && <span className="text-red-500 ml-1">*</span>}
                </Label>
                {renderQuestion(question)}
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Actions */}
      <div className="flex justify-between pt-4 border-t">
        <Button type="button" variant="outline" onClick={onBack} disabled={isLoading}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <Button type="submit" size="lg" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating Project...
            </>
          ) : (
            <>
              Create Project
              <ArrowRight className="ml-2 h-4 w-4" />
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
