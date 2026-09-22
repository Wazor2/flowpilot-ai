import os
import json
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError
from agents.state import State, PlanStep
from backend.tools import registry
import time

def get_tools_description() -> str:
    desc = []
    for tool_name, tool_def in registry._tools.items():
        schema_str = json.dumps(tool_def.inputSchema, indent=2)
        desc.append(f"Tool: {tool_name}\nDescription: {tool_def.description}\nRequires Approval: {tool_def.requiresApproval}\nInput Schema:\n{schema_str}\n")
    return "\n".join(desc)

def planner_node(state: State) -> State:
    # If the workflow is already planned and we are not replanning due to failure, skip
    if state.status in ["EXECUTE", "APPROVED"] and not state.failures:
        return state
        
    tools_desc = get_tools_description()
    
    completed_actions_str = json.dumps([a.model_dump() for a in state.completed_actions], indent=2)
    failures_str = json.dumps(state.failures, indent=2)
    
    system_prompt = f"""You are a workflow planner AI. Your job is to select the next steps to achieve the user's objective.
    
Available Tools:
{tools_desc}

You must respond with a JSON array of steps. Each step must have:
- "tool": the name of the tool to execute
- "arguments": a JSON object containing the arguments for the tool, matching its schema exactly
- "reason": why this tool is being used
- "requires_approval": boolean, true if the tool requires approval (action-taking)

If the objective is already fully achieved based on the completed actions, you MUST return an empty JSON array `[]`.
Do NOT include markdown formatting or backticks around your JSON response. Just the raw JSON array.
"""

    user_prompt = f"""Objective: {state.objective}

Completed Actions:
{completed_actions_str}

Recent Failures:
{failures_str}

Given this context, what are the next steps to take?
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    models = ["gemini-flash-latest", "gemini-pro-latest", "gemini-flash-lite-latest"]
    response = None
    for attempt in range(3):
        for model_name in models:
            try:
                print(f"Trying model: {model_name}...")
                llm = ChatGoogleGenerativeAI(model=model_name, temperature=0, max_retries=1)
                response = llm.invoke(messages)
                break
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                time.sleep(2)
        if response is not None:
            break
        print("All models failed on this attempt, retrying in 5 seconds...")
        time.sleep(5)
    
    if response is None:
        state.status = "FAILED"
        state.failures.append({"error": "Planning failed: All models returned 503 or errors."})
        return state
    
    # Parse the response
    try:
        raw_content = response.content
        if isinstance(raw_content, list):
            raw_content = "".join([part.get("text", "") for part in raw_content if isinstance(part, dict) and "text" in part])
        elif not isinstance(raw_content, str):
            raw_content = str(raw_content)
            
        raw_content = raw_content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:-3]
        elif raw_content.startswith("```"):
            raw_content = raw_content[3:-3]
            
        steps_data = json.loads(raw_content)
        new_plan = []
        for s in steps_data:
            step = PlanStep(
                tool=s.get("tool"),
                arguments=s.get("arguments", {}),
                reason=s.get("reason", ""),
                requires_approval=s.get("requires_approval", False)
            )
            # Enforce requires_approval based on registry
            tool_def = registry.get_tool(step.tool)
            if tool_def and tool_def.requiresApproval:
                step.requires_approval = True
            new_plan.append(step)
            
        if not new_plan:
            state.status = "COMPLETED"
        else:
            state.plan = new_plan
            state.current_step_index = 0
            state.status = "EXECUTE"
            # Clear failures after replanning
            state.failures = []
    except Exception as e:
        print(f"Failed to parse LLM plan: {e}")
        state.status = "FAILED"
        state.failures.append({"error": f"Planning failed: {str(e)}", "response": response.content})
        
    return state
