from app.graph.state import ChatState
from app.graph.nodes.intent_analysis import analyze_intent
from app.graph.nodes.retrieval import retrieve_documents
from app.graph.nodes.generation import generate_answer
from app.graph.nodes.document_filter import filter_documents

from langgraph.graph import StateGraph, END, START


def should_retrieve(state: ChatState):
    """
    Determines whether to retrieve documents based on the intent analysis.
    """
    return "retrieve" if state.get("needs_retrieval") else "generate"


# --- GRAPH CONSTRUCTION ---

def build_graph():

    workflow = StateGraph(ChatState)

    workflow.add_node("analyze_intent", analyze_intent)
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("generate", generate_answer)
    workflow.add_node("filter", filter_documents)

    workflow.add_edge(START, "analyze_intent")

    workflow.add_conditional_edges(
        "analyze_intent",
        should_retrieve,
        {
            "retrieve": "retrieve",
            "generate": "generate",
        },
    )

    workflow.add_edge("retrieve", "filter")
    workflow.add_edge("filter", "generate")
    workflow.add_edge("generate", END)

    return workflow

