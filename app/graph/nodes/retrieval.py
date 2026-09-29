from ssl import SSLError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from app.graph.state import ChatState
from app.core.dependencies import vector_store  # Import the shared vector_store instance
from app.utils.timer import time_node

# --- 4. NODE : RETRIEVAL ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((TimeoutError, SSLError))
)
@time_node
async def retrieve_documents(state: ChatState, config):


    # Use rewritten_query if available, otherwise use the original message
    if state.get("rewritten_query"):
        query = state["rewritten_query"]
    else:
        query = state["messages"][-1].content

    docs = await vector_store.asimilarity_search(
        query,
        k=6
        
    )
    return {"context": docs}
