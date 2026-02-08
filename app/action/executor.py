# action/executor.py
from typing import Dict, List, Any

CONFIDENCE_THRESHOLD = 0.6  # same threshold as Orchestrator
HIGH_RISK_LEVELS = ["high"]

class ActionExecutor:
    """
    Converts orchestrator output into deterministic actions.
    """

    def __init__(self, confidence_threshold: float = CONFIDENCE_THRESHOLD):
        self.confidence_threshold = confidence_threshold

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Action Layer - Converts orchestrator output into deterministic actions.
        
        Args:
            context: Output from Orchestrator (includes synthesis results)
        Returns:
            dict with deterministic actions:
            {
                "action": "answer|clarify|escalate|flag",
                "message": str,
                "flagged_documents": List[str]
            }
        """
        actions: Dict[str, Any] = {
            "action": None,
            "message": "",
            "flagged_documents": []
        }

        # Always flag documents if conflict exists
        if context.get("conflict", False):
            actions["flagged_documents"] = [
                meta.get("source_file", "") for meta in context.get("metadata", [])
            ]

        # Get synthesis result (from Final Decision Synthesizer)
        synthesis = context.get("synthesis", {})
        recommendation = synthesis.get("recommendation", "")
        risks = synthesis.get("risks", [])
        tradeoffs = synthesis.get("tradeoffs", [])
        confidence_score = synthesis.get("confidence_score", 0.0)
        reasoning = synthesis.get("reasoning", "")

        # Build comprehensive message from synthesis
        message_parts = []
        if recommendation:
            message_parts.append(f"Recommendation: {recommendation}")
        if reasoning:
            message_parts.append(f"Reasoning: {reasoning}")
        if risks:
            message_parts.append(f"Risks: {', '.join(risks)}")
        if tradeoffs:
            message_parts.append(f"Tradeoffs: {', '.join(tradeoffs)}")
        if confidence_score is not None:
            message_parts.append(f"Confidence: {confidence_score:.2f}")

        # Determine action based on synthesis and context
        risk_level = context.get("risk", "medium")
        response_mode = context.get("response_mode", "direct")
        has_conflict = context.get("conflict", False)

        # Escalate conditions:
        # 1. High risk queries
        # 2. Very low confidence (< 0.3)
        # 3. High uncertainty from debate (if debate mode)
        if risk_level in HIGH_RISK_LEVELS:
            actions["action"] = "escalate"
            actions["message"] = (
                f"High-risk query detected ({risk_level}). "
                f"Recommendation: {recommendation if recommendation else 'N/A'}. "
                "Please review manually with legal/compliance team."
            )
        elif confidence_score < 0.3:
            actions["action"] = "escalate"
            actions["message"] = (
                f"Very low confidence ({confidence_score:.2f}). "
                "Escalating to human review."
            )
        elif response_mode == "debate":
            judgment = context.get("final_judgment", {})
            uncertainty = judgment.get("uncertainty", 1.0)
            if uncertainty > 0.7:
                actions["action"] = "escalate"
                actions["message"] = (
                    f"Debate resulted in high uncertainty ({uncertainty:.2f}). "
                    f"{' '.join(message_parts)}. "
                    "Please review manually."
                )
            else:
                actions["action"] = "answer"
                actions["message"] = " ".join(message_parts) if message_parts else recommendation
        elif confidence_score < self.confidence_threshold:
            # Low confidence → ask clarification
            actions["action"] = "clarify"
            actions["message"] = (
                f"System confidence is low ({confidence_score:.2f}). "
                "Could you clarify your request or provide more context?"
            )
        elif has_conflict:
            # Conflict detected → flag and answer with warning
            actions["action"] = "flag"
            actions["message"] = (
                f"⚠️ WARNING: Conflicting documents detected. "
                f"{' '.join(message_parts)}. "
                "Please review flagged documents."
            )
        else:
            # Safe to answer
            actions["action"] = "answer"
            actions["message"] = " ".join(message_parts) if message_parts else recommendation

        # Default fail-safe
        if not actions["action"]:
            actions["action"] = "clarify"
            actions["message"] = "Unable to determine response. Please clarify your request."

        return actions
