from datetime import datetime
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from app.core.dependencies import llm

from app.graph.prompts.generation_prompt import generation_prompt
from app.graph.state import ChatState
from app.utils.timer import time_node


@time_node
async def generate_answer(state: ChatState):
    """
    Generates an answer based on the context and the user's query,
    and correctly updates the message history.
    """
    context = state.get("context", [])
    messages = state["messages"]
    
    # Use rewritten_query if available, otherwise use the original message
    #if state.get("rewritten_query"):
    #question = state["rewritten_query"]
    #else:
    question = messages[-1].content

    # Generate current date information
    now = datetime.now()
    current_date_str = f"Today's date is {now.strftime('%A, %B %d, %Y')}. Year: {now.year}, Month: {now.strftime('%B')}."


    chain = generation_prompt | llm | StrOutputParser()

    answer = await chain.ainvoke({
        "context": context, 
        "question": question, 
        "history": messages[-5:-1],
        "language": state.get("language"),
        "current_date": current_date_str
    })

    new_ai_message = AIMessage(content=answer)

    # If the last message was from the AI, replace it (retry mechanism)
    if messages and isinstance(messages[-1], AIMessage):
        messages[-1] = new_ai_message
    else:
        messages.append(new_ai_message)

    return {"messages": messages}
