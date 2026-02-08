# orchestration/graph.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Import your agents
from app.agents.planner import PlannerAgent
from app.retrieval.retriever import Retriever
from app.agents.evaluator import KnowledgeEvaluator
from app.debate.pro_agent import ProAgent
from app.debate.contra_agent import ContraAgent
from app.debate.judge_agent import JudgeAgent
from app.synthesis.decision_synthesizer import FinalDecisionSynthesizer

CONFIDENCE_THRESHOLD = 0.6  # configurable


@dataclass
class Node:
    name: str
    agent: Any  # instance of planner, retriever, evaluator, etc.


@dataclass
class Edge:
    source: str
    target: str
    condition: Optional[Any] = None  # lambda that returns bool


class Orchestrator:
    def __init__(
        self,
        planner: PlannerAgent,
        retriever: Retriever,
        evaluator: KnowledgeEvaluator,
        pro_agent: ProAgent,
        contra_agent: ContraAgent,
        judge_agent: JudgeAgent,
        synthesizer: FinalDecisionSynthesizer,
        confidence_threshold: float = CONFIDENCE_THRESHOLD
    ):
        self.nodes: Dict[str, Node] = {
            "planner": Node("planner", planner),
            "retriever": Node("retriever", retriever),
            "evaluator": Node("evaluator", evaluator),
            "pro_agent": Node("pro_agent", pro_agent),
            "contra_agent": Node("contra_agent", contra_agent),
            "judge_agent": Node("judge_agent", judge_agent),
            "synthesizer": Node("synthesizer", synthesizer)
        }
        self.edges: List[Edge] = []
        self.confidence_threshold = confidence_threshold

        self._build_graph()

    def _build_graph(self):
        """
        Conditional routing:
        planner -> (needs retrieval?) -> retriever -> evaluator
        evaluator -> (confidence low?) -> debate council
        else -> direct response
        """
        self.edges = [
            Edge("planner", "retriever", lambda ctx: ctx.get("needs_retrieval", False)),
            Edge("retriever", "evaluator", lambda ctx: True),
            Edge("evaluator", "pro_agent", lambda ctx: ctx.get("confidence", 0.0) < self.confidence_threshold),
            Edge("evaluator", "contra_agent", lambda ctx: ctx.get("confidence", 0.0) < self.confidence_threshold),
            Edge("pro_agent", "judge_agent", lambda ctx: True),
            Edge("contra_agent", "judge_agent", lambda ctx: True),
        ]

    def run(self, user_query: str, metadata_filter: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Executes the full agentic flow as per the diagram:
        1. User Query → Planner/Orchestrator
        2. Planner → RAG Pipeline (if needs knowledge)
        3. RAG → Knowledge Evaluation Agent
        4. Evaluation → High confidence? → Direct Response OR Debate Mode
        5. Debate Mode → Pro Agent, Contra Agent → Judge Agent
        6. All paths → Final Decision Synthesizer
        7. Synthesizer → Action Layer
        """
        context: Dict[str, Any] = {"user_query": user_query}

        # -------------------
        # 1️⃣ Planner / Orchestrator
        # - Intent detection
        # - Risk assessment
        # - Decide next steps
        # -------------------
        planner_node = self.nodes["planner"].agent
        plan_result = planner_node.plan(user_query)
        context.update(plan_result)

        # -------------------
        # 2️⃣ RAG Pipeline (if needs knowledge)
        # - Vector Store (Embeddings)
        # - Top-K Retrieval
        # -------------------
        if context.get("needs_retrieval", False):
            retriever_node = self.nodes["retriever"].agent
            rag_result = retriever_node.retrieve(
                query=user_query,
                top_k=5,
                metadata_filter=metadata_filter
            )
            context.update(rag_result)
        else:
            # No retrieval needed - set empty results
            rag_result = {"chunks": [], "scores": [], "metadata": []}
            context.update(rag_result)

        # -------------------
        # 3️⃣ Knowledge Evaluation Agent
        # - Freshness scoring
        # - Conflict detection
        # - Confidence estimation
        # -------------------
        evaluator_node = self.nodes["evaluator"].agent
        eval_result = evaluator_node.evaluate(
            chunks=context["chunks"],
            metadatas=context["metadata"],
            scores=context["scores"]
        )
        context.update(eval_result)

        # -------------------
        # 4️⃣ Conditional Routing
        # High confidence? → Direct Response
        # NO / RISKY → Multi-Agent Debate Mode
        # -------------------
        confidence = context.get("confidence", 0.0)
        is_high_confidence = confidence >= self.confidence_threshold
        
        if is_high_confidence:
            # -------------------
            # Direct Response Path
            # -------------------
            context["response_mode"] = "direct"
            debate_result = None
        else:
            # -------------------
            # Multi-Agent Debate Mode (Reasoning Council)
            # -------------------
            context["response_mode"] = "debate"
            
            pro_agent = self.nodes["pro_agent"].agent
            contra_agent = self.nodes["contra_agent"].agent
            judge_agent = self.nodes["judge_agent"].agent

            # Generate a proposed decision/recommendation from the query and context
            decision = self._generate_proposed_decision(user_query, context)
            
            # Pro Agent argues FOR the decision
            context["pro_result"] = pro_agent.argue(decision, context["chunks"])
            
            # Contra Agent argues AGAINST the decision
            context["contra_result"] = contra_agent.argue(decision, context["chunks"])
            
            # Judge Agent makes the decision
            context["final_judgment"] = judge_agent.judge(
                context["pro_result"], context["contra_result"]
            )
            
            debate_result = {
                "pro_result": context["pro_result"],
                "contra_result": context["contra_result"],
                "judgment": context["final_judgment"]
            }

        # -------------------
        # 5️⃣ Final Decision Synthesizer
        # - Recommendation
        # - Risks & tradeoffs
        # - Confidence score
        # -------------------
        synthesizer_node = self.nodes["synthesizer"].agent
        synthesis_result = synthesizer_node.synthesize(
            context=context,
            debate_result=debate_result if context["response_mode"] == "debate" else None
        )
        context["synthesis"] = synthesis_result

        return context
    
    def _generate_proposed_decision(self, user_query: str, context: Dict[str, Any]) -> str:
        """
        Generates a proposed decision/recommendation based on the query and context.
        This is used as input to the debate agents.
        """
        # Simple heuristic: use first chunk or query-based decision
        chunks = context.get("chunks", [])
        if chunks:
            # Use a summary of the first chunk as the proposed decision
            return f"Based on retrieved knowledge: {chunks[0][:200]}..."
        else:
            # Fallback to query-based decision
            return f"Proposed action: {user_query}"