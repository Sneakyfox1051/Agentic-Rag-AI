# debate/pro_agent.py
from typing import List, Dict
import json

class ProAgent:
    def __init__(self, llm_client):
        """
        llm_client: must implement generate(prompt: str) -> str
        """
        self.llm = llm_client

    def argue(self, decision: str, context_chunks: List[str]) -> Dict:
        """
        Args:
            decision: proposed decision / recommendation
            context_chunks: retrieved documents / knowledge

        Returns:
            dict: {"argument": str, "evidence": List[str]}
        """
        prompt = f"""
You are the Pro Agent arguing FOR a decision in an enterprise setting.

Decision to support:
"{decision}"

Use ONLY the provided context chunks.
Cite evidence explicitly using [#] notation (matching chunk number).

Context chunks:
"""
        for i, chunk in enumerate(context_chunks):
            prompt += f"\n[{i+1}] {chunk}\n"

        prompt += """
Rules:
- Construct a coherent argument supporting the decision
- Include citations in [#] format
- Return ONLY valid JSON, no explanations
- JSON format:
{
  "argument": "...",
  "evidence": ["#1", "#3"]
}
"""

        raw = self.llm.generate(prompt)
        try:
            return json.loads(raw)
        except Exception:
            # Fail-safe: return minimal structure
            return {"argument": "", "evidence": []}
