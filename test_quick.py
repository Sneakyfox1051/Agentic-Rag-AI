# test_quick.py
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
from app.ingestion.models import Document
from datetime import datetime

class MockLLM:
    def generate(self, prompt: str) -> str:
        if "Planner Agent" in prompt:
            return '{"intent": "policy_decision", "risk": "high", "needs_retrieval": true}'
        if "contradiction detection" in prompt:
            return '{"conflict": true}'
        if "Pro Agent" in prompt:
            return '{"argument": "Support policy", "evidence": ["#1"]}'
        if "Contra Agent" in prompt:
            return '{"risks": ["High risk"], "contradictions": ["Policy contradicts"]}'
        if "Judge Agent" in prompt:
            return '{"winner": "contra", "reasoning": "Contra stronger", "uncertainty": 0.2}'
        if "Final Decision Synthesizer" in prompt:
            return '{"recommendation": "Proceed with caution", "risks": ["High risk"], "tradeoffs": ["Tradeoff 1"], "confidence_score": 0.5, "reasoning": "Based on debate"}'
        return '{"conflict": false}'

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Agentic RAG AI Pipeline")
    print("=" * 60)
    
    # Setup
    llm = MockLLM()
    planner = PlannerAgent(llm)
    vector_store = MagicMock(spec=VectorStore)
    retriever = Retriever(vector_store, MagicMock())
    retriever.retrieve = MagicMock(return_value={
        "chunks": ["Chunk 1: Leave policy allows 20 days per year", "Chunk 2: Policy updated in 2024"],
        "scores": [0.9, 0.8],
        "metadata": [{"source_file": "doc1.pdf", "ingested_at": datetime.utcnow().isoformat()}]
    })
    evaluator = KnowledgeEvaluator(llm)
    pro_agent = ProAgent(llm)
    contra_agent = ContraAgent(llm)
    judge_agent = JudgeAgent(llm)
    synthesizer = FinalDecisionSynthesizer(llm)

    orchestrator = Orchestrator(
        planner=planner,
        retriever=retriever,
        evaluator=evaluator,
        pro_agent=pro_agent,
        contra_agent=contra_agent,
        judge_agent=judge_agent,
        synthesizer=synthesizer
    )

    executor = ActionExecutor()

    # Test 1: High-risk query
    print("\n[TEST 1] High-Risk Query")
    print("-" * 60)
    query1 = "What is the leave policy?"
    print(f"Query: {query1}")
    
    context1 = orchestrator.run(query1)
    print(f"[OK] Response Mode: {context1.get('response_mode')}")
    print(f"[OK] Confidence: {context1.get('confidence'):.2f}")
    print(f"[OK] Risk: {context1.get('risk')}")
    print(f"[OK] Intent: {context1.get('intent')}")
    
    action1 = executor.execute(context1)
    print(f"[OK] Action: {action1['action']}")
    print(f"[OK] Message: {action1['message'][:100]}...")
    if action1['flagged_documents']:
        print(f"[OK] Flagged Documents: {action1['flagged_documents']}")

    # Test 2: Low confidence scenario
    print("\n[TEST 2] Low Confidence Scenario")
    print("-" * 60)
    query2 = "Check outdated policy"
    
    # Mock low confidence
    retriever.retrieve = MagicMock(return_value={
        "chunks": ["Old policy from 2020"],
        "scores": [0.5],
        "metadata": [{"source_file": "old_doc.pdf", "ingested_at": (datetime(2020, 1, 1)).isoformat()}]
    })
    
    print(f"Query: {query2}")
    context2 = orchestrator.run(query2)
    print(f"[OK] Response Mode: {context2.get('response_mode')}")
    print(f"[OK] Confidence: {context2.get('confidence'):.2f}")
    
    action2 = executor.execute(context2)
    print(f"[OK] Action: {action2['action']}")
    print(f"[OK] Message: {action2['message'][:100]}...")

    # Test 3: Direct response (high confidence)
    print("\n[TEST 3] Direct Response (High Confidence)")
    print("-" * 60)
    
    # Mock high confidence scenario
    class HighConfidenceLLM:
        def generate(self, prompt: str) -> str:
            if "Planner Agent" in prompt:
                return '{"intent": "information_lookup", "risk": "low", "needs_retrieval": true}'
            if "contradiction detection" in prompt:
                return '{"conflict": false}'
            if "Final Decision Synthesizer" in prompt:
                return '{"recommendation": "Standard leave policy: 20 days per year", "risks": [], "tradeoffs": [], "confidence_score": 0.85, "reasoning": "Clear policy found"}'
            return '{"conflict": false}'
    
    llm_high = HighConfidenceLLM()
    planner_high = PlannerAgent(llm_high)
    evaluator_high = KnowledgeEvaluator(llm_high)
    synthesizer_high = FinalDecisionSynthesizer(llm_high)
    
    retriever.retrieve = MagicMock(return_value={
        "chunks": ["Clear policy: 20 days annual leave"],
        "scores": [0.95],
        "metadata": [{"source_file": "current_policy.pdf", "ingested_at": datetime.utcnow().isoformat()}]
    })
    
    orchestrator_high = Orchestrator(
        planner=planner_high,
        retriever=retriever,
        evaluator=evaluator_high,
        pro_agent=pro_agent,
        contra_agent=contra_agent,
        judge_agent=judge_agent,
        synthesizer=synthesizer_high
    )
    
    query3 = "How many leave days do I get?"
    print(f"Query: {query3}")
    context3 = orchestrator_high.run(query3)
    print(f"[OK] Response Mode: {context3.get('response_mode')}")
    print(f"[OK] Confidence: {context3.get('confidence'):.2f}")
    
    action3 = executor.execute(context3)
    print(f"[OK] Action: {action3['action']}")
    print(f"[OK] Message: {action3['message'][:100]}...")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
