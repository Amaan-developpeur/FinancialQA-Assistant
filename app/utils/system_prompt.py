def system_prompt(context_chunks, question):
    context = ""
    for index, chunk in enumerate(context_chunks):
        context += f"### Chunk {index+1} (Page {chunk['page']} of {chunk['filename']}):\n{chunk['text']}\n\n"

    prompt = f"""
You are a financial question-answering assistant working with company annual reports.

Only use the information provided in the context below to answer the question. Do not guess. 
If the answer cannot be found, respond with: "Not found in the documents."

-----------------------
Context:
{context}
-----------------------

Question: {question}

Answer:"""

    return prompt.strip()
