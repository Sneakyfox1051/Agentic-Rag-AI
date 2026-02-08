# Agentic RAG AI Pipeline - Flow Documentation

This document describes the complete flow of the Agentic RAG AI system as implemented.

## System Architecture Flow

```
┌──────────────────────┐
│        User          │
│  (Employee / Admin)  │
└─────────┬────────────┘
          │ Query
          ▼
┌──────────────────────┐
│  Planner / Orchestrator│
│  (Agentic Controller) │
│  - Intent detection   │
│  - Risk assessment    │
│  - Decide next steps  │
└─────────┬────────────┘
          │
          │ Needs knowledge?
          ▼
┌──────────────────────┐
│     RAG Pipeline     │
│                      │
│  ┌───────────────┐  │
│  │ Vector Store  │◄─┼─ PDFs, SOPs,
│  │ (Embeddings)  │  │  Policies
│  └───────────────┘  │
│                      │
│  Top-K Retrieval     │
└─────────┬────────────┘
          ▼
┌─────────────────────────────┐
│ Knowledge Evaluation Agent  │
│                             │
│ - Freshness scoring         │
│ - Conflict detection        │
│ - Confidence estimation     │
└─────────┬───────────────────┘
          │
          │ High confidence?
          │
   ┌──────┴──────┐
   │             │
 YES             NO / RISKY
   │             │
   ▼             ▼
┌────────────┐   ┌──────────────────────────┐
│ Direct     │   │  Multi-Agent Debate Mode │
│ Response   │   │  (Reasoning Council)     │
└─────┬──────┘   │                          │
      │          │  ┌──────────────┐        │
      │          │  │ Pro Agent    │        │
      │          │  │ (Argues FOR) │        │
      │          │  └──────┬───────┘        │
      │          │         │                │
      │          │  ┌──────▼───────┐        │
      │          │  │ Contra Agent │        │
      │          │  │ (Argues AGAINST)│     │
      │          │  └──────┬────────┘       │
      │          │         │                │
      │          │  ┌──────▼───────┐        │
      │          │  │ Judge Agent  │        │
      │          │  │ (Decision)   │        │
      │          │  └──────────────┘        │
      │          └─────────┬────────────────┘
      │                    ▼
      │          ┌──────────────────────────┐
      │          │ Final Decision Synthesizer│
      │          │ - Recommendation          │
      │          │ - Risks & tradeoffs       │
      │          │ - Confidence score        │
      │          └─────────┬────────────────┘
      │                    │
      └────────────────────┘
                ▼
┌──────────────────────────────────────────┐
│ Action Layer                              │
│                                          │
│ - Answer user                             │
│ - Ask clarification                      │
│ - Flag conflicting documents             │
│ - Escalate to human (legal/compliance)   │
└───────────────┬──────────────────────────┘
                ▼
        ┌────────────────┐
        │ Final Response │
        └────────────────┘
```

## Component Details

### 1. Planner / Orchestrator (`app/agents/planner.py`)
- **Purpose**: Intent detection, risk assessment, and routing decisions
- **Output**: Intent type, risk level, and whether retrieval is needed
- **Intent Types**: `information_lookup`, `policy_decision`, `procedural_guidance`, `compliance_check`, `unknown`
- **Risk Levels**: `low`, `medium`, `high`

### 2. RAG Pipeline (`app/retrieval/retriever.py`)
- **Purpose**: Retrieves relevant knowledge from vector store
- **Components**:
  - Vector Store: FAISS index with document embeddings
  - Top-K Retrieval: Returns top K most relevant chunks
- **Input**: User query, metadata filters
- **Output**: Chunks, relevance scores, metadata

### 3. Knowledge Evaluation Agent (`app/agents/evaluator.py`)
- **Purpose**: Evaluates quality and reliability of retrieved knowledge
- **Evaluations**:
  - **Freshness Scoring**: Based on document age (exponential decay)
  - **Conflict Detection**: Uses LLM to detect semantic contradictions
  - **Confidence Estimation**: Combines relevance, freshness, and conflict penalty
- **Output**: Freshness score, conflict flag, confidence score

### 4. Conditional Routing
- **High Confidence (≥ threshold)**: Direct Response Path
- **Low Confidence / Risky**: Multi-Agent Debate Mode

### 5. Multi-Agent Debate Mode (`app/debate/`)
- **Pro Agent** (`pro_agent.py`): Argues FOR the proposed decision
- **Contra Agent** (`contra_agent.py`): Argues AGAINST, identifies risks and contradictions
- **Judge Agent** (`judge_agent.py`): Evaluates both arguments and makes a decision
- **Output**: Winner, reasoning, uncertainty score

### 6. Final Decision Synthesizer (`app/synthesis/decision_synthesizer.py`)
- **Purpose**: Synthesizes final recommendation from either debate or direct evaluation
- **Input**: Context from orchestrator, optional debate results
- **Output**:
  - Recommendation
  - Risks
  - Tradeoffs
  - Confidence score
  - Reasoning

### 7. Action Layer (`app/action/executor.py`)
- **Purpose**: Converts synthesis into deterministic actions
- **Actions**:
  - `answer`: Provide direct answer
  - `clarify`: Ask for clarification
  - `escalate`: Escalate to human review
  - `flag`: Flag conflicting documents
- **Decision Logic**:
  - High risk → Escalate
  - Very low confidence (< 0.3) → Escalate
  - High uncertainty from debate (> 0.7) → Escalate
  - Conflicts detected → Flag
  - Low confidence → Clarify
  - Otherwise → Answer

## Configuration

### Confidence Threshold
Default: `0.6` (configurable in `Orchestrator` and `ActionExecutor`)

### High Risk Levels
Default: `["high"]` (configurable in `ActionExecutor`)

## Usage

### API Endpoint
```python
POST /ask
{
    "query": "What is the leave policy?",
    "metadata_filter": {"department": "HR"}  # Optional
}
```

### Response
```python
{
    "action": "answer|clarify|escalate|flag",
    "message": "Full response with recommendation, risks, tradeoffs, and confidence",
    "flagged_documents": ["doc1.pdf", "doc2.pdf"]  # If conflicts detected
}
```

## File Structure

```
app/
├── agents/
│   ├── planner.py          # Planner/Orchestrator
│   └── evaluator.py        # Knowledge Evaluation Agent
├── retrieval/
│   └── retriever.py        # RAG Pipeline
├── debate/
│   ├── pro_agent.py        # Pro Agent
│   ├── contra_agent.py     # Contra Agent
│   └── judge_agent.py      # Judge Agent
├── synthesis/
│   └── decision_synthesizer.py  # Final Decision Synthesizer
├── action/
│   └── executor.py         # Action Layer
├── orchestration/
│   └── graph.py           # Main Orchestrator
├── ingestion/             # Document ingestion pipeline
└── main.py                # FastAPI application
```

## Flow Execution

1. **User Query** → Received via API
2. **Planner** → Analyzes intent and risk
3. **RAG Pipeline** → Retrieves relevant knowledge (if needed)
4. **Knowledge Evaluator** → Evaluates quality and confidence
5. **Routing Decision**:
   - High confidence → Direct path
   - Low confidence → Debate mode
6. **Final Synthesizer** → Creates comprehensive recommendation
7. **Action Executor** → Determines final action
8. **Response** → Returned to user

## Testing

Run tests with:
```bash
pytest app/test_pipeline.py
```

Test cases cover:
- Conflicting policies triggering debate
- Outdated documents reducing confidence
- High-risk query escalation
