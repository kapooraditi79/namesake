"""Step 1 of building LLMAgent: prove we can query a local Ollama model.

Throwaway script -- not part of the harness yet. Delete or fold into
agents/llm_agent.py once the full loop (query -> parse -> execute) works
standalone. Run manually: python experiments/step1_query_lm.py
"""

from openai import OpenAI

MODEL = "qwen2.5-coder:7b"

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Ollama ignores this, but the client requires something
)


def query_lm(messages: list[dict]) -> str:
    # query the model and return the model msges
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content


TEXT= "what are qwen-2.5-coder-7b's benchmarks with agentic and coding tasks"
if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": TEXT},
    ]
    print(query_lm(messages))
