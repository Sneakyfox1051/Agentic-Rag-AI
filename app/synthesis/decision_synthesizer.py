# synthesis/decision_synthesizer.py
from typing import Dict, Any, Optional
import json


class FinalDecisionSynthesizer:
    """
    Final Decision Synthesizer - Combines debate results or direct evaluation
    into a final recommendation with risks, tradeoffs, and confidence score.
    """
    
    def __init__(self, llm_client):
        """
        llm_client must expose:
        generate(prompt: str) -> str
        """
        self.llm = llm_client
    
    def synthesize(
        self,
        context: Dict[str, Any],
        debate_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes final decision from either:
        - Debate mode: Uses judge's decision + pro/contra arguments
        - Direct mode: Uses evaluator's confidence + retrieved knowledge
        
        Args:
            context: Full context from orchestrator (includes chunks, confidence, etc.)
            debate_result: Optional debate results if debate mode was used
            
        Returns:
            dict: {
                "recommendation": str,
                "risks": List[str],
                "tradeoffs": List[str],
                "confidence_score": float,
                "reasoning": str
            }
        """
        if debate_result:
            return self._synthesize_from_debate(context, debate_result)
        else:
            return self._synthesize_from_direct(context)
    
    def _synthesize_from_debate(
        self,
        context: Dict[str, Any],
        debate_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesizes decision from debate council results.
        """
        pro_result = context.get("pro_result", {})
        contra_result = context.get("contra_result", {})
        judgment = context.get("final_judgment", {})
        chunks = context.get("chunks", [])
        user_query = context.get("user_query", "")
        
        prompt = f"""
You are the Final Decision Synthesizer in an enterprise AI system.

Your task is to synthesize a final recommendation from a multi-agent debate.

USER QUERY:
"{user_query}"

DEBATE RESULTS:
Judge's Decision: {judgment.get("winner", "tie")}
Judge's Reasoning: {judgment.get("reasoning", "")}
Uncertainty: {judgment.get("uncertainty", 1.0)}

Pro Agent Arguments:
{json.dumps(pro_result, indent=2)}

Contra Agent Arguments:
{json.dumps(contra_result, indent=2)}

RETRIEVED KNOWLEDGE:
"""
        for i, chunk in enumerate(chunks[:5]):
            prompt += f"\n[{i+1}] {chunk}\n"
        
        prompt += """
Synthesize a final recommendation that includes:
1. Clear recommendation/answer
2. Identified risks
3. Tradeoffs to consider
4. Confidence score (0.0-1.0)
5. Reasoning for the recommendation

Return ONLY valid JSON. No explanations.

JSON FORMAT:
{
  "recommendation": "...",
  "risks": ["risk1", "risk2"],
  "tradeoffs": ["tradeoff1", "tradeoff2"],
  "confidence_score": 0.85,
  "reasoning": "..."
}
"""
        
        raw = self.llm.generate(prompt)
        try:
            result = json.loads(raw)
            # Ensure all required fields exist
            result.setdefault("recommendation", "")
            result.setdefault("risks", [])
            result.setdefault("tradeoffs", [])
            result.setdefault("confidence_score", judgment.get("uncertainty", 1.0))
            result.setdefault("reasoning", judgment.get("reasoning", ""))
            return result
        except Exception:
            # Fallback to judgment-based synthesis
            return {
                "recommendation": judgment.get("reasoning", "Unable to determine recommendation"),
                "risks": contra_result.get("risks", []),
                "tradeoffs": [],
                "confidence_score": 1.0 - judgment.get("uncertainty", 1.0),
                "reasoning": judgment.get("reasoning", "")
            }
    
    def _synthesize_from_direct(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes decision from direct evaluation (high confidence path).
        """
        chunks = context.get("chunks", [])
        confidence = context.get("confidence", 0.0)
        freshness = context.get("freshness", 0.0)
        user_query = context.get("user_query", "")
        intent = context.get("intent", "unknown")
        risk = context.get("risk", "medium")
        
        prompt = f"""
You are the Final Decision Synthesizer in an enterprise AI system.

Your task is to synthesize a final recommendation from high-confidence retrieved knowledge.

USER QUERY:
"{user_query}"

INTENT: {intent}
RISK LEVEL: {risk}
CONFIDENCE: {confidence:.2f}
FRESHNESS: {freshness:.2f}

RETRIEVED KNOWLEDGE:
"""
        for i, chunk in enumerate(chunks[:5]):
            prompt += f"\n[{i+1}] {chunk}\n"
        
        prompt += """
Synthesize a final recommendation that includes:
1. Clear recommendation/answer based on the knowledge
2. Potential risks to consider
3. Tradeoffs if any
4. Confidence score (use the provided confidence value)
5. Reasoning

Return ONLY valid JSON. No explanations.

JSON FORMAT:
{
  "recommendation": "...",
  "risks": ["risk1", "risk2"],
  "tradeoffs": ["tradeoff1"],
  "confidence_score": 0.85,
  "reasoning": "..."
}
"""
        
        raw = self.llm.generate(prompt)
        try:
            result = json.loads(raw)
            result.setdefault("recommendation", " ".join(chunks[:3]) if chunks else "No information available")
            result.setdefault("risks", [])
            result.setdefault("tradeoffs", [])
            result.setdefault("confidence_score", confidence)
            result.setdefault("reasoning", f"Based on retrieved knowledge with confidence {confidence:.2f}")
            return result
        except Exception:
            # Fallback synthesis
            return {
                "recommendation": " ".join(chunks[:3]) if chunks else "Unable to provide recommendation",
                "risks": [] if risk == "low" else ["Medium to high risk query"],
                "tradeoffs": [],
                "confidence_score": confidence,
                "reasoning": f"Direct response based on retrieved knowledge"
            }
