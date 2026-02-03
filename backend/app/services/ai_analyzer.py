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
        # Check if CUDA is actually available
        if settings.llm_device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested for Llama but not available. Falling back to CPU.")
            self.device = "cpu"
        else:
            self.device = settings.llm_device
        # Don't load model on init to allow for authentication first
    
    def initialize(self):
        """Initialize models after authentication"""
        if self.model is None:
            self._load_model()
            
    def _load_model(self):
        try:
            logger.info(f"Loading Llama model: {settings.llm_model_name}")
            
            # Load tokenizer with token
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.llm_model_name,
                token=settings.hf_token,
                trust_remote_code=True
            )
            
            # Load model with optimizations and token
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.llm_model_name,
                token=settings.hf_token,
                torch_dtype=torch.float16, # Use half-precision to save 50% RAM
                device_map=None, # Disable auto mapping for CPU stability
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            if self.device != "cpu":
                self.model = self.model.to(self.device)
            
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
        Extract workflow steps from text using AI analysis
        """
        self.initialize()
        try:
            logger.info("Extracting workflow from text")
            logger.debug(f"Input text: {text[:500]}...") # Log start of input
            
            # Create prompt for workflow extraction
            prompt = self._create_workflow_extraction_prompt(text, context)
            
            # Generate response
            response = self.pipeline(
                prompt,
                max_new_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                return_full_text=False
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
        
        system_prompt = """You are an expert BPMN process analyst. Your task is to extract a sequential workflow from a transcription.

CRITICAL RULES FOR EXTRACTION:
1. **IDs**: Must be short, unique, `snake_case`, and NO spaces (e.g., `fill_form`, `find_client`). NEVER use full sentences as IDs.
2. **Step Types**:
   - `task`: Default for any action (e.g., "fill document", "find client").
   - `gateway`: ONLY for explicit decisions (e.g., "If correct then A, else B"). Do NOT use gateways for simple sequence.
   - `event`: Only for Start/End.
3. **Sequence**: Ensure the `next_steps` create a logical flow.

JSON Schema:
{
  "step_id": "string (snake_case_id, max 3 words)",
  "name": "string (Human readable name)",
  "description": "string (Brief description)",
  "step_type": "string (task, gateway, event)",
  "next_steps": ["string (ID of the next step)"]
}"""
        
        user_prompt = f"""TRANSCRIPT:
"{text}"

{"Additional context: " + context if context else ""}

Analyze the transcript above and extract the workflow steps as a JSON array."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    
    def _parse_workflow_response(self, response: str) -> List[WorkflowStep]:
        """Parse workflow steps from AI response"""
        try:
            logger.debug(f"Raw AI response: {response}")
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if not json_match:
                logger.warning("No JSON array found in response, creating default workflow")
                return self._create_default_workflow()
            
            json_str = json_match.group(0)
            
            # Robust JSON parsing
            try:
                steps_data = json.loads(json_str)
            except json.JSONDecodeError:
                # Try to find the first valid JSON array
                start_ptr = json_str.find('[')
                if start_ptr != -1:
                    try:
                        decoder = json.JSONDecoder()
                        steps_data, _ = decoder.raw_decode(json_str[start_ptr:])
                    except Exception as e:
                        logger.error(f"Failed to parse JSON using raw_decode: {e}")
                        return self._create_default_workflow()
                else:
                    return self._create_default_workflow()
            
            logger.debug(f"Parsed JSON type: {type(steps_data)}")
            
            # Handle if the model returned a dict wrapping the array (e.g. {"steps": [...]})
            if isinstance(steps_data, dict):
                logger.warning("Model returned a Dict instead of List. Searching for array.")
                # Look for the first list value
                found_list = False
                for key, value in steps_data.items():
                    if isinstance(value, list):
                        steps_data = value
                        found_list = True
                        break
                if not found_list:
                    logger.error("Could not find a list in the returned dictionary.")
                    return self._create_default_workflow()

            if not isinstance(steps_data, list):
                logger.error(f"Parsed data is not a list: {type(steps_data)}")
                return self._create_default_workflow()

            # Convert to WorkflowStep objects
            workflow_steps = []
            for step_data in steps_data:
                if isinstance(step_data, str):
                    logger.warning(f"Skipping string step data: {step_data}")
                    continue
                    
                workflow_steps.append(WorkflowStep(
                    step_id=step_data.get('step_id', f'step_{len(workflow_steps) + 1}'),
                    name=step_data.get('name', 'Unnamed Step'),
                    description=step_data.get('description', ''),
                    step_type=step_data.get('step_type', 'task'),
                    next_steps=step_data.get('next_steps', []),
                    metadata=step_data.get('metadata', {})
                ))
            
            return workflow_steps
            
        except Exception as e:
            logger.error(f"Failed to parse workflow response: {e}")
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
        self.initialize()
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
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    
    def _parse_extraction_response(
        self,
        response: str,
        expected_fields: List[str]
    ) -> Dict[str, Any]:
        """Parse extracted data from AI response"""
        try:
            logger.debug(f"Raw AI extraction response: {response}")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                logger.warning("No JSON object found in extraction response")
                return {field: "" for field in expected_fields}
            
            json_str = json_match.group(0)
            
            # Robust JSON parsing
            try:
                extracted_data = json.loads(json_str)
            except json.JSONDecodeError:
                start_ptr = json_str.find('{')
                if start_ptr != -1:
                    try:
                        decoder = json.JSONDecoder()
                        extracted_data, _ = decoder.raw_decode(json_str[start_ptr:])
                    except Exception as e:
                        logger.error(f"Failed to parse extraction JSON using raw_decode: {e}")
                        return {field: "" for field in expected_fields}
                else:
                    return {field: "" for field in expected_fields}
            
            # Ensure all expected fields are present
            for field in expected_fields:
                if field not in extracted_data:
                    extracted_data[field] = ""
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Failed to parse extraction response: {e}")
            return {field: "" for field in expected_fields}
    
    def is_ready(self) -> bool:
        """Check if the AI analyzer is ready"""
        return self.model is not None and self.tokenizer is not None


# Global instance
ai_analyzer = AIAnalyzer()
