from ollama import chat

MODEL = "qwen3.5:4b"


def ask_llm(question: str, data_context: str) -> str:

    prompt = f"""
You are InsightForge, a business data analyst.

Answer the user's question using ONLY the verified business data below.

Rules:
- Give ONE final answer.
- Do not show reasoning.
- Do not think aloud.
- Do not provide multiple possible answers.
- Do not invent numbers.
- If the data does not answer the question, say so.
- Keep the answer concise.
- Start directly with the answer.

VERIFIED BUSINESS DATA:

{data_context}


USER QUESTION:

{question}


FINAL ANSWER:
"""

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        think=False,
        options={
            "temperature": 0.2,
            "num_predict": 120,
        }
    )

    return response.message.content.strip()