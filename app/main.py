# api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

# Import orchestrator and executor
from app.orchestration.graph import Orchestrator
from app.action.executor import ActionExecutor
from app.mock_setup import create_mock_orchestrator

# -----------------------------
# API models
# -----------------------------
class AskRequest(BaseModel):
    query: str
    metadata_filter: Optional[Dict[str, str]] = None


class AskResponse(BaseModel):
    action: str
    message: str
    flagged_documents: list


# -----------------------------
# Initialize FastAPI app
# -----------------------------
app = FastAPI(title="Agentic RAG AI Pipeline API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "build")
static_path = os.path.join(frontend_path, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# -----------------------------
# Initialize your agents here
# (replace with actual instances)
# -----------------------------
# TODO: Replace with actual implementations
# You'll need to provide:
# - llm_client: An LLM client with a generate(prompt: str) -> str method
# - vector_store: A VectorStore instance (from app.retrieval.retriever)
# - embedding_model: An embedding model with embed(texts: List[str]) -> np.ndarray

# Example initialization (commented out - replace with actual):
# from app.agents.planner import PlannerAgent
# from app.retrieval.retriever import Retriever, VectorStore
# from app.agents.evaluator import KnowledgeEvaluator
# from app.debate.pro_agent import ProAgent
# from app.debate.contra_agent import ContraAgent
# from app.debate.judge_agent import JudgeAgent
# from app.synthesis.decision_synthesizer import FinalDecisionSynthesizer
# 
# llm_client = YourLLMClient()  # Replace with actual LLM client
# planner_agent = PlannerAgent(llm_client)
# evaluator = KnowledgeEvaluator(llm_client)
# pro_agent = ProAgent(llm_client)
# contra_agent = ContraAgent(llm_client)
# judge_agent = JudgeAgent(llm_client)
# synthesizer = FinalDecisionSynthesizer(llm_client)
# 
# vector_store = VectorStore("path/to/vector/store")
# embedding_model = YourEmbeddingModel()  # Replace with actual embedding model
# retriever = Retriever(vector_store, embedding_model)
# 
# orchestrator = Orchestrator(
#     planner=planner_agent,
#     retriever=retriever,
#     evaluator=evaluator,
#     pro_agent=pro_agent,
#     contra_agent=contra_agent,
#     judge_agent=judge_agent,
#     synthesizer=synthesizer
# )
# 
# executor = ActionExecutor()

# Initialize with mock setup for demo
# Replace with actual implementations for production
USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"

if USE_MOCK:
    orchestrator = create_mock_orchestrator()
    executor = ActionExecutor()
else:
    # TODO: Initialize with actual LLM client and vector store
    orchestrator = None
    executor = ActionExecutor()


# -----------------------------
# API Endpoint
# -----------------------------
@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator not initialized. Please configure all agents."
        )

    # Run the orchestration pipeline
    # Flow: User Query → Planner → RAG → Evaluator → (Debate/Direct) → Synthesizer → Action
    context = orchestrator.run(
        user_query=request.query,
        metadata_filter=request.metadata_filter
    )

    # Action Layer: Map synthesis to deterministic action
    action_result = executor.execute(context)

    return AskResponse(**action_result)


# -----------------------------
# Serve frontend
# -----------------------------
@app.get("/")
async def read_root():
    """Serve frontend index.html"""
    frontend_index = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "build", "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {"message": "Frontend not built. Run 'npm run build' in frontend directory."}

# Catch-all route for React Router (if needed in future)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend for all routes (React Router support)"""
    # Don't interfere with API routes
    if full_path.startswith(("api/", "ask", "health", "docs", "openapi.json", "static/")):
        raise HTTPException(status_code=404, detail="Not found")
    
    frontend_index = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "build", "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    raise HTTPException(status_code=404, detail="Frontend not found")

# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok", "orchestrator_initialized": orchestrator is not None}
