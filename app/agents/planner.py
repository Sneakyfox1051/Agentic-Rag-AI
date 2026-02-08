# planner/planner.py
import json
from typing import Dict, Literal
from dataclasses import dataclass


IntentType = Literal[
    "information_lookup",
    "policy_decision",
    "procedural_guidance",
    "compliance_check",
    "unknown"
]

RiskLevel = Literal["low", "medium", "high"]


@dataclass
class PlannerOutput:
    intent: IntentType
    risk: RiskLevel
    needs_retrieval: bool

    def to_dict(self) -> Dict:
        return {
            "intent": self.intent,
            "risk": self.risk,
            "needs_retrieval": self.needs_retrieval
        }


class PlannerAgent:
    def __init__(self, llm_client):
        """
        llm_client must expose:
        generate(prompt: str) -> str
        """
        self.llm = llm_client

    def plan(self, user_query: str) -> Dict:
        prompt = self._build_prompt(user_query)
        raw_output = self.llm.generate(prompt)

        parsed = self._parse_json(raw_output)
        validated = self._validate(parsed)

        return validated.to_dict()

    def _build_prompt(self, query: str) -> str:
        return f"""
You are a Planner Agent in an enterprise AI system.

Your job is to classify a user query.

USER QUERY:
"{query}"

Return ONLY a valid JSON object.
DO NOT include explanations, markdown, or extra text.

JSON SCHEMA (strict):
{{
  "intent": one of [
    "information_lookup",
    "policy_decision",
    "procedural_guidance",
    "compliance_check",
    "unknown"
  ],
  "risk": one of ["low", "medium", "high"],
  "needs_retrieval": boolean
}}

Classification rules:
- policy decisions, legal, compliance, HR, finance → risk = high
- unclear or ambiguous intent → risk = medium
- factual lookups → risk = low
- needs_retrieval = true if internal documents are required
"""

    def _parse_json(self, raw: str) -> Dict:
        """
        Hard JSON extraction.
        """
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError(f"Planner output is not valid JSON: {raw}")

    def _validate(self, data: Dict) -> PlannerOutput:
        """
        Enforces schema + value constraints.
        """
        required_keys = {"intent", "risk", "needs_retrieval"}

        if not required_keys.issubset(data.keys()):
            raise ValueError(f"Missing keys in planner output: {data}")

        intent = data["intent"]
        risk = data["risk"]
        needs_retrieval = data["needs_retrieval"]

        if intent not in PlannerOutput.__annotations__["intent"].__args__:
            intent = "unknown"

        if risk not in ("low", "medium", "high"):
            risk = "medium"

        if not isinstance(needs_retrieval, bool):
            needs_retrieval = True

        return PlannerOutput(
            intent=intent,
            risk=risk,
            needs_retrieval=needs_retrieval
        )
