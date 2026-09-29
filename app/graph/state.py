from typing import List
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage


# --- 1. LE STATE ---
# We now manage the message list manually to allow replacing messages on retry.

class ChatState(TypedDict):
    messages: List[BaseMessage]
    context: list
    intent: str
    language: str
    rewritten_query: str
    needs_retrieval: bool
