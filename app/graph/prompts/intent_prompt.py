from langchain_core.prompts import PromptTemplate

INTENT_PROMPT_TEMPLATE = """
**Your Role:** You are an AI routing system, an expert in RAG (Retrieval-Augmented Generation) strategies. Your function is to analyze user queries to determine the best processing approach.
**User messages can be in French or English.**

**Conversation History:**
```
{history}
```

**Last User Message:**
```
{question}
```

**Your Tasks:**

1.  **Classify Intent:** Categorize the user's message into one of the following two intents:
    *   `need_retrieval`: The user's query requires a search for information in the knowledge base (e.g., questions about documents, policies, procedures, technical data, etc.).
    *   `small_talk`: The user is engaging in informal conversation, greetings, or expressing gratitude (e.g., "Hello", "How are you?", "Thanks for your help!").

2.  **Detect Language:** Identify the language of the user's message.
    *   Set `language` to `"french"` if the message is in French.
    *   Set `language` to `"english"` if the message is in English.

3.  **Determine if Retrieval is Needed (`needs_retrieval`):**
    *   Set to `true` if the intent is `need_retrieval`.
    *   Set to `false` if the intent is `small_talk`.

4.  **Rewrite the Query (`rewritten_query`):**
    *   If `needs_retrieval` is `true`, rewrite the user's message into a clear and concise query, optimized for vector search. **The rewritten query must be in English.** Remove pleasantries and focus on the main question.
    *   If `needs_retrieval` is `false`, return an empty string.

**Output Format:** Respond with a valid JSON object. Do not add any comments or explanations.

**Example:**
User Message: "Salut, je me demandais quelle est la politique de l'entreprise concernant le congé paternité. Merci !"
```json
{{
  "intent": "need_retrieval",
  "language": "french",
  "needs_retrieval": true,
  "rewritten_query": "paternity leave policy"
}}
```

**Your Answer:**
"""

intent_prompt = PromptTemplate.from_template(INTENT_PROMPT_TEMPLATE)
