# app/llm/prompt_builder.py
def build_prompt(chunks, question):
    """
    Build a concise, context-aware prompt for financial QA.
    """
    context = ""
    for i, ch in enumerate(chunks, 1):
        context += f"### Chunk {i} (Page {ch['page']} – {ch['filename']}):\n{ch['text']}\n\n"

    prompt = f"""
You are a financial analysis assistant.

Use only the context below to answer the question.
Do not speculate; if not found, reply "Not found in the documents."

--------------------------
Context:
{context}
--------------------------

Question: {question}

Answer:
""".strip()
    return prompt
