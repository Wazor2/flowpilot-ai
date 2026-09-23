import os
import json
import subprocess
from typing import List, Dict, Any
from agents.state import State, PlanStep
from backend.tools import registry

def get_tools_dictionary() -> Dict[str, Any]:
    tools_dict = {}
    for tool_name, tool_def in registry._tools.items():
        tools_dict[tool_name] = {
            "name": tool_name,
            "description": tool_def.description,
            "inputSchema": tool_def.inputSchema,
            "requiresApproval": tool_def.requiresApproval
        }
    return tools_dict

def planner_node(state: State) -> State:
    # If the workflow is already planned and we are not replanning due to failure, skip
    if state.status in ["EXECUTE", "APPROVED"] and not state.failures:
        return state
        
    tools_dict = get_tools_dictionary()
    completed_actions = [a.model_dump() for a in state.completed_actions]
    failures = state.failures
    
    payload = {
        "objective": state.objective,
        "completed_actions": completed_actions,
        "failures": failures,
        "tools": tools_dict
    }
    
    payload_str = json.dumps(payload)
    
    # Run the TS CLI adapter
    cli_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src", "ai", "cli.js")
    
    import tempfile
    
    try:
        # Create a temporary file to hold the JSON payload
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_file.write(payload_str)
            temp_file_path = temp_file.name

        print(f"Calling TS AI Orchestrator via CLI: {cli_path}")
        result = subprocess.run(
            ["node", cli_path, temp_file_path],
            text=True,
            capture_output=True,
            check=True,
            shell=True
        )
        
        # Clean up temp file
        try:
            os.remove(temp_file_path)
        except OSError:
            pass
            
        stdout_str = result.stdout
        # Extract only the JSON part to ignore dotenv's stdout logs
        if "{" in stdout_str:
            json_str = stdout_str[stdout_str.find("{"):]
            output_json = json.loads(json_str)
        else:
            raise ValueError(f"No JSON found in stdout: {stdout_str}")
        
        if output_json.get("status") == "SUCCESS":
            steps_data = output_json.get("steps", [])
            
            new_plan = []
            for s in steps_data:
                # The TS code uses `action`, but Python state uses `reason`. Adapt if necessary.
                reason_str = s.get("action") or s.get("reason", "")
                
                step = PlanStep(
                    tool=s.get("tool"),
                    arguments=s.get("arguments", {}),
                    reason=reason_str,
                    requires_approval=s.get("requiresApproval", False)
                )
                
                # Enforce requires_approval based on registry (defense in depth)
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
        else:
            print("CLI Returned FAILED:", output_json)
            state.status = "FAILED"
            state.failures.append({"error": output_json.get("message", "Unknown TS error"), "code": output_json.get("error")})
            
    except subprocess.CalledProcessError as e:
        print(f"TS CLI failed: {e.stderr}")
        state.status = "FAILED"
        
        # Try to parse stdout for error JSON if available
        try:
            err_json = json.loads(e.stdout)
            err_msg = err_json.get("message", e.stderr)
        except:
            err_msg = e.stderr or str(e)
            
        state.failures.append({"error": f"Planning failed: {err_msg}"})
    except Exception as e:
        print(f"Failed to execute planner CLI: {e}")
        state.status = "FAILED"
        state.failures.append({"error": f"Planning execution failed: {str(e)}"})
        
    return state
