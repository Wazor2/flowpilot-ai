from langgraph.graph import StateGraph, START, END
from .state import State
from .nodes.planner import planner_node
from .nodes.executor import executor_node


def route_next_node(state: State) -> str:
    if state.status in {"COMPLETED", "FAILED", "WAITING_FOR_APPROVAL", "PAUSED"}:
        return END
    if state.status == "REPLAN":
        return "planner"
    return "executor"


def create_workflow_graph():
    builder = StateGraph(State)
    builder.add_node("planner", planner_node)
    builder.add_node("executor", executor_node)
    builder.add_edge(START, "planner")
    builder.add_conditional_edges("planner", route_next_node, {"executor": "executor", END: END})
    builder.add_conditional_edges("executor", route_next_node, {"executor": "executor", "planner": "planner", END: END})
    return builder.compile()
