from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..tool import Tool
from ..agent import get_llm

def default_llm(prompt: str) -> str:
    raise RuntimeError("No LLM callable provided")

@dataclass
class ThoughtStep:
    text: str

@dataclass
class ActionStep:
    tool: str
    args: Dict[str, Any]

@dataclass
class ObservationStep:
    result: Any

@dataclass
class Scratchpad:
    steps: List[Any] = field(default_factory=list)

    def add(self, step: Any) -> None:
        self.steps.append(step)

    def format(self) -> str:
        lines = []
        for step in self.steps:
            if isinstance(step, ThoughtStep):
                lines.append(f"Thought: {step.text}")
            elif isinstance(step, ActionStep):
                lines.append(f"Action: {step.tool}")
                lines.append(f"Action Input: {json.dumps(step.args)}")
            elif isinstance(step, ObservationStep):
                lines.append(f"Observation: {step.result}")
        return "\n".join(lines)

@dataclass
class ReactAgent:
    """ReAct (Reasoning + Acting) agent with built-in LLM support."""
    
    llm_callable: Optional[callable] = None
    tools: List[Tool] = field(default_factory=list)
    max_steps: int = 10
    
    def __post_init__(self):
        if self.llm_callable is None:
            self.llm_callable = get_llm()

    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the agent."""
        self.tools.append(tool)

    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all available tools."""
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"{tool.name}: {tool.description}")
        return "\n".join(descriptions)

    def parse_action(self, text: str) -> Optional[ActionStep]:
        """Parse action from LLM response."""
        lines = text.strip().split('\n')
        action_line = None
        input_line = None
        
        for line in lines:
            if line.startswith("Action:"):
                action_line = line[7:].strip()
            elif line.startswith("Action Input:"):
                input_line = line[13:].strip()
        
        if action_line and input_line:
            try:
                args = json.loads(input_line)
                return ActionStep(tool=action_line, args=args)
            except json.JSONDecodeError:
                return None
        return None

    def execute_tool(self, action: ActionStep) -> Any:
        """Execute a tool action."""
        for tool in self.tools:
            if tool.name == action.tool:
                return tool.execute(**action.args)
        return f"Tool '{action.tool}' not found"

    def run_react(self, query: str, max_steps: Optional[int] = None) -> str:
        """Run the ReAct reasoning loop."""
        if max_steps is None:
            max_steps = self.max_steps
            
        scratchpad = Scratchpad()
        
        for step in range(max_steps):
            # Create prompt with current scratchpad
            prompt = self._create_prompt(query, scratchpad)
            
            # Get LLM response
            response = self.llm_callable(prompt)
            
            # Check if this is a final answer
            if "Final Answer:" in response:
                final_answer = response.split("Final Answer:")[-1].strip()
                return final_answer
            
            # Parse thought
            if "Thought:" in response:
                thought_text = response.split("Thought:")[-1].split("Action:")[0].strip()
                scratchpad.add(ThoughtStep(thought_text))
            
            # Parse and execute action
            action = self.parse_action(response)
            if action:
                scratchpad.add(action)
                result = self.execute_tool(action)
                scratchpad.add(ObservationStep(result))
            else:
                # If no valid action, treat as final answer
                return response.strip()
        
        return "Maximum steps reached without final answer"

    def _create_prompt(self, query: str, scratchpad: Scratchpad) -> str:
        """Create the ReAct prompt."""
        tools_desc = self.get_tool_descriptions()
        
        prompt = f"""You are a helpful assistant that can use tools to answer questions.

Available tools:
{tools_desc}

Use the following format:
Thought: think about what to do
Action: the action to take (must be one of the available tools)
Action Input: the input to the action as valid JSON
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Final Answer: the final answer to the original question

Question: {query}

{scratchpad.format()}
"""
        return prompt

