# Populated in F4 - Agentic Multi-hop Reasoning

from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.agent.nodes import router_node, decomposer_node, rag_retrieve_node


class AgentState(TypedDict):
    question: str
    provider: str
    top_k: int
    route: str                    # set by router_node: "simple" | "complex"
    sub_questions: list[str]      # set by decomposer_node
    retrieved_chunks: list[dict]  # set by rag_retrieve_node
    hop_traces: list[dict]        # each node appends one entry


def _route_decision(state: AgentState) -> str:
    """Tell LangGraph which node to go to after the router."""
    return "decomposer" if state.get("route") == "complex" else "rag_retrieve"


def build_graph():
    graph = StateGraph(AgentState)

    # Register nodes: add_node("name", function_to_call)
    # "name" is used to reference the node in edges below
    graph.add_node("router", router_node)
    graph.add_node("decomposer", decomposer_node)
    graph.add_node("rag_retrieve", rag_retrieve_node)

    # Entry point: always start at router
    # START is a LangGraph constant meaning "beginning of graph"
    graph.add_edge(START, "router")

    # Conditional edge after router:
    # add_conditional_edges(source, path_fn, path_map)
    # source   → "router": evaluate condition after this node finishes
    # path_fn  → _route_decision: called with current state, returns a string
    # path_map → maps that string to the actual node to go to next
    #   "decomposer"  → go to decomposer node (complex question)
    #   "rag_retrieve"→ go to rag_retrieve node (simple question)
    graph.add_conditional_edges("router", _route_decision, {
        "decomposer": "decomposer",
        "rag_retrieve": "rag_retrieve",
    })

    # Fixed edge: add_edge(source, destination)
    # After decomposer always go to rag_retrieve — no branching needed
    graph.add_edge("decomposer", "rag_retrieve")

    # Fixed edge: after rag_retrieve the graph is done
    # END is a LangGraph constant meaning "stop here"
    graph.add_edge("rag_retrieve", END)

    # compile() validates the graph (no dead ends, all nodes reachable)
    # and locks it into a runnable object
    return graph.compile()


compiled_graph = build_graph()