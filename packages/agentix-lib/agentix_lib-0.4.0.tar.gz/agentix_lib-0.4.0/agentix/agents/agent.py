import time
from typing import List, Dict, Any, Optional, Callable, Union, Awaitable
from dataclasses import dataclass, field
from typing import Set
import asyncio

from ..tools.tool_analyzer import ToolAnalyzer
from ..llms import LLM
from ..memory.memory import Memory, ConversationMessage
from ..memory.reflection_memory import ReflectionMemory
from ..tools.tools import Tool
from ..planner import SimpleLLMPlanner, Planner
from ..tools.tool_request import ToolRequestParser, ParsedToolRequest
from ..utils.debug_logger import DebugLogger
from ..metrics.workflow_metrics import BaseWorkflowMetrics

@dataclass
class AgentOptions:
    """Options to configure agent behavior and safety checks."""
    max_steps: int = 15
    usage_limit: int = 15
    use_reflection: bool = True
    time_to_live: int = 120000  # ms
    debug: bool = False
    validate_output: bool = False
    
    # Planning capabilities
    enable_planning: bool = False
    
    # Recovery capabilities
    auto_recovery: bool = False
    max_recovery_attempts: int = 3
    
    # Approval settings
    require_approval_for: Set[str] = field(default_factory=lambda: set())
    approval_callback: Optional[Callable[[str, str], Awaitable[bool]]] = None
    
    # Progress tracking
    progress_callback: Optional[Callable[[str, float], None]] = None


@dataclass
class AgentHooks:
    """Lifecycle hooks for debugging or advanced usage."""
    on_plan_generated: Optional[Callable[[str], None]] = None
    on_tool_call: Optional[Callable[[str, str], Union[Awaitable[bool], bool]]] = None
    on_tool_validation_error: Optional[Callable[[str, str], None]] = None
    on_tool_result: Optional[Callable[[str, str], None]] = None
    on_final_answer: Optional[Callable[[str], None]] = None
    on_step: Optional[Callable[[List[ConversationMessage]], None]] = None


class Agent:
    """
    The main Agent class that can do multi-step reasoning, tool usage, etc.
    """
    
    def __init__(self, 
                 name: Optional[str] = None,
                 model: LLM = None,
                 memory: Memory = None,
                 tools: List[Tool] = None,
                 instructions: List[str] = None,
                 planner: Optional[Planner] = None,
                 options: Optional[Union[AgentOptions, Dict[str, Any]]] = None,
                 hooks: Optional[AgentHooks] = None,
                 task: Optional[str] = None,
                 validation_model: Optional[LLM] = None,
                 metrics: Optional[BaseWorkflowMetrics] = None):
        """
        Initialize an agent with the given parameters.
        """
        self.name = name or "UnnamedAgent"
        self.model = model
        self.memory = memory
        self.tools = tools or []
        self.instructions = instructions or []
        self.planner = planner
        self.hooks = hooks or AgentHooks()
        
        self.task = task
        self.validation_model = validation_model
        
        # Initialize metrics
        self.metrics = metrics or BaseWorkflowMetrics()
        
        # Options - handle both dict and AgentOptions
        if options is None:
            self.options = AgentOptions()
        elif isinstance(options, dict):
            # Convert dict to AgentOptions
            agent_options = AgentOptions()
            for key, value in options.items():
                if hasattr(agent_options, key):
                    setattr(agent_options, key, value)
                else:
                    print(f"Warning: Ignoring unknown option '{key}'")
            self.options = agent_options
        else:
            self.options = options
        
        # Set instance variables from options for backward compatibility
        self.max_steps = self.options.max_steps
        self.usage_limit = self.options.usage_limit
        self.time_to_live = self.options.time_to_live
        self.debug = self.options.debug
        self.logger = DebugLogger(enabled=self.debug)
        self.validate_output = self.options.validate_output
        
        # Reflection toggling
        if len(self.tools) > 0:
            self.use_reflection = True
            if not self.options.use_reflection:
                self.logger.warn(f"[Agent] Tools were provided, forcing use_reflection to True.")
        else:
            self.use_reflection = self.options.use_reflection
            
        # Initialize tracking attributes
        self.llm_calls_used = 0
        self.start_time = 0
        self.step_count = 0
        
        # Initialize tool tracking
        self._tool_usage_counter = {}
        self._consecutive_tool_calls = 0
        self._failed_tool_calls = {}
        self._last_n_tool_calls = []
        self._last_n_assistant_messages = []
    
    @classmethod
    def create(cls, 
               name: Optional[str] = None,
               model: LLM = None,
               memory: Memory = None,
               tools: Optional[List[Tool]] = None,
               instructions: Optional[List[str]] = None,
               planner: Optional[Planner] = None,
               options: Optional[Union[AgentOptions, Dict[str, Any]]] = None,
               hooks: Optional[AgentHooks] = None,
               task: Optional[str] = None,
               validation_model: Optional[LLM] = None,
               metrics: Optional[BaseWorkflowMetrics] = None) -> 'Agent':
        """
        Factory method to create an Agent instance.
        
        Args:
            name: Agent name
            model: The LLM to use (OpenAIChat or TogetherChat)
            memory: Memory implementation to use
            tools: Available tools
            instructions: Custom instructions to add to the prompt
            planner: Optional planner for more complex reasoning
            options: Agent configuration options
            hooks: Lifecycle hooks for debugging or advanced usage
            task: The user's stated task (for validation context)
            validation_model: Optional separate model for validation
            metrics: Optional metrics tracker for the agent
            
        Returns:
            An initialized Agent
        """
        return cls(
            name=name,
            model=model,
            memory=memory,
            tools=tools,
            instructions=instructions,
            planner=planner,
            options=options,
            hooks=hooks,
            task=task,
            validation_model=validation_model,
            metrics=metrics
        )
    
    @classmethod
    async def create_with_generated_prompt(
        cls,
        name: str,
        model: LLM,
        memory: Memory,
        tools: List[Tool],
        task_description: str,
        additional_instructions: Optional[List[str]] = None,
        prompt_builder_model: Optional[LLM] = None,
        use_json_format: bool = False,
        options: Optional[Union[AgentOptions, Dict[str, Any]]] = None,
        hooks: Optional[AgentHooks] = None,
        validation_model: Optional[LLM] = None
    ) -> 'Agent':
        """
        Factory method to create an Agent with an auto-generated system prompt.
        
        This method uses the AgentPromptBuilder to automatically generate tailored
        instructions based on the agent's purpose and available tools.
        
        Args:
            name: Agent name
            model: The LLM to use for the agent
            memory: Memory implementation to use
            tools: Available tools
            task_description: Description of the agent's purpose/task
            additional_instructions: Optional custom instruction points to include
            prompt_builder_model: Optional custom LLM for prompt generation
            use_json_format: If True, generates prompt in JSON format
            options: Agent configuration options
            hooks: Lifecycle hooks for debugging or advanced usage
            validation_model: Optional separate model for validation
            
        Returns:
            An initialized Agent with auto-generated instructions
        """
        from .prompt_builder import AgentPromptBuilder
        
        # Create the prompt builder
        # If no model is provided, it will initialize its own default model
        builder = AgentPromptBuilder(model=prompt_builder_model)
        
        # Generate the prompt
        prompt_result = await builder.generate_prompt(
            agent_name=name,
            tools=tools,
            task_description=task_description,
            additional_instructions=additional_instructions,
            return_json=use_json_format
        )
        
        # Extract the prompt text from JSON if necessary
        prompt_text = prompt_result["prompt"] if use_json_format else prompt_result
        
        # Convert the prompt into instruction lines
        instruction_lines = [line.strip() for line in prompt_text.split('\n') if line.strip()]
        
        # Create the agent with the generated instructions
        return cls.create(
            name=name,
            model=model,
            memory=memory,
            tools=tools,
            instructions=instruction_lines,
            options=options,
            hooks=hooks,
            task=task_description,
            validation_model=validation_model
        )
    
    async def run(self, query: str) -> str:
        """
        The main entry point for the agent.
        """
        self.start_time = int(time.time() * 1000)  # current time in ms
        self.step_count = 0
        
        self.logger.log(f"[Agent:{self.name}] Starting run", {"query": query})
        
        # Initialize conversation
        await self.memory.add_message({
            "role": "system",
            "content": self.build_system_prompt()
        })
        await self.memory.add_message({"role": "user", "content": query})
        
        try:
            # If planning is enabled, use planner-based execution
            if self.options.enable_planning:
                self.logger.log(f"[Agent:{self.name}] Using planner-based execution")
                
                # Create planner if not provided, using the agent's model
                if not self.planner:
                    self.planner = SimpleLLMPlanner(self.model, debug=self.debug)
                    self.logger.log(f"[Agent:{self.name}] Created default planner")
                
                return await self._execute_with_recovery(
                    lambda: self.execute_planner_flow(query),
                    is_planning=True
                )
            
            # Single-pass if reflection is off
            if not self.use_reflection:
                return await self._execute_with_recovery(
                    lambda: self.single_pass(),
                    is_planning=False
                )
            
            # Default reflection loop with recovery
            while True:
                # Check usage/time
                elapsed = int(time.time() * 1000) - self.start_time
                self.logger.stats({
                    "llm_calls_used": self.llm_calls_used,
                    "llm_calls_limit": self.usage_limit,
                    "steps_used": self.step_count,
                    "max_steps": self.max_steps,
                    "elapsed_ms": elapsed,
                    "time_to_live": self.time_to_live,
                })
                
                if self.should_stop(elapsed):
                    return self.get_stopping_reason(elapsed)
                
                self.llm_calls_used += 1
                self.step_count += 1
                
                context = await self.memory.get_context_for_prompt(query)
                llm_output = await self.model.call(context)
                self.logger.log(f"[Agent:{self.name}] LLM Output:", {"llm_output": llm_output})
                
                # Track recent LLM outputs to detect repetition
                self._last_n_assistant_messages.append(llm_output)
                if len(self._last_n_assistant_messages) > 3:
                    self._last_n_assistant_messages.pop(0)  # Keep only the most recent 3
                    
                # Check for repetitive outputs
                is_repetitive = False
                if len(self._last_n_assistant_messages) >= 2:
                    # Check if last two messages are identical or very similar
                    if self._last_n_assistant_messages[-1] == self._last_n_assistant_messages[-2]:
                        is_repetitive = True
                
                # Tool usage?
                tool_request = ToolRequestParser.parse(llm_output)
                if tool_request:
                    self.logger.log(f"[Agent:{self.name}] Tool request parsed:", {"tool": tool_request.tool_name, "query": tool_request.query, "args": tool_request.args})
                    
                    # Keep track of last few tool calls to detect patterns
                    tool_key = f"{tool_request.tool_name}:{tool_request.query}"
                    self._last_n_tool_calls.append(tool_key)
                    if len(self._last_n_tool_calls) > 3:
                        self._last_n_tool_calls.pop(0)  # Keep only the most recent 3
                        
                    # Check if we're in a problematic pattern
                    is_stuck_pattern = self._check_for_stuck_patterns()
                    
                    # Increment counter
                    self._consecutive_tool_calls += 1
                    
                    # Check for tool call issues
                    if is_stuck_pattern or self._consecutive_tool_calls > 3:
                        # We're either in a loop or making too many consecutive calls
                        guidance_message = (
                            "I notice you're making multiple tool calls without providing a final answer. "
                            "Based on the information you've gathered so far, please provide a FINAL ANSWER: to "
                            "the user's query. If you're encountering errors with a particular tool, try a different "
                            "approach or summarize what you do know."
                        )
                        
                        # If we've made many tool calls, make the message stronger
                        if self._consecutive_tool_calls > 5:
                            guidance_message = (
                                "You have made several consecutive tool calls without reaching a conclusion. "
                                "Please STOP making additional tool calls and provide a FINAL ANSWER: based on "
                                "the information you have. Even a partial answer is better than continuing to "
                                "call tools in a loop."
                            )
                        
                        await self.memory.add_message({
                            "role": "system", 
                            "content": guidance_message
                        })
                        
                        # For extreme cases, force a final answer
                        if self._consecutive_tool_calls > 7:
                            self.logger.log(f"[Agent:{self.name}] Forcing final answer after too many consecutive tool calls")
                            return "I apologize, but I've been unable to provide a complete answer due to tool usage issues. Please try rephrasing your query or asking about a different topic."
                    
                    # Store the tool request in memory to help the model see its own requests
                    await self.memory.add_message({
                        "role": "assistant", 
                        "content": llm_output,
                        "metadata": {"type": "tool_request"}
                    })
                    
                    result = await self._execute_with_recovery(
                        lambda: self.handle_tool_request(tool_request),
                        is_planning=False
                    )
                    
                    # Store tool results with a more distinctive format
                    await self.memory.add_message({
                        "role": "assistant",
                        "content": f"Tool '{tool_request.tool_name}' returned: {result}",
                        "metadata": {
                            "type": "tool_result",
                            "tool_name": tool_request.tool_name
                        }
                    })
                    
                    continue  # Next iteration
                else:
                    self.logger.log(f"[Agent:{self.name}] No tool request found in output")
                
                # Reset consecutive tool calls counter if we're not making a tool call
                self._consecutive_tool_calls = 0
                
                # Check for repetitive outputs and add guidance if needed
                if is_repetitive:
                    self.logger.log(f"[Agent:{self.name}] Detected repetitive outputs")
                    guidance_message = (
                        "I notice you're repeating similar responses. If you've gathered enough information, "
                        "please provide a FINAL ANSWER: to the user's query. Remember to prefix your final response "
                        "with 'FINAL ANSWER:' to clearly indicate you've completed the task."
                    )
                    await self.memory.add_message({
                        "role": "system", 
                        "content": guidance_message
                    })
                    
                    # Force a final answer if repeatedly stuck
                    if len(self._last_n_assistant_messages) >= 3 and all(m == self._last_n_assistant_messages[0] for m in self._last_n_assistant_messages):
                        self.logger.log(f"[Agent:{self.name}] Forcing final answer after too many repetitive outputs")
                        # Extract previous non-repetitive content as the final answer
                        final_content = ""
                        for msg in reversed(await self.memory.get_context()):
                            if msg["role"] == "assistant" and msg["content"] != self._last_n_assistant_messages[-1]:
                                final_content = msg["content"]
                                break
                        
                        if not final_content:
                            final_content = self._last_n_assistant_messages[-1]
                        
                        return f"FINAL ANSWER: {final_content}"
                
                # Final answer check
                if "FINAL ANSWER:" in llm_output:
                    # Check if FINAL ANSWER is at the start or end
                    parts = llm_output.split("FINAL ANSWER:")
                    if len(parts) != 2:
                        # Multiple FINAL ANSWER markers - take the last one
                        final_ans = parts[-1].strip()
                    else:
                        # If FINAL ANSWER is at the start, take what's after
                        # If it's at the end, take what's before
                        if parts[0].strip() == "":
                            final_ans = parts[1].strip()
                        else:
                            final_ans = parts[0].strip()
                    
                    self.logger.log(f"[Agent:{self.name}] Final answer found", {"final_ans": final_ans})
                    
                    # Add final answer to memory
                    await self.memory.add_message({"role": "assistant", "content": llm_output})
                    
                    # If validate_output is true, attempt validation
                    if self.validate_output:
                        validated = await self.validate_final_answer(final_ans)
                        if not validated:
                            self.logger.log(f"[Agent:{self.name}] Validation failed. Continuing loop to refine...")
                            # We can either continue the loop or forcibly revise the answer
                            # We'll continue the loop here:
                            continue
                    
                    # Log final stats before returning
                    elapsed = int(time.time() * 1000) - self.start_time
                    self.logger.stats({
                        "llm_calls_used": self.llm_calls_used,
                        "llm_calls_limit": self.usage_limit,
                        "steps_used": self.step_count,
                        "max_steps": self.max_steps,
                        "elapsed_ms": elapsed,
                        "time_to_live": self.time_to_live,
                        "final_status": "completed"
                    })
                    
                    if self.hooks.on_final_answer:
                        await self.hooks.on_final_answer(final_ans)
                    return final_ans
                
                # Otherwise, treat as intermediate output
                await self.memory.add_message({"role": "assistant", "content": llm_output})
                
        except Exception as e:
            # Use recovery if enabled
            if self.options.auto_recovery:
                return await self._execute_with_recovery(
                    lambda: self.run(query),
                    is_planning=False
                )
            raise e
    
    def _check_for_stuck_patterns(self) -> bool:
        """
        Check if the agent is stuck in a pattern of repetitive tool calls.
        
        Returns:
            bool: True if a stuck pattern is detected, False otherwise
        """
        # Need at least 3 calls to detect a pattern
        if len(self._last_n_tool_calls) < 3:
            return False
        
        # Check for exact repetition (A, A, A)
        if self._last_n_tool_calls[-1] == self._last_n_tool_calls[-2] == self._last_n_tool_calls[-3]:
            return True
        
        # Check for alternating pattern (A, B, A)
        if self._last_n_tool_calls[-1] == self._last_n_tool_calls[-3]:
            return True
        
        # Check for cycling pattern (A, B, C, A, B, C)
        if len(self._last_n_tool_calls) >= 6:
            if (self._last_n_tool_calls[-1] == self._last_n_tool_calls[-4] and
                self._last_n_tool_calls[-2] == self._last_n_tool_calls[-5] and
                self._last_n_tool_calls[-3] == self._last_n_tool_calls[-6]):
                return True
            
        return False
    
    async def single_pass(self) -> str:
        """
        Single pass execution without reflection
        """
        if self.llm_calls_used >= self.usage_limit and self.usage_limit != -1:
            return "Usage limit reached. No more LLM calls allowed."
            
        self.llm_calls_used += 1
        single_response = await self.model.call(await self.memory.get_context())
        await self.memory.add_message({"role": "assistant", "content": single_response})
        
        # If validate_output is true, attempt validation
        if self.validate_output:
            validated = await self.validate_final_answer(single_response)
            if not validated:
                # If single-pass and fails validation, we just return it anyway, or we can override
                self.logger.log(f"[Agent:{self.name}] Single pass validation failed. Returning anyway.")
        
        # Log final stats before returning
        elapsed = int(time.time() * 1000) - self.start_time
        self.logger.stats({
            "llm_calls_used": self.llm_calls_used,
            "llm_calls_limit": self.usage_limit,
            "steps_used": self.step_count,
            "max_steps": self.max_steps,
            "elapsed_ms": elapsed,
            "time_to_live": self.time_to_live,
            "final_status": "completed"
        })
        
        if self.hooks.on_final_answer:
            await self.hooks.on_final_answer(single_response)
        return single_response
    
    async def execute_planner_flow(self, query: str) -> str:
        """
        Plan-then-execute approach if a planner is provided
        """
        if not self.planner:
            return "No planner specified."
            
        try:
            # Log stats before plan generation
            elapsed = int(time.time() * 1000) - self.start_time
            self.logger.stats({
                "llm_calls_used": self.llm_calls_used,
                "llm_calls_limit": self.usage_limit,
                "steps_used": self.step_count,
                "max_steps": self.max_steps,
                "elapsed_ms": elapsed,
                "time_to_live": self.time_to_live,
            })
            
            # Increment counters for plan generation
            self.llm_calls_used += 1
            self.step_count += 1
            
            # Generate plan with timeout to prevent hanging
            plan = await asyncio.wait_for(
                self.planner.generate_plan(query, self.tools, self.memory),
                timeout=30.0  # 30 second timeout for plan generation
            )
            
            if self.hooks.on_plan_generated:
                self.hooks.on_plan_generated(plan)
                
            # Format the plan nicely for logging
            try:
                import json
                parsed_plan = json.loads(plan)
                formatted_plan = json.dumps(parsed_plan, indent=2)
                
                # Create a summary of the plan
                plan_summary = "\n".join([
                    f"Step {i+1}: {step['action'].upper()} - {step['details'][:60]}..."
                    for i, step in enumerate(parsed_plan)
                ])
                
                self.logger.log(f"[Agent:{self.name}] Generated Plan:", {
                    "total_steps": len(parsed_plan),
                    "summary": plan_summary,
                    "full_plan": formatted_plan
                })
                
                # Check if planning requires approval
                if "planning" in {a.lower() for a in self.options.require_approval_for}:
                    self.logger.log(f"[Agent:{self.name}] Requesting plan approval")
                    approved = await self._request_approval(
                        "Planning",
                        f"Generated plan for task: {query}\n\nSummary:\n{plan_summary}\n\nFull Plan:\n{formatted_plan}"
                    )
                    if not approved:
                        self.logger.warn(f"[Agent:{self.name}] Plan was not approved")
                        return "Plan was not approved by user. Please try a different approach."
                
            except json.JSONDecodeError:
                self.logger.log(f"[Agent:{self.name}] Failed to parse plan for formatting", {
                    "error": "Plan is None or invalid JSON",
                    "raw_plan": plan,
                    "level": "error"
                })
                return "Failed to generate a valid plan. Falling back to direct execution."
            
            steps = self.parse_plan(plan)
            if not steps:
                return "Generated plan had no executable steps. Please try again with a different approach."
                
            total_steps = len(steps)
            
            # Update progress to 0%
            if self.options.progress_callback:
                self.options.progress_callback(self.name, 0.0)
            
            for i, step in enumerate(steps, 1):
                # Format the current step nicely
                try:
                    step_formatted = json.dumps(step, indent=2)
                except:
                    step_formatted = str(step)
                    
                self.logger.log(f"[Agent:{self.name}] Executing step {i}/{len(steps)}", {
                    "step_details": step_formatted,
                    "action": step.get("action"),
                    "details": step.get("details")
                })
                
                # Execute step with recovery
                try:
                    # Log stats before step execution
                    elapsed = int(time.time() * 1000) - self.start_time
                    self.logger.stats({
                        "llm_calls_used": self.llm_calls_used,
                        "llm_calls_limit": self.usage_limit,
                        "steps_used": self.step_count,
                        "max_steps": self.max_steps,
                        "elapsed_ms": elapsed,
                        "time_to_live": self.time_to_live,
                    })
                    
                    # Increment counters for step execution
                    self.llm_calls_used += 1
                    self.step_count += 1
                    
                    step_response = await self._execute_with_recovery(
                        lambda: self.execute_plan_step(step, query),
                        is_planning=True
                    )
                    await self.memory.add_message({"role": "assistant", "content": step_response})
                    
                    self.logger.log(f"[Agent:{self.name}] Step {i} completed", {
                        "response": step_response
                    })
                except Exception as e:
                    self.logger.log(f"[Agent:{self.name}] Step {i} failed", {
                        "error": str(e),
                        "level": "error"
                    })
                    # If a step fails, try to continue with remaining steps
                    continue
                
                # Update progress
                if self.options.progress_callback:
                    progress = i / total_steps
                    self.options.progress_callback(self.name, progress)
                
                if "FINAL ANSWER" in step_response:
                    # Extract the final answer string
                    final_answer = step_response.replace("FINAL ANSWER:", "").strip()
                    
                    self.logger.log(f"[Agent:{self.name}] Plan execution completed with final answer", {
                        "total_steps_executed": i,
                        "final_answer": final_answer
                    })
                    
                    # Validate if required
                    if self.validate_output:
                        pass_validation = await self.validate_final_answer(final_answer)
                        if not pass_validation:
                            self.logger.log(
                                f"[Agent:{self.name}] Validation failed in planner flow. Continuing with best effort answer."
                            )
                    
                    # Update progress to 100%
                    if self.options.progress_callback:
                        self.options.progress_callback(self.name, 1.0)
                    
                    # Log final stats before returning
                    elapsed = int(time.time() * 1000) - self.start_time
                    self.logger.stats({
                        "llm_calls_used": self.llm_calls_used,
                        "llm_calls_limit": self.usage_limit,
                        "steps_used": self.step_count,
                        "max_steps": self.max_steps,
                        "elapsed_ms": elapsed,
                        "time_to_live": self.time_to_live,
                        "final_status": "completed"
                    })
                    
                    return final_answer
            
            self.logger.log(f"[Agent:{self.name}] Plan execution completed without final answer", {
                "total_steps": len(steps)
            })
            return "Plan executed but no final answer was found. Please try again with a more specific query."
            
        except asyncio.TimeoutError:
            self.logger.log(f"[Agent:{self.name}] Plan generation timed out", {
                "level": "error"
            })
            return "Plan generation timed out. Falling back to direct execution."
            
        except Exception as e:
            self.logger.log(f"[Agent:{self.name}] Error in planner flow", {
                "error": str(e),
                "level": "error"
            })
            return f"Error during planning: {str(e)}. Please try again with a different approach."
    
    def build_system_prompt(self) -> str:
        """
        Build an intelligent system prompt that includes complete tool documentation.
        """
        lines = []
        lines.append(f'You are an intelligent AI agent named "{self.name}".')
        
        if self.tools:
            # Analyze all tools using the new analyze_tools method
            tool_analyses = ToolAnalyzer.analyze_tools(self.tools)
            
            lines.append("\nAvailable Tools:")
            for analysis in tool_analyses:
                # Tool name and description
                lines.append(f"\n📦 {analysis.name}")
                lines.append(f"Description: {analysis.description}")
                
                # Parameters if any
                if analysis.parameters:
                    lines.append("Parameters:")
                    for param in analysis.parameters:
                        required = "(required)" if param.required else "(optional)"
                        lines.append(f"  - {param.name}: {param.type} {required}")
                        if param.description:
                            lines.append(f"    {param.description}")
                        
                        # Show valid values if available
                        if analysis.valid_parameter_values and param.name in analysis.valid_parameter_values:
                            valid_values = analysis.valid_parameter_values[param.name]
                            lines.append(f"    Valid values: {', '.join(valid_values)}")
                
                # Usage examples with explanations
                if analysis.usage_examples:
                    lines.append("Example Usage:")
                    for example in analysis.usage_examples:
                        lines.append(f"  {example}")
                
                # Parameter schema if available
                if analysis.parameter_schema:
                    lines.append("Parameter Schema:")
                    lines.append(f"  {analysis.parameter_schema}")
            
            lines.append("\nHow to use tools:")
            lines.append("1. For tools with parameters, ALWAYS use the JSON format:")
            lines.append('   TOOL REQUEST: ToolName {"param1": "value1", "param2": "value2"}')
            lines.append("2. For simple tools without parameters:")
            lines.append('   TOOL REQUEST: ToolName "your query"')
            lines.append("3. When a tool accepts specific values (like '1mo', '3mo', etc.), use ONLY those valid values")
            lines.append("4. Always check the parameter descriptions and valid values before making a tool request")
            lines.append("5. For date-based queries, use the appropriate period parameter instead of specific dates")
        else:
            lines.append("You do not have any tools available.")
        
        lines.append(
            "\nImportant guidelines:"
            "\n1. After using tools to gather information, you MUST provide a final answer to the user."
            "\n2. Do not repeat the same tool calls unnecessarily."
            "\n3. When you have gathered sufficient information and are ready to provide your final response:"
            "\n   - Start your response with 'FINAL ANSWER:' followed by your complete answer"
            "\n   - Put 'FINAL ANSWER:' at the START of your response, not at the end"
            "\n   - Include all relevant information in your final answer"
            "\n   - Make your final answer comprehensive and directly address the user's query"
            "\n4. When you see 'TOOL RESULT:' in the conversation, this means you've already received a response from that tool."
            "\n5. PAY CLOSE ATTENTION to previous tool results in the conversation before making new tool calls."
            "\n6. If you already have the information needed from a previous tool result, DO NOT call the same tool again."
            "\n7. Always analyze provided tool results before making additional tool calls."
            "\n8. NEVER try to use date strings directly - use the predefined period values like '1mo', '3mo', etc."
            "\n9. DO NOT just ask if the user has more questions without providing a 'FINAL ANSWER:' first."
        )
        
        lines.extend(self.instructions)
        
        return "\n".join(lines)
    
    def parse_plan(self, plan: str) -> List[Dict[str, str]]:
        """
        Parse the plan into steps
        """
        try:
            import json
            return json.loads(plan)
        except Exception:
            return [{"action": "message", "details": plan}]
    
    async def execute_plan_step(self, step: Dict[str, str], query: str) -> str:
        """
        Execute a single step from a plan with enhanced error handling and result processing
        """
        action = step.get("action", "")
        details = step.get("details", "")
        args = step.get("args", {})
        
        if action == "tool":
            # Create a tool request with the arguments
            from ..tools.tool_request import ParsedToolRequest
            tool_request = ParsedToolRequest(
                tool_name=details,
                query=query,
                args=args
            )
            
            try:
                # Increment tool call metrics
                self.metrics.increment("total_tool_calls")
                self.metrics.increment("total_agent_calls")
                
                # Validate tool exists before execution
                tool = self._find_tool(details)
                
                if not tool:
                    error_msg = f"Tool '{details}' not found in available tools"
                    await self.memory.add_message({
                        "role": "system",
                        "content": f"Error: {error_msg}"
                    })
                    return error_msg
                
                # Validate required parameters are present
                missing_params = []
                if tool.parameters:
                    for param in tool.parameters:
                        if param.required and param.name not in args:
                            missing_params.append(param.name)
                
                if missing_params:
                    error_msg = f"Missing required parameters for tool '{details}': {', '.join(missing_params)}"
                    await self.memory.add_message({
                        "role": "system",
                        "content": f"Error: {error_msg}"
                    })
                    return error_msg
                
                # Use handle_tool_request for execution
                result = await self.handle_tool_request(tool_request)
                
                # Process and store the result
                if not result:
                    error_msg = f"Tool '{details}' returned no result"
                    self.metrics.increment("error_count")
                    await self.memory.add_message({
                        "role": "system",
                        "content": f"Warning: {error_msg}"
                    })
                    return error_msg
                elif isinstance(result, str) and result.lower().startswith("error"):
                    self.metrics.increment("error_count")
                    await self.memory.add_message({
                        "role": "system",
                        "content": f"Tool execution error: {result}"
                    })
                else:
                    # Store successful result
                    await self.memory.add_message({
                        "role": "system",
                        "content": f"Tool '{details}' executed successfully. Result: {result}"
                    })
                
                return result
                
            except Exception as e:
                self.metrics.increment("error_count")
                error_msg = f"Error executing tool {details}: {str(e)}"
                await self.memory.add_message({
                    "role": "system",
                    "content": f"Exception during tool execution: {error_msg}"
                })
                return error_msg
            
        elif action == "message":
            # Process message step with context
            try:
                # Get relevant context from memory
                context = await self.memory.get_context()
                
                # Create a prompt that includes context
                message_prompt = [
                    {"role": "system", "content": "You are processing the results of previous steps to continue the plan execution. Analyze the information and provide clear insights."},
                    {"role": "user", "content": f"""
Task: {query}

Previous context:
{context[-10:] if context else 'No previous context'}

Current step message:
{details}

Provide a clear analysis of the current state and what should be done next.
"""}
                ]
                
                # Increment LLM call metrics
                self.metrics.increment("total_llm_calls")
                
                # Get response from model
                response = await self.model.call(message_prompt)
                
                # Log LLM output
                self.logger.log(f"[Agent:{self.name}] LLM Output:", {"llm_output": response})
                
                # Store the analysis
                await self.memory.add_message({
                    "role": "assistant",
                    "content": response
                })
                
                return response
                
            except Exception as e:
                error_msg = f"Error processing message step: {str(e)}"
                await self.memory.add_message({
                    "role": "system",
                    "content": f"Error: {error_msg}"
                })
                return error_msg
                
        elif action == "complete":
            # Validate and format final answer
            try:
                # Get full context
                context = await self.memory.get_context()
                
                # Create completion prompt
                completion_prompt = [
                    {"role": "system", "content": "You are finalizing the response to the user's query. Ensure the answer is complete and incorporates all relevant information from previous steps."},
                    {"role": "user", "content": f"""
Original query: {query}

Context from previous steps:
{context[-10:] if context else 'No previous context'}

Proposed final answer:
{details}

Provide a comprehensive final answer that includes all relevant information and addresses the original query.
"""}
                ]
                
                # Get validated response
                self.metrics.increment("total_llm_calls")
                final_response = await self.model.call(completion_prompt)
                
                # Remove any existing FINAL ANSWER prefix before adding our own
                cleaned_response = final_response.replace("FINAL ANSWER:", "").strip()
                return f"FINAL ANSWER: {cleaned_response}"
                
            except Exception as e:
                error_msg = f"Error finalizing answer: {str(e)}"
                await self.memory.add_message({
                    "role": "system",
                    "content": f"Error: {error_msg}"
                })
                return f"FINAL ANSWER: Error occurred while finalizing the answer. Based on available information: {details}"
                
        else:
            error_msg = f"Unknown action: {action}"
            await self.memory.add_message({
                "role": "system",
                "content": f"Error: {error_msg}"
            })
            return error_msg
    
    async def handle_tool_request(self, request: ParsedToolRequest) -> str:
        """
        Handle a tool request from the agent with improved error handling and feedback.
        """
        self.logger.log("Processing tool request", request)
        
        # Track tool usage to detect loops
        tool_key = f"{request.tool_name}:{request.query}"
        self._tool_usage_counter[tool_key] = self._tool_usage_counter.get(tool_key, 0) + 1
        
        # If the same tool with the same parameters is called more than twice, suggest moving to a final answer
        if self._tool_usage_counter.get(tool_key, 0) > 2:
            self.logger.log(f"Tool loop detected: {tool_key} used {self._tool_usage_counter[tool_key]} times")
            return (
                f"I've noticed you've called '{request.tool_name}' with the same parameters multiple times. "
                f"You already have this information from previous calls or the request is failing consistently. "
                f"Please analyze the previous tool results and provide a FINAL ANSWER: to respond to the user's query "
                f"with the best information you have, even if incomplete."
            )
        
        try:
            # First check if tool requires approval
            tool_approval_key = f"tool.{request.tool_name}".lower()
            if tool_approval_key in {a.lower() for a in self.options.require_approval_for}:
                approval_details = f"Tool: {request.tool_name}\nArgs: {request.args}\nQuery: {request.query}"
                if not await self._request_approval("Tool", approval_details):
                    return f"Tool '{request.tool_name}' execution was not approved"
            
            # Find and execute the tool
            tool = self._find_tool(request.tool_name)
            if not tool:
                return f"Tool '{request.tool_name}' not found"
                
            # Track consecutive tool calls
            self._consecutive_tool_calls += 1
            self._last_n_tool_calls.append(tool_key)
            if len(self._last_n_tool_calls) > 6:  # Keep last 6 for pattern detection
                self._last_n_tool_calls.pop(0)
                
            # Check for stuck patterns
            if self._check_for_stuck_patterns():
                return (
                    "I notice we're in a loop of repetitive tool calls. "
                    "Let's analyze what we know and provide a FINAL ANSWER with our current information."
                )
                
            # Call tool hooks if defined
            if self.hooks.on_tool_call:
                should_proceed = await self.hooks.on_tool_call(request.tool_name, str(request.args))
                if not should_proceed:
                    return f"Tool call to {request.tool_name} was rejected by hooks"
                    
            # Execute the tool with both query and args
            result = await tool.run(input_str=request.query, args=request.args)
            
            # Call result hooks if defined
            if self.hooks.on_tool_result:
                self.hooks.on_tool_result(request.tool_name, str(result))
                
            # Reset consecutive tool calls on success
            self._consecutive_tool_calls = 0
            
            # Return formatted result
            return f"Tool '{request.tool_name}' returned: {result}"
            
        except Exception as e:
            # Track failed calls
            self._failed_tool_calls[tool_key] = self._failed_tool_calls.get(tool_key, 0) + 1
            
            error_msg = f"Error calling {request.tool_name}: {str(e)}"
            self.logger.error("Tool execution returned error or empty result", {
                "tool_name": request.tool_name,
                "result": error_msg,
                "level": "error"
            })
            
            if self.hooks.on_tool_validation_error:
                self.hooks.on_tool_validation_error(request.tool_name, str(e))
                
            return error_msg
    
    def should_stop(self, elapsed: int) -> bool:
        """
        Called each iteration to see if we should stop for usage/time reasons
        """
        if self.max_steps != -1 and self.step_count >= self.max_steps:
            return True
        if self.usage_limit != -1 and self.llm_calls_used >= self.usage_limit:
            return True
        if self.time_to_live != -1 and elapsed >= self.time_to_live:
            return True
        return False
    
    def get_stopping_reason(self, elapsed: int) -> str:
        """
        Get a message explaining why execution stopped
        """
        if self.step_count >= self.max_steps:
            return f"Max steps ({self.max_steps}) reached without final answer."
        if self.usage_limit != -1 and self.llm_calls_used >= self.usage_limit:
            return f"Usage limit ({self.usage_limit} calls) reached."
        if elapsed >= self.time_to_live:
            return f"Time limit ({self.time_to_live}ms) reached after {elapsed}ms."
        return "Unknown stopping condition reached."
    
    async def handle_reflection(self, reflection_content: str) -> None:
        """
        Handle reflection content
        """
        reflection_message = {
            "role": "reflection",
            "content": reflection_content,
        }
        
        if isinstance(self.memory, ReflectionMemory):
            await self.memory.add_message(reflection_message)
        
        self.logger.log(f"Reflection stored: {reflection_content}")
    
    async def validate_final_answer(self, final_answer: str) -> bool:
        """
        Validate final answer if validate_output is True.
        Uses the agent's own model if no separate validation_model is provided.
        If passes validation, returns True. If fails, returns False.
        """
        # Use the agent's model if no separate validation model is provided
        validation_model = self.validation_model or self.model
        if not validation_model:
            # No model available at all, skip validation
            return True
        
        system_prompt = f"""
You are a validator that checks if an agent's final answer meets the user's task requirements.
If the final answer is correct and satisfies the task, respond with a JSON:
{{"is_valid":true,"reason":"some short reason"}}
If it fails or is incomplete, respond with:
{{"is_valid":false,"reason":"some short reason"}}

User's task (if any): {self.task or "(none provided)"}

Agent's final answer to validate:
{final_answer}
        """
        
        validator_output = await validation_model.call([
            {"role": "system", "content": system_prompt},
        ])
        
        self.logger.log(f"[Agent:{self.name}] Validator output:", {"validator_output": validator_output})
        
        # Attempt to parse
        try:
            import json
            parsed = json.loads(validator_output)
            if parsed.get("is_valid") is True:
                self.logger.log(f"[Agent:{self.name}] Validation PASSED: {parsed.get('reason')}")
                return True
            else:
                self.logger.log(f"[Agent:{self.name}] Validation FAILED: {parsed.get('reason')}")
                return False
        except Exception:
            self.logger.warn(f"[Agent:{self.name}] Could not parse validator output. Assuming fail.",
                            {"validator_output": validator_output})
            return False
    
    async def _request_approval(self, action_type: str, details: str) -> bool:
        """Request approval for an action.
        
        Args:
            action_type: Type of action requiring approval (e.g. "Planning", "Recovery", "Tool")
            details: Details about the action
            
        Returns:
            bool: True if approved, False otherwise
        """
        # Convert action type to lowercase for case-insensitive comparison
        action_type_lower = action_type.lower()
        
        # Check if this action type requires approval
        if action_type_lower not in {a.lower() for a in self.options.require_approval_for}:
            return True
            
        self.logger.log(f"[Agent:{self.name}] Requesting approval for {action_type}", {
            "action_type": action_type,
            "details": details
        })
        
        if self.options.approval_callback:
            # Directly await the callback since we're in an async context
            return await self.options.approval_callback(action_type, details)
            
        return True
    
    async def _execute_with_recovery(self, fn: Callable[[], Awaitable[Any]], is_planning: bool = False) -> Any:
        """
        Execute a function with automatic recovery attempts on failure.
        
        Args:
            fn: The async function to execute with recovery
            is_planning: Whether this is a planning operation (to prevent recursive recovery)
            
        Returns:
            The result of the function execution
            
        Raises:
            Exception: If all recovery attempts fail
        """
        recovery_attempts = 0
        max_attempts = self.options.max_recovery_attempts
        
        while True:
            try:
                # Execute the function
                return await fn()
                
            except Exception as e:
                # Don't attempt recovery if auto-recovery is disabled or if we're in planning
                if not self.options.auto_recovery or is_planning:
                    self.logger.log(f"[Agent:{self.name}] Auto-recovery disabled or in planning, failing", {
                        "error": str(e),
                        "is_planning": is_planning,
                        "level": "error"
                    })
                    raise e
                    
                # Track the error
                self.logger.log(f"[Agent:{self.name}] Error during execution", {
                    "error": str(e),
                    "recovery_attempt": recovery_attempts + 1,
                    "max_attempts": max_attempts,
                    "level": "error"
                })
                
                recovery_attempts += 1
                
                # Check if we've exceeded max attempts
                if recovery_attempts > max_attempts:
                    self.logger.log(f"[Agent:{self.name}] Max recovery attempts exceeded", {
                        "error": str(e),
                        "max_attempts": max_attempts,
                        "level": "error"
                    })
                    raise Exception(f"Failed after {max_attempts} recovery attempts: {str(e)}")
                    
                # Check if recovery requires approval
                if "recovery" in {a.lower() for a in self.options.require_approval_for}:
                    self.logger.log(f"[Agent:{self.name}] Requesting recovery approval", {
                        "attempt": recovery_attempts
                    })
                    approved = await self._request_approval(
                        "Recovery",
                        f"Recovery attempt {recovery_attempts}/{max_attempts} for error: {str(e)}"
                    )
                    if not approved:
                        self.logger.warn(f"[Agent:{self.name}] Recovery not approved")
                        raise Exception("Recovery was not approved by user")
                        
                # Execute recovery thinking
                self.logger.log(f"[Agent:{self.name}] Executing recovery thinking", {
                    "attempt": recovery_attempts
                })
                
                recovery_prompt = self._build_recovery_prompt(str(e), recovery_attempts)
                try:
                    recovery_thinking = await asyncio.wait_for(
                        self.model.call([
                            {"role": "system", "content": self.build_system_prompt()},
                            {"role": "user", "content": recovery_prompt}
                        ]),
                        timeout=30.0  # 30 second timeout for recovery thinking
                    )
                    
                    # Add recovery thinking to memory
                    await self.memory.add_message({
                        "role": "assistant", 
                        "content": f"[RECOVERY THINKING] {recovery_thinking}"
                    })
                    
                    self.logger.log(f"[Agent:{self.name}] Recovery thinking complete, retrying", {
                        "attempt": recovery_attempts
                    })
                    
                except asyncio.TimeoutError:
                    self.logger.log(f"[Agent:{self.name}] Recovery thinking timed out", {
                        "level": "error"
                    })
                    raise Exception("Recovery thinking timed out")
                
                # Wait briefly before retrying
                await asyncio.sleep(1)
                
    def _build_recovery_prompt(self, error: str, attempt: int) -> str:
        """
        Build a prompt for error recovery.
        
        Args:
            error: The error message
            attempt: The current recovery attempt number
            
        Returns:
            A prompt for recovery
        """
        return f"""
I encountered an error during execution: {error}

This is recovery attempt {attempt}. Please help me recover from this error by:

1. Analyzing what went wrong
2. Suggesting an alternative approach 
3. Providing a specific plan to overcome this issue

Be specific and precise in your recovery plan. Consider:
- Were there incorrect assumptions?
- Was there missing information?
- Was the approach incorrect?
- Is there a simpler way to achieve the goal?

Please think step by step and provide a clear recovery plan.
"""
    
    def _find_tool(self, tool_name: str) -> Optional[Tool]:
        """Find a tool by name (case-insensitive).
        
        Args:
            tool_name: Name of the tool to find
            
        Returns:
            The matching tool or None if not found
        """
        tool_name_lower = tool_name.lower()
        for tool in self.tools:
            if tool.name.lower() == tool_name_lower:
                return tool
        return None 