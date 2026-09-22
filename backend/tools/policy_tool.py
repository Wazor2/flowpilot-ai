from typing import Dict, Any
from ..tool_registry import ToolResult, ToolContext

def get_policy_execute(input_data: Dict[str, Any], context: ToolContext) -> ToolResult:
    policy_type = input_data.get("policy_type")
    if not policy_type:
        return ToolResult(status="FAILED", error="Missing policy_type")
        
    # Mocking database/storage retrieval
    if policy_type == "payment_terms":
        return ToolResult(status="SUCCESS", data={
            "content": "Standard payment terms are Net 30. Overdue accounts after 60 days require collection notice."
        })
    elif policy_type == "communication":
        return ToolResult(status="SUCCESS", data={
            "content": "Emails must be professional and include standard legal disclaimers. Attempt primary contact first, then alternate billing contacts."
        })
        
    return ToolResult(status="FAILED", error=f"Policy {policy_type} not found")
