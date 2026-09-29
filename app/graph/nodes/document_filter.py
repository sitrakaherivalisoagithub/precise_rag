from typing import List
from pydantic import BaseModel, Field

from app.graph.prompts.filter_prompt import filter_prompt
from app.core.dependencies import llm
from app.graph.state import ChatState
from app.utils.timer import time_node


# --- 5. NODE : DOCUMENT FILTER ---
class FilteredDocs(BaseModel):
    """A list of documents that are relevant to the query."""
    relevant_documents: List[int] = Field(
        description="A list of indices of the documents that are relevant to the user's query."
    )


@time_node
async def filter_documents(state: ChatState, config):
    """
    Filter the retrieved documents using a powerful LLM to ensure relevance.
    """
    query = state["messages"][-1].content
    chat_history = "\n".join([f"{msg.type}: {msg.content}" for msg in state["messages"][-5:-1]])
    documents = state["context"]

    if not documents:
        return {"context": []}
    print(f"\n========== len docs before filter: {len(documents)} ======== \n")
    formatted_docs = "\n\n".join([f"--- Document index: {i} ---\n{doc.page_content}" for i, doc in enumerate(documents)])


    # Using a structured output chain to get a list of indices
    parser = llm.with_structured_output(FilteredDocs)
    chain = filter_prompt | parser

    result = await chain.ainvoke(
        {
            "chat_history": chat_history,
            "query": query,
            "context": formatted_docs,
        },
        config=config,
    )

    # Filter the documents based on the indices returned by the LLM
    relevant_docs = [documents[i] for i in result.relevant_documents if i < len(documents)]
    print(f"\n======= len docs after filter: {len(relevant_docs)} ========= \n")

    return {"context": relevant_docs}
