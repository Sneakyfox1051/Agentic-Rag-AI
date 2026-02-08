# debate/contra_agent.py
from typing import List, Dict
import json

class ContraAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def argue(self, decision: str, context_chunks: List[str]) -> Dict:
        """
        Args:
            decision: proposed decision / recommendation
            context_chunks: retrieved knowledge

        Returns:
            dict: {"risks": List[str], "contradictions": List[str]}
        """
        prompt = f"""
You are the Contra Agent arguing AGAINST a proposed decision.

Decision:
"{decision}"

Use ONLY the provided context chunks.
Identify potential risks and highlight contradictions.
Avoid repeating the same points.

Return ONLY valid JSON.

JSON format:
{{
  "risks": ["..."],
  "contradictions": ["..."]
}}

Context chunks:
"""
        for i, chunk in enumerate(context_chunks):
            prompt += f"\n[{i+1}] {chunk}\n"

        raw = self.llm.generate(prompt)
        try:
            return json.loads(raw)
        except Exception:
            return {"risks": [], "contradictions": []}
