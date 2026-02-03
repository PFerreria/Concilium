from lxml import etree
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime
import uuid
import subprocess
import tempfile

from app.config import settings
from app.models.schemas import WorkflowStep, WorkflowDiagram

logger = logging.getLogger(__name__)


class WorkflowGenerator:
    """Enhanced Workflow XML generation service with diagram rendering"""
    
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
            
            # Generate BPMN XML (now .bpmn)
            xml_path = await self.generate_bpmn_xml(
                workflow_id, steps, name, description
            )
            
            # Diagram generation REMOVED as requested.
            
            workflow = WorkflowDiagram(
                workflow_id=workflow_id,
                name=name,
                description=description,
                steps=steps,
                xml_path=str(xml_path),
                diagram_path=None,
                created_at=datetime.now()
            )
            
            logger.info(f"Workflow generated successfully: {workflow_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Workflow generation failed: {e}")
            raise
    
    async def generate_bpmn_xml(
        self,
        workflow_id: str,
        steps: List[WorkflowStep],
        name: str,
        description: str
    ) -> Path:
        """Generate BPMN 2.0 compliant XML file with proper logic and visualization"""
        
        # Create BPMN namespace
        BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
        BPMNDI_NS = "http://www.omg.org/spec/BPMN/20100524/DI"
        DC_NS = "http://www.omg.org/spec/DD/20100524/DC"
        DI_NS = "http://www.omg.org/spec/DD/20100524/DI"
        
        nsmap = {
            None: BPMN_NS,
            'bpmndi': BPMNDI_NS,
            'dc': DC_NS,
            'di': DI_NS
        }
        
        # Create root element
        definitions = etree.Element(
            f"{{{BPMN_NS}}}definitions",
            nsmap=nsmap,
            id=f"definitions_{workflow_id}",
            targetNamespace="http://concilium.ai/workflows",
            exporter="Concilium",
            exporterVersion="1.0"
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
        
        # Analyze and fix workflow structure
        fixed_steps = self._fix_workflow_structure(steps)
        
        # Add workflow steps as BPMN elements
        for step in fixed_steps:
            self._add_bpmn_element(process, step, BPMN_NS)
        
        # Add sequence flows (connections between steps)
        flow_counter = 0
        for step in fixed_steps:
            for next_step_id in step.next_steps:
                flow_counter += 1
                flow = etree.SubElement(
                    process,
                    f"{{{BPMN_NS}}}sequenceFlow",
                    id=f"flow_{flow_counter}",
                    sourceRef=step.step_id,
                    targetRef=next_step_id
                )
        
        # Add BPMN Diagram Information (for visualization)
        diagram = etree.SubElement(
            definitions,
            f"{{{BPMNDI_NS}}}BPMNDiagram",
            id=f"diagram_{workflow_id}"
        )
        
        plane = etree.SubElement(
            diagram,
            f"{{{BPMNDI_NS}}}BPMNPlane",
            id=f"plane_{workflow_id}",
            bpmnElement=f"process_{workflow_id}"
        )
        
        # Add visual layout for each element
        self._add_visual_layout(plane, fixed_steps, BPMNDI_NS, DC_NS, DI_NS, flow_counter)
        
        # Write to file
        xml_filename = f"workflow_{workflow_id}.bpmn"
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
    
    # Diagram generation methods removed
    
    def _fix_workflow_structure(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """
        Fix and validate workflow structure:
        - Ensure there's a start event
        - Ensure there's an end event
        - Fix disconnected steps
        - Validate flow logic
        """
        if not steps:
            # Create minimal workflow
            return [
                WorkflowStep(
                    step_id="start_1",
                    name="Start",
                    description="Workflow start",
                    step_type="event",
                    next_steps=["end_1"]
                ),
                WorkflowStep(
                    step_id="end_1",
                    name="End",
                    description="Workflow end",
                    step_type="event",
                    next_steps=[]
                )
            ]
        
        fixed_steps = list(steps)
        
        # Find start and end events
        start_events = [s for s in fixed_steps if 'start' in s.name.lower() or s.step_type == 'event' and not any(s.step_id in step.next_steps for step in fixed_steps)]
        end_events = [s for s in fixed_steps if 'end' in s.name.lower() or (not s.next_steps and s.step_type == 'event')]
        
        # If no start event, create one
        if not start_events:
            start_event = WorkflowStep(
                step_id="start_1",
                name="Start",
                description="Workflow start",
                step_type="event",
                next_steps=[fixed_steps[0].step_id] if fixed_steps else []
            )
            fixed_steps.insert(0, start_event)
            start_events = [start_event]
        
        # If no end event, create one
        if not end_events:
            # Find steps with no next_steps (potential end points)
            leaf_steps = [s for s in fixed_steps if not s.next_steps and s.step_type != 'event']
            
            end_event = WorkflowStep(
                step_id="end_1",
                name="End",
                description="Workflow end",
                step_type="event",
                next_steps=[]
            )
            
            # Connect leaf steps to end event
            for leaf in leaf_steps:
                leaf.next_steps.append(end_event.step_id)
            
            fixed_steps.append(end_event)
        
        # Ensure all steps are connected (no orphans)
        connected_ids = set()
        
        def mark_connected(step_id):
            if step_id in connected_ids:
                return
            connected_ids.add(step_id)
            step = next((s for s in fixed_steps if s.step_id == step_id), None)
            if step:
                for next_id in step.next_steps:
                    mark_connected(next_id)
        
        # Start from start events
        for start in start_events:
            mark_connected(start.step_id)
        
        # Remove orphaned steps or connect them
        all_step_ids = {s.step_id for s in fixed_steps}
        orphaned = all_step_ids - connected_ids
        
        if orphaned:
            logger.warning(f"Found orphaned steps: {orphaned}")
            # Connect first orphaned step to start event
            if start_events and orphaned:
                first_orphan = next(s for s in fixed_steps if s.step_id in orphaned)
                start_events[0].next_steps.append(first_orphan.step_id)
        
        return fixed_steps
    
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
    
    def _add_visual_layout(self, plane, steps, BPMNDI_NS, DC_NS, DI_NS, flow_count):
        """Add visual positioning information for BPMN elements"""
        
        # Layout configuration
        start_x = 100
        start_y = 100
        step_width = 120
        step_height = 80
        event_size = 40
        horizontal_spacing = 180
        vertical_spacing = 120
        
        # Calculate positions (simple linear layout)
        positions = {}
        x = start_x
        y = start_y
        
        for i, step in enumerate(steps):
            if step.step_type == 'event':
                positions[step.step_id] = {
                    'x': x,
                    'y': y,
                    'width': event_size,
                    'height': event_size
                }
            else:
                positions[step.step_id] = {
                    'x': x,
                    'y': y,
                    'width': step_width,
                    'height': step_height
                }
            
            # Move to next position
            if i % 3 == 2:  # Every 3 steps, go to next row
                x = start_x
                y += vertical_spacing
            else:
                x += horizontal_spacing
        
        # Add shape elements
        for step in steps:
            pos = positions[step.step_id]
            
            shape = etree.SubElement(
                plane,
                f"{{{BPMNDI_NS}}}BPMNShape",
                id=f"shape_{step.step_id}",
                bpmnElement=step.step_id
            )
            
            bounds = etree.SubElement(
                shape,
                f"{{{DC_NS}}}Bounds",
                x=str(pos['x']),
                y=str(pos['y']),
                width=str(pos['width']),
                height=str(pos['height'])
            )
        
        # Add edge elements for flows
        flow_num = 0
        for step in steps:
            for next_step_id in step.next_steps:
                flow_num += 1
                
                edge = etree.SubElement(
                    plane,
                    f"{{{BPMNDI_NS}}}BPMNEdge",
                    id=f"edge_flow_{flow_num}",
                    bpmnElement=f"flow_{flow_num}"
                )
                
                # Start point (from current step)
                if step.step_id in positions:
                    start_pos = positions[step.step_id]
                    start_x = start_pos['x'] + start_pos['width']
                    start_y = start_pos['y'] + start_pos['height'] / 2
                    
                    waypoint1 = etree.SubElement(
                        edge,
                        f"{{{DI_NS}}}waypoint",
                        x=str(start_x),
                        y=str(start_y)
                    )
                
                # End point (to next step)
                if next_step_id in positions:
                    end_pos = positions[next_step_id]
                    end_x = end_pos['x']
                    end_y = end_pos['y'] + end_pos['height'] / 2
                    
                    waypoint2 = etree.SubElement(
                        edge,
                        f"{{{DI_NS}}}waypoint",
                        x=str(end_x),
                        y=str(end_y)
                    )
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDiagram]:
        """Retrieve workflow by ID"""
        xml_path = self.output_dir / f"workflow_{workflow_id}.xml"
        diagram_path = self.output_dir / f"workflow_{workflow_id}.{self.diagram_format}"
        
        if not xml_path.exists():
            return None
        
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
