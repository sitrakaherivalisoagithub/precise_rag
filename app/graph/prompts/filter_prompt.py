from langchain_core.prompts import PromptTemplate


FILTER_PROMPT_TEMPLATE = """
You are an expert in evaluating the relevance of documents to a user query.
Your task is to filter a list of retrieved documents based on the user's question and conversation history.
The goal is to return only the documents that are highly relevant to the user's last question.

Conversation history:
{chat_history}

Last user question:
{query}

Retrieved documents:
{context}

Carefully analyze each document and its content.
Return a list of indices of the most relevant documents for the last user question.
If no document is relevant, return an empty list.
"""

filter_prompt = PromptTemplate.from_template(FILTER_PROMPT_TEMPLATE)
