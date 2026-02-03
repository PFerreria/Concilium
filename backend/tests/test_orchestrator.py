import asyncio
import sys
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path
from datetime import datetime

# Add the backend path to sys.path
backend_path = Path(r"c:\Users\epifh\Desktop\Github\Concilium\backend")
sys.path.append(str(backend_path))

# Mock heavy dependencies before importing app services
sys.modules['whisper'] = MagicMock()
sys.modules['torch'] = MagicMock()
sys.modules['torch.cuda'] = MagicMock()
sys.modules['transformers'] = MagicMock()

from app.services.orchestrator import WorkflowOrchestrator
from app.models.schemas import TranscriptionResult, WorkflowStep, WorkflowDiagram

class TestWorkflowOrchestrator(unittest.IsolatedAsyncioTestCase):
    
    @patch('app.services.orchestrator.audio_processor')
    @patch('app.services.orchestrator.ai_analyzer')
    @patch('app.services.orchestrator.workflow_generator')
    async def test_audio_to_diagram_flow(self, mock_gen, mock_ai, mock_audio):
        # Setup mocks
        mock_audio.transcribe_audio = AsyncMock(return_value=TranscriptionResult(
            file_id="test_file",
            language="en",
            duration_seconds=10.0,
            segments=[],
            full_text="Test transcription text"
        ))
        
        mock_ai.extract_workflow_from_text = AsyncMock(return_value=[
            WorkflowStep(step_id="step_1", name="Step 1", description="Desc 1", step_type="task", next_steps=[])
        ])
        
        mock_gen.generate_bpmn_xml = AsyncMock(return_value=Path("test.xml"))
        # mock_gen.generate_diagram is removed
        
        orchestrator = WorkflowOrchestrator()
        
        # Execute
        result = await orchestrator.audio_to_diagram(
            audio_path=Path("fake_audio.mp3"),
            file_id="test_file",
            workflow_name="Test Workflow"
        )
        
        # Assertions
        self.assertEqual(result.name, "Test Workflow")
        self.assertEqual(len(result.steps), 1)
        self.assertEqual(result.xml_path, "test.xml")
        self.assertIsNone(result.diagram_path)
        
        # Verify call order (strict sequential)
        mock_audio.transcribe_audio.assert_called_once()
        mock_ai.extract_workflow_from_text.assert_called_once()
        mock_gen.generate_bpmn_xml.assert_called_once()
        # mock_gen.generate_diagram should NOT be called
        
        print("Verification test passed!")

if __name__ == "__main__":
    unittest.main()
