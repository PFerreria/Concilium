import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import List, Dict, Any, Optional
import logging
import json
import re

from app.config import settings
from app.models.schemas import WorkflowStep, TranscriptionResult

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI analysis service using Llama model"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.device = settings.llm_device
        self._load_model()
    
    def _load_model(self):
        try:
            logger.info(f"Loading Llama model: {settings.llm_model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.llm_model_name,
                trust_remote_code=True
            )
            
            # Load model with optimizations
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.llm_model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                do_sample=True,
                top_p=0.95
            )
            
            logger.info("Llama model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Llama model: {e}")
            raise
    
    async def extract_workflow_from_text(
        self,
        text: str,
        context: Optional[str] = None
    ) -> List[WorkflowStep]:
        """
            logger.info("Extracting workflow from text")
            
            # Create prompt for workflow extraction
            prompt = self._create_workflow_extraction_prompt(text, context)
            
            # Generate response
            response = self.pipeline(
                prompt,
                max_new_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature
            )
            
            # Extract generated text
            generated_text = response[0]['generated_text']
            
            # Parse workflow steps from response
            workflow_steps = self._parse_workflow_response(generated_text)
            
            logger.info(f"Extracted {len(workflow_steps)} workflow steps")
            return workflow_steps
            
        except Exception as e:
            logger.error(f"Workflow extraction failed: {e}")
            raise
    
    def _create_workflow_extraction_prompt(
        self,
        text: str,
        context: Optional[str] = None
    ) -> str:
        """Create prompt for workflow extraction"""
        
        system_prompt = """You are an expert business process analyst. Your task is to analyze text and extract workflow steps in a structured format.

For each workflow step, identify:
1. Step name (concise title)
2. Description (what happens in this step)
3. Step type (task, decision, event, or gateway)
4. Next steps (which steps follow this one)

Return the workflow as a JSON array of steps."""
        
        user_prompt = f"""Analyze the following text and extract the workflow steps:

{text}

{"Additional context: " + context if context else ""}

Return a JSON array of workflow steps with this structure:
[
  {{
    "step_id": "step_1",
    "name": "Step Name",
    "description": "What happens in this step",
    "step_type": "task",
    "next_steps": ["step_2"]
  }}
]"""
        
        # Format for Llama chat template
        full_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{user_prompt} [/INST]"
        
        return full_prompt
    
    def _parse_workflow_response(self, response: str) -> List[WorkflowStep]:
        """Parse workflow steps from AI response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in response, creating default workflow")
                return self._create_default_workflow()
            
            json_str = json_match.group(0)
            steps_data = json.loads(json_str)
            
            # Convert to WorkflowStep objects
            workflow_steps = []
            for step_data in steps_data:
                step = WorkflowStep(
                    step_id=step_data.get('step_id', f'step_{len(workflow_steps) + 1}'),
                    name=step_data.get('name', 'Unnamed Step'),
                    description=step_data.get('description', ''),
                    step_type=step_data.get('step_type', 'task'),
                    next_steps=step_data.get('next_steps', []),
                    metadata=step_data.get('metadata', {})
                )
                workflow_steps.append(step)
            
            return workflow_steps
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return self._create_default_workflow()
    
    def _create_default_workflow(self) -> List[WorkflowStep]:
        """Create a default workflow when extraction fails"""
        return [
            WorkflowStep(
                step_id="step_1",
                name="Start",
                description="Process initiation",
                step_type="event",
                next_steps=["step_2"]
            ),
            WorkflowStep(
                step_id="step_2",
                name="Analysis Required",
                description="Manual analysis needed - automatic extraction failed",
                step_type="task",
                next_steps=["step_3"]
            ),
            WorkflowStep(
                step_id="step_3",
                name="End",
                description="Process completion",
                step_type="event",
                next_steps=[]
            )
        ]
    
    async def extract_template_data(
        self,
        text: str,
        template_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Extract data to fill template fields from text
        
        Args:
            text: Source text (transcript or document)
            template_fields: List of field names to extract
        
        Returns:
            Dictionary mapping field names to extracted values
        """
        try:
            logger.info(f"Extracting data for {len(template_fields)} template fields")
            
            # Create prompt for data extraction
            prompt = self._create_extraction_prompt(text, template_fields)
            
            # Generate response
            response = self.pipeline(
                prompt,
                max_new_tokens=settings.llm_max_tokens,
                temperature=0.3  # Lower temperature for more precise extraction
            )
            
            # Extract generated text
            generated_text = response[0]['generated_text']
            
            # Parse extracted data
            extracted_data = self._parse_extraction_response(generated_text, template_fields)
            
            logger.info(f"Extracted data for {len(extracted_data)} fields")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Template data extraction failed: {e}")
            raise
    
    def _create_extraction_prompt(
        self,
        text: str,
        fields: List[str]
    ) -> str:
        """Create prompt for template data extraction"""
        
        system_prompt = """You are a data extraction expert. Extract specific information from text to fill template fields."""
        
        fields_list = "\n".join([f"- {field}" for field in fields])
        
        user_prompt = f"""Extract the following information from the text:

Fields to extract:
{fields_list}

Text:
{text}

Return a JSON object with the extracted values:
{{
  "field_name": "extracted value"
}}"""
        
        full_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{user_prompt} [/INST]"
        
        return full_prompt
    
    def _parse_extraction_response(
        self,
        response: str,
        expected_fields: List[str]
    ) -> Dict[str, Any]:
        """Parse extracted data from AI response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in extraction response")
                return {field: "" for field in expected_fields}
            
            json_str = json_match.group(0)
            extracted_data = json.loads(json_str)
            
            # Ensure all expected fields are present
            for field in expected_fields:
                if field not in extracted_data:
                    extracted_data[field] = ""
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction response: {e}")
            return {field: "" for field in expected_fields}
    
    def is_ready(self) -> bool:
        """Check if the AI analyzer is ready"""
        return self.model is not None and self.tokenizer is not None


# Global instance
ai_analyzer = AIAnalyzer()
