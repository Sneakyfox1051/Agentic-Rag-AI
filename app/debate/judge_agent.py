# debate/judge_agent.py
from typing import Dict
import json

class JudgeAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def judge(self, pro: Dict, contra: Dict) -> Dict:
        """
        Args:
            pro: {"argument": str, "evidence": List[str]}
            contra: {"risks": List[str], "contradictions": List[str]}

        Returns:
            dict: {"winner": "pro"|"contra"|"tie", "reasoning": str, "uncertainty": float}
        """
        prompt = f"""
You are the Judge Agent. Compare arguments from Pro and Contra agents.

Pro argument and evidence:
{json.dumps(pro, indent=2)}

Contra arguments:
{json.dumps(contra, indent=2)}

Rules:
- Decide which side is stronger: "pro", "contra", or "tie"
- Provide reasoning
- Estimate uncertainty (0.0 = certain, 1.0 = highly uncertain)
- Return ONLY valid JSON

JSON format:
{{
  "winner": "pro"|"contra"|"tie",
  "reasoning": "...",
  "uncertainty": 0.0
}}
"""
        raw = self.llm.generate(prompt)
        try:
            return json.loads(raw)
        except Exception:
            return {"winner": "tie", "reasoning": "", "uncertainty": 1.0}
