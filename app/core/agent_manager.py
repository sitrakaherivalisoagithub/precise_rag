from app.graph.workflow import build_graph
from app.graph.state import ChatState
from langgraph.checkpoint.memory import InMemorySaver

class AgentManager:
    """
    Manages the lifecycle of a compiled LangGraph agent as a singleton.
    """
    def __init__(self):
        self.graph = build_graph()
        self.checkpointer = None
        self.compiled_graph = None

    async def setup(self):
        """
        Initializes checkpointer, and compiles the graph.
        This should be called once at application startup.
        """
        if self.compiled_graph is not None:
            print("AgentManager is already initialized.")
            return

        print("Initializing AgentManager...")
       
        self.checkpointer = InMemorySaver()
        
        # Compile the graph with the checkpointer
        self.compiled_graph = self.graph.compile(checkpointer=self.checkpointer)
        print("AgentManager initialized successfully.")

    async def close(self):
        """
        Closes the database connection.
        This should be called once at application shutdown.
        """
        if self.checkpointer:
            self.checkpointer = None
            self.compiled_graph = None
            print("AgentManager resources cleaned up.")

    async def get_state(self, session_id: str) -> dict:
        """
        Retrieves the current state for a given session ID.
        """
        if not self.compiled_graph:
            raise RuntimeError("AgentManager not initialized.")
        
        config = {"configurable": {"thread_id": session_id}}
        state = await self.compiled_graph.aget_state(config)
        return state.values if state else {}

    async def invoke(self, state: ChatState, session_id: str) -> dict:
        """
        Invokes the compiled graph with the given state and session ID.
        """
        if self.compiled_graph is None:
            raise RuntimeError("AgentManager is not initialized. Call setup() first.")

        print(f"Invoking graph for session: {session_id}")
        config = {"configurable": {"thread_id": session_id or "default"}}

        if isinstance(state, dict):
            state = ChatState(**state)

        print(f"Input state for session {session_id}: {state}")
        result = await self.compiled_graph.ainvoke(state, config)

        if hasattr(result, 'dict'):
            result = result.dict()

        print(f"Graph result for session {session_id}: {result}...")
        return result
