# retrieval/query_rewrite.py
from typing import List


class QueryRewriter:
    def __init__(self, llm_client):
        """
        llm_client: any callable with `.generate(prompt: str) -> str`
        """
        self.llm = llm_client

    def rewrite(self, query: str, n: int = 3) -> List[str]:
        prompt = f"""
You are a query rewriting engine for a retrieval system.

Original query:
"{query}"

Generate {n} semantically equivalent search queries.
Rules:
- Do NOT answer the question
- Do NOT add new information
- Preserve intent
- Each query on a new line
"""

        raw_output = self.llm.generate(prompt)

        rewrites = [
            line.strip("-• ").strip()
            for line in raw_output.split("\n")
            if line.strip()
        ]

        # Fallback safety
        if not rewrites:
            rewrites = [query]

        return rewrites[:n]
