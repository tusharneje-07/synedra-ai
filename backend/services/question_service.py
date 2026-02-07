"""
AI Question Generation Service - Dynamically creates questionnaires
"""
from typing import List, Dict, Any, Optional
import json


class QuestionGenerationService:
    """Service for generating AI-powered project questionnaires"""
    
    # Question templates based on project type and context
    CORE_QUESTIONS = [
        {
            "id": "primary_goal",
            "question": "What is the primary goal of this marketing campaign?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., Increase brand awareness, drive sales, launch new product"
        },
        {
            "id": "target_audience",
            "question": "Who is your target audience?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., Tech-savvy millennials, B2B decision makers"
        },
        {
            "id": "key_message",
            "question": "What is the key message you want to convey?",
            "type": "textarea",
            "required": True,
            "placeholder": "Describe the main message or value proposition"
        },
        {
            "id": "budget_range",
            "question": "What is your approximate budget range?",
            "type": "select",
            "required": False,
            "options": [
                "Less than $5,000",
                "$5,000 - $10,000",
                "$10,000 - $25,000",
                "$25,000 - $50,000",
                "More than $50,000"
            ]
        },
        {
            "id": "timeline",
            "question": "What is your campaign timeline?",
            "type": "select",
            "required": True,
            "options": [
                "1-2 weeks",
                "3-4 weeks",
                "1-2 months",
                "3-6 months",
                "6+ months"
            ]
        }
    ]
    
    PLATFORM_QUESTIONS = {
        "id": "platforms",
        "question": "Which platforms do you want to target?",
        "type": "multi-select",
        "required": True,
        "options": [
            "LinkedIn",
            "Twitter/X",
            "Facebook",
            "Instagram",
            "TikTok",
            "YouTube",
            "Email",
            "Blog/Website"
        ]
    }
    
    PRODUCT_SPECIFIC_QUESTIONS = [
        {
            "id": "unique_selling_points",
            "question": "What are the unique selling points of your product/service?",
            "type": "textarea",
            "required": True,
            "placeholder": "List key differentiators from competitors"
        },
        {
            "id": "competitor_landscape",
            "question": "Who are your main competitors?",
            "type": "text",
            "required": False,
            "placeholder": "e.g., Company A, Company B"
        },
        {
            "id": "success_metrics",
            "question": "How will you measure success?",
            "type": "multi-select",
            "required": True,
            "options": [
                "Engagement rate",
                "Reach/Impressions",
                "Click-through rate",
                "Conversion rate",
                "Lead generation",
                "Sales revenue",
                "Brand sentiment"
            ]
        }
    ]
    
    TONE_AND_STYLE_QUESTIONS = [
        {
            "id": "brand_voice",
            "question": "What tone should the content have?",
            "type": "multi-select",
            "required": True,
            "options": [
                "Professional",
                "Casual/Friendly",
                "Humorous",
                "Inspirational",
                "Educational",
                "Authoritative"
            ]
        },
        {
            "id": "content_style",
            "question": "What type of content resonates with your audience?",
            "type": "multi-select",
            "required": False,
            "options": [
                "Data-driven insights",
                "Customer stories",
                "How-to guides",
                "Industry news",
                "Behind-the-scenes",
                "Product demos"
            ]
        }
    ]
    
    def generate_questionnaire(
        self,
        project_name: str,
        description: Optional[str] = None,
        product_details: Optional[Dict[str, Any]] = None,
        target_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a dynamic questionnaire based on project information
        
        Args:
            project_name: Name of the project
            description: Project description
            product_details: Details about the product/service
            target_details: Target audience information
            
        Returns:
            Dictionary containing questionnaire sections and questions
        """
        
        questionnaire = {
            "project_name": project_name,
            "sections": []
        }
        
        # Section 1: Campaign Basics
        basic_section = {
            "id": "campaign_basics",
            "title": "Campaign Basics",
            "description": "Let's start with the fundamentals of your campaign",
            "questions": self.CORE_QUESTIONS.copy()
        }
        questionnaire["sections"].append(basic_section)
        
        # Section 2: Platform Strategy
        platform_section = {
            "id": "platform_strategy",
            "title": "Platform Strategy",
            "description": "Where will you reach your audience?",
            "questions": [self.PLATFORM_QUESTIONS]
        }
        questionnaire["sections"].append(platform_section)
        
        # Section 3: Product/Service Details (conditional on product_details)
        if product_details:
            product_section = {
                "id": "product_details",
                "title": "Product/Service Information",
                "description": "Tell us more about what you're promoting",
                "questions": self.PRODUCT_SPECIFIC_QUESTIONS.copy()
            }
            questionnaire["sections"].append(product_section)
        
        # Section 4: Brand Voice & Content
        voice_section = {
            "id": "brand_voice",
            "title": "Brand Voice & Content Style",
            "description": "How should we communicate with your audience?",
            "questions": self.TONE_AND_STYLE_QUESTIONS.copy()
        }
        questionnaire["sections"].append(voice_section)
        
        # Section 5: Additional Context (AI-generated based on input)
        context_questions = self._generate_contextual_questions(
            description,
            product_details,
            target_details
        )
        
        if context_questions:
            context_section = {
                "id": "additional_context",
                "title": "Additional Insights",
                "description": "Help us understand your specific needs",
                "questions": context_questions
            }
            questionnaire["sections"].append(context_section)
        
        # Add metadata
        questionnaire["metadata"] = {
            "total_sections": len(questionnaire["sections"]),
            "total_questions": sum(
                len(section["questions"]) 
                for section in questionnaire["sections"]
            ),
            "estimated_time_minutes": len(questionnaire["sections"]) * 3
        }
        
        return questionnaire
    
    def _generate_contextual_questions(
        self,
        description: Optional[str],
        product_details: Optional[Dict[str, Any]],
        target_details: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate questions based on provided context"""
        
        contextual_questions = []
        
        # If it's a B2B product
        if target_details and "B2B" in str(target_details).upper():
            contextual_questions.append({
                "id": "decision_makers",
                "question": "Who are the key decision-makers in your target organizations?",
                "type": "text",
                "required": False,
                "placeholder": "e.g., CTO, Marketing Director, CEO"
            })
            contextual_questions.append({
                "id": "sales_cycle",
                "question": "What is your typical sales cycle length?",
                "type": "select",
                "required": False,
                "options": [
                    "Less than 1 month",
                    "1-3 months",
                    "3-6 months",
                    "6+ months"
                ]
            })
        
        # If it's tech-related
        if product_details and any(
            tech_word in str(product_details).lower() 
            for tech_word in ["ai", "software", "saas", "tech", "app", "platform"]
        ):
            contextual_questions.append({
                "id": "technical_complexity",
                "question": "How technical should the messaging be?",
                "type": "select",
                "required": False,
                "options": [
                    "Very technical (for engineers/developers)",
                    "Moderately technical (for technical managers)",
                    "Business-focused (for executives)",
                    "Simple/accessible (for general audience)"
                ]
            })
        
        # If targeting specific industries
        if target_details and "industry" in str(target_details).lower():
            contextual_questions.append({
                "id": "industry_regulations",
                "question": "Are there any industry-specific regulations or compliance requirements we should consider?",
                "type": "textarea",
                "required": False,
                "placeholder": "e.g., HIPAA for healthcare, GDPR for EU customers"
            })
        
        # Always ask about existing content
        contextual_questions.append({
            "id": "existing_content",
            "question": "Do you have existing marketing materials or content we should align with?",
            "type": "textarea",
            "required": False,
            "placeholder": "Describe any brand guidelines, previous campaigns, or assets"
        })
        
        return contextual_questions
    
    def validate_responses(
        self,
        questionnaire: Dict[str, Any],
        responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate questionnaire responses
        
        Returns:
            Dictionary with 'valid' bool and 'errors' list
        """
        errors = []
        
        for section in questionnaire.get("sections", []):
            for question in section.get("questions", []):
                question_id = question["id"]
                
                if question.get("required") and question_id not in responses:
                    errors.append({
                        "question_id": question_id,
                        "error": f"Required question '{question['question']}' not answered"
                    })
                
                # Validate select/multi-select options
                if question_id in responses:
                    response_value = responses[question_id]
                    
                    if question["type"] in ["select", "multi-select"]:
                        options = question.get("options", [])
                        if question["type"] == "select":
                            if response_value not in options:
                                errors.append({
                                    "question_id": question_id,
                                    "error": f"Invalid option selected"
                                })
                        elif question["type"] == "multi-select":
                            if not isinstance(response_value, list):
                                errors.append({
                                    "question_id": question_id,
                                    "error": "Multi-select response must be a list"
                                })
                            elif not all(v in options for v in response_value):
                                errors.append({
                                    "question_id": question_id,
                                    "error": "One or more selected options are invalid"
                                })
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
