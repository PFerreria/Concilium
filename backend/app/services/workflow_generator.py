from lxml import etree
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime
import uuid

from graphviz import Digraph
from app.config import settings
from app.models.schemas import WorkflowStep, WorkflowDiagram

logger = logging.getLogger(__name__)


class WorkflowGenerator:
    """Workflow diagram generation service"""
    
    def __init__(self):
        self.output_dir = settings.workflow_output_dir
        self.diagram_format = settings.diagram_format
    
    async def generate_workflow(
        self,
        steps: List[WorkflowStep],
        name: str,
        description: str = ""
    ) -> WorkflowDiagram:
        try:
            workflow_id = str(uuid.uuid4())
            logger.info(f"Generating workflow: {name} (ID: {workflow_id})")
            
            # Generate BPMN XML
            xml_path = await self._generate_bpmn_xml(
                workflow_id, steps, name, description
            )
            
            # Generate graphical diagram
            diagram_path = await self._generate_diagram(
                workflow_id, steps, name
            )
            
            workflow = WorkflowDiagram(
                workflow_id=workflow_id,
                name=name,
                description=description,
                steps=steps,
                xml_path=str(xml_path),
                diagram_path=str(diagram_path),
                created_at=datetime.now()
            )
            
            logger.info(f"Workflow generated successfully: {workflow_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Workflow generation failed: {e}")
            raise
    
    async def _generate_bpmn_xml(
        self,
        workflow_id: str,
        steps: List[WorkflowStep],
        name: str,
        description: str
    ) -> Path:
        """Generate BPMN 2.0 compliant XML file"""
        
        # Create BPMN namespace
        BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
        BPMNDI_NS = "http://www.omg.org/spec/BPMN/20100524/DI"
        DC_NS = "http://www.omg.org/spec/DD/20100524/DC"
        DI_NS = "http://www.omg.org/spec/DD/20100524/DI"
        
        nsmap = {
            None: BPMN_NS,
            'bpmndi': BPMNDI_NS,
        }
        
        # Create root element
        definitions = etree.Element(
            f"{{{BPMN_NS}}}definitions",
            nsmap=nsmap,
            id=f"definitions_{workflow_id}",
            targetNamespace="http://concilium.ai/workflows"
        )
        
        # Create process element
        process = etree.SubElement(
            definitions,
            f"{{{BPMN_NS}}}process",
            id=f"process_{workflow_id}",
            name=name,
            isExecutable="false"
        )
        
        # Add documentation
        if description:
            doc = etree.SubElement(process, f"{{{BPMN_NS}}}documentation")
            doc.text = description
        
        # Add workflow steps as BPMN elements
        for step in steps:
            self._add_bpmn_element(process, step, BPMN_NS)
        
        # Add sequence flows (connections between steps)
        for step in steps:
            for next_step_id in step.next_steps:
                flow = etree.SubElement(
                    process,
                    f"{{{BPMN_NS}}}sequenceFlow",
                    id=f"flow_{step.step_id}_to_{next_step_id}",
                    sourceRef=step.step_id,
                    targetRef=next_step_id
                )
        
        # Write to file
        xml_filename = f"workflow_{workflow_id}.xml"
        xml_path = self.output_dir / xml_filename
        
        tree = etree.ElementTree(definitions)
        tree.write(
            str(xml_path),
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        )
        
        logger.info(f"BPMN XML generated: {xml_path}")
        return xml_path
    
    def _add_bpmn_element(
        self,
        process: etree.Element,
        step: WorkflowStep,
        namespace: str
    ):
        """Add BPMN element based on step type"""
        
        element_map = {
            'task': 'task',
            'event': 'startEvent' if 'start' in step.name.lower() else 'endEvent',
            'gateway': 'exclusiveGateway',
            'decision': 'exclusiveGateway'
        }
        
        element_type = element_map.get(step.step_type, 'task')
        
        element = etree.SubElement(
            process,
            f"{{{namespace}}}{element_type}",
            id=step.step_id,
            name=step.name
        )
        
        # Add documentation
        if step.description:
            doc = etree.SubElement(element, f"{{{namespace}}}documentation")
            doc.text = step.description
    
    async def _generate_diagram(
        self,
        workflow_id: str,
        steps: List[WorkflowStep],
        name: str
    ) -> Path:
        """Generate graphical workflow diagram using Graphviz"""
        
        # Create directed graph
        dot = Digraph(comment=name)
        dot.attr(rankdir='TB')  # Top to bottom layout
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
        
        # Add nodes
        for step in steps:
            # Customize node appearance based on type
            if step.step_type == 'event':
                dot.node(
                    step.step_id,
                    step.name,
                    shape='ellipse',
                    fillcolor='lightgreen' if 'start' in step.name.lower() else 'lightcoral'
                )
            elif step.step_type in ['gateway', 'decision']:
                dot.node(
                    step.step_id,
                    step.name,
                    shape='diamond',
                    fillcolor='lightyellow'
                )
            else:
                dot.node(
                    step.step_id,
                    step.name,
                    fillcolor='lightblue'
                )
        
        # Add edges
        for step in steps:
            for next_step_id in step.next_steps:
                dot.edge(step.step_id, next_step_id)
        
        # Render diagram
        diagram_filename = f"workflow_{workflow_id}"
        diagram_path = self.output_dir / f"{diagram_filename}.{self.diagram_format}"
        
        dot.render(
            str(self.output_dir / diagram_filename),
            format=self.diagram_format,
            cleanup=True
        )
        
        logger.info(f"Workflow diagram generated: {diagram_path}")
        return diagram_path
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDiagram]:
        """Retrieve workflow by ID"""
        xml_path = self.output_dir / f"workflow_{workflow_id}.xml"
        diagram_path = self.output_dir / f"workflow_{workflow_id}.{self.diagram_format}"
        
        if not xml_path.exists():
            return None
        
        # Parse XML to reconstruct workflow
        tree = etree.parse(str(xml_path))
        root = tree.getroot()
        
        # Extract basic info (simplified)
        # In production, you'd want to fully parse the BPMN
        
        return WorkflowDiagram(
            workflow_id=workflow_id,
            name="Retrieved Workflow",
            description="",
            steps=[],
            xml_path=str(xml_path),
            diagram_path=str(diagram_path) if diagram_path.exists() else None,
            created_at=datetime.now()
        )


# Global instance
workflow_generator = WorkflowGenerator()
