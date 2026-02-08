# app/mock_setup.py
"""
Mock setup for testing/demo purposes.
Replace with actual LLM client and vector store for production.
"""
from unittest.mock import MagicMock
from app.agents.planner import PlannerAgent
from app.retrieval.retriever import Retriever, VectorStore
from app.agents.evaluator import KnowledgeEvaluator
from app.debate.pro_agent import ProAgent
from app.debate.contra_agent import ContraAgent
from app.debate.judge_agent import JudgeAgent
from app.synthesis.decision_synthesizer import FinalDecisionSynthesizer
from app.orchestration.graph import Orchestrator
from app.action.executor import ActionExecutor
from datetime import datetime

class MockLLM:
    """Mock LLM client for demo purposes"""
    def generate(self, prompt: str) -> str:
        if "Planner Agent" in prompt:
            return '{"intent": "policy_decision", "risk": "high", "needs_retrieval": true}'
        if "contradiction detection" in prompt:
            return '{"conflict": true}'
        if "Pro Agent" in prompt:
            return '{"argument": "Support policy", "evidence": ["#1"]}'
        if "Contra Agent" in prompt:
            return '{"risks": ["High risk"], "contradictions": ["Policy contradicts previous"]}'
        if "Judge Agent" in prompt:
            return '{"winner": "contra", "reasoning": "Contra arguments stronger", "uncertainty": 0.2}'
        if "Final Decision Synthesizer" in prompt:
            return '{"recommendation": "Proceed with caution", "risks": ["High risk"], "tradeoffs": ["Tradeoff 1"], "confidence_score": 0.5, "reasoning": "Based on debate results"}'
        return '{"conflict": false}'

def create_mock_orchestrator():
    """Create orchestrator with mock components"""
    llm = MockLLM()
    
    planner_agent = PlannerAgent(llm)
    vector_store = MagicMock(spec=VectorStore)
    retriever = Retriever(vector_store, MagicMock())
    
    # Mock retriever to return sample data
    retriever.retrieve = MagicMock(return_value={
        "chunks": [
            "Leave policy allows 20 days per year for full-time employees.",
            "Policy updated in 2024. Previous policy allowed 15 days."
        ],
        "scores": [0.9, 0.8],
        "metadata": [
            {"source_file": "hr_policy_2024.pdf", "ingested_at": datetime.utcnow().isoformat()},
            {"source_file": "hr_policy_2023.pdf", "ingested_at": datetime(2023, 1, 1).isoformat()}
        ]
    })
    
    evaluator = KnowledgeEvaluator(llm)
    pro_agent = ProAgent(llm)
    contra_agent = ContraAgent(llm)
    judge_agent = JudgeAgent(llm)
    synthesizer = FinalDecisionSynthesizer(llm)

    orchestrator = Orchestrator(
        planner=planner_agent,
        retriever=retriever,
        evaluator=evaluator,
        pro_agent=pro_agent,
        contra_agent=contra_agent,
        judge_agent=judge_agent,
        synthesizer=synthesizer
    )
    
    return orchestrator
