from typing import Literal

from pydantic import BaseModel, Field
from app.core.dependencies import llm

from app.graph.prompts.intent_prompt import intent_prompt
from app.graph.state import  ChatState
from app.utils.timer import time_node


class IntentAnalysis(BaseModel):
    intent: Literal["need_retrieval", "small_talk"] = Field(
        description="The classified intent of the user's query."
    )
    language: Literal["french", "english"] = Field(
        description="The detected language of the user's message."
    )
    needs_retrieval: bool = Field(
        description="Whether a document search is necessary to answer the query."
    )
    rewritten_query: str = Field(
        description="The user's query, rewritten for optimal vector search."
    )


@time_node
async def analyze_intent(state: ChatState):
    """
    Analyze the user's intent and rewrite the query if necessary.
    """
    history = state["messages"][-7:-1]
    user_message = state["messages"][-1].content

    structured_llm = llm.with_structured_output(IntentAnalysis)

    chain = intent_prompt | structured_llm

    result = await chain.ainvoke({"question": user_message, "history": history})

    return {
        "intent": result.intent,
        "language": result.language,
        "rewritten_query": result.rewritten_query,
        "needs_retrieval": result.needs_retrieval
    }
