/**
 * BasicInfoStep - Step 1 of project creation wizard
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ArrowRight, Loader2 } from 'lucide-react';

interface BasicInfo {
  name: string;
  description: string;
  post_topic: string;
  product_details: Record<string, any>;
  target_details: Record<string, any>;
}

interface BasicInfoStepProps {
  initialData: BasicInfo;
  onNext: (data: BasicInfo) => void;
  isLoading: boolean;
}

export function BasicInfoStep({ initialData, onNext, isLoading }: BasicInfoStepProps) {
  const [formData, setFormData] = useState(initialData);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (field: keyof BasicInfo, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Project name is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validate()) {
      // Parse product and target details from description
      const productDetails = {
        description: formData.description,
        topic: formData.post_topic,
      };

      const targetDetails = {
        description: formData.description,
      };

      onNext({
        ...formData,
        product_details: productDetails,
        target_details: targetDetails,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">
          Project Name <span className="text-red-500">*</span>
        </Label>
        <Input
          id="name"
          placeholder="e.g., Q1 2025 Product Launch Campaign"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          className={errors.name ? 'border-red-500' : ''}
        />
        {errors.name && <p className="text-sm text-red-500">{errors.name}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">
          Project Description <span className="text-red-500">*</span>
        </Label>
        <Textarea
          id="description"
          placeholder="Describe your marketing project, the product/service you're promoting, and your target audience..."
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          rows={5}
          className={errors.description ? 'border-red-500' : ''}
        />
        {errors.description && <p className="text-sm text-red-500">{errors.description}</p>}
        <p className="text-sm text-muted-foreground">
          Provide detailed information about your campaign goals, target market, and what makes your offering unique.
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="post_topic">Campaign Topic (Optional)</Label>
        <Input
          id="post_topic"
          placeholder="e.g., AI-Powered Analytics Launch"
          value={formData.post_topic}
          onChange={(e) => handleChange('post_topic', e.target.value)}
        />
        <p className="text-sm text-muted-foreground">
          Main theme or focus of your marketing campaign
        </p>
      </div>

      <div className="flex justify-end pt-4">
        <Button type="submit" size="lg" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Generating Questions...
            </>
          ) : (
            <>
              Next: Answer Questions
              <ArrowRight className="ml-2 h-4 w-4" />
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
