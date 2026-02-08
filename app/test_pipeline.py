import pytest
from unittest.mock import MagicMock

# Import all your modules
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

# -----------------------------
# Mock LLM client
# -----------------------------
class MockLLM:
    def generate(self, prompt: str) -> str:
        if "Planner Agent" in prompt:
            # High-risk query
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
        # Fallback
        return '{"conflict": false}'

# -----------------------------
# Helper functions
# -----------------------------
def make_mock_docs(outdated=False, conflicting=False):
    from datetime import datetime, timedelta
    docs = []
    now = datetime.utcnow()
    for i in range(3):
        text = f"Document {i+1}"
        meta = {
            "source_file": f"doc{i+1}.pdf",
            "ingested_at": (now - timedelta(days=400) if outdated else now).isoformat()
        }
        docs.append(Document.create(text=text, metadata=meta))
    return docs

# -----------------------------
# Test cases
# -----------------------------
@pytest.fixture
def orchestrator_setup():
    llm = MockLLM()

    planner_agent = PlannerAgent(llm)
    vector_store = MagicMock(spec=VectorStore)
    # Mock Retriever to always return some chunks
    retriever = Retriever(vector_store, embedding_model=MagicMock())
    retriever.retrieve = MagicMock(return_value={
        "chunks": ["Chunk 1", "Chunk 2"],
        "scores": [0.9, 0.8],
        "metadata": make_mock_docs(conflicting=True)
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
        synthesizer=synthesizer,
        confidence_threshold=0.6
    )

    executor = ActionExecutor(confidence_threshold=0.6)

    return orchestrator, executor

# -----------------------------
# Test 1: Conflicting Policies Trigger Debate
# -----------------------------
def test_conflicting_policy_triggers_debate(orchestrator_setup):
    orchestrator, executor = orchestrator_setup
    user_query = "Update HR policy that conflicts with existing policy"

    context = orchestrator.run(user_query)
    assert context["response_mode"] == "debate", "Debate should be triggered for conflicts"

    action_result = executor.execute(context)
    assert action_result["action"] in ["escalate", "answer"], "High-risk/conflict should escalate or answer"
    assert len(action_result["flagged_documents"]) > 0, "Conflicting docs must be flagged"

# -----------------------------
# Test 2: Outdated Documents Reduce Confidence
# -----------------------------
def test_outdated_documents_trigger_clarification(orchestrator_setup):
    orchestrator, executor = orchestrator_setup
    # Mock outdated docs inside retriever
    orchestrator.nodes["retriever"].agent.retrieve = MagicMock(return_value={
        "chunks": ["Old doc chunk"],
        "scores": [0.5],
        "metadata": make_mock_docs(outdated=True)
    })

    user_query = "Check leave policy from old documents"
    context = orchestrator.run(user_query)
    # Evaluator should reduce confidence due to outdated documents
    assert context["confidence"] < 0.6, "Outdated documents lower confidence"

    action_result = executor.execute(context)
    assert action_result["action"] == "clarify", "Low-confidence should ask clarification"

# -----------------------------
# Test 3: High-Risk Query Escalates
# -----------------------------
def test_high_risk_query_escalation(orchestrator_setup):
    orchestrator, executor = orchestrator_setup
    user_query = "Approve high-risk financial policy"

    context = orchestrator.run(user_query)
    assert context["risk"] == "high", "Planner should classify as high risk"

    action_result = executor.execute(context)
    assert action_result["action"] == "escalate", "High-risk queries should escalate"
