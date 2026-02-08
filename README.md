# Agentic-Rag-AI

# Agentic RAG AI Pipeline

Enterprise AI Assistant with Multi-Agent Reasoning, RAG (Retrieval-Augmented Generation), and Debate-based Decision Making.

## 🚀 Features

- **Planner/Orchestrator**: Intent detection and risk assessment
- **RAG Pipeline**: Vector-based knowledge retrieval
- **Knowledge Evaluator**: Freshness scoring, conflict detection, confidence estimation
- **Multi-Agent Debate**: Pro/Contra agents with Judge for complex decisions
- **Final Decision Synthesizer**: Comprehensive recommendations with risks and tradeoffs
- **Action Layer**: Smart routing (answer/clarify/escalate/flag)

## 📋 Prerequisites

- Python 3.11+
- Node.js 16+ (for frontend)
- npm or yarn

## 🛠️ Local Setup

### Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000` and the API at `http://localhost:8000`.

## 🚢 Deployment on Render

### Quick Deploy (Recommended)

1. **Verify everything is ready**:
   ```bash
   python verify_deployment.py
   ```

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

3. **Deploy on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Click **"Apply"** to deploy

4. **Wait 5-10 minutes** for build to complete

5. **Test**: Visit your Render URL and try the `/health` endpoint

See `DEPLOY_NOW.md` for detailed step-by-step instructions.

### Manual Setup (Alternative)

If not using `render.yaml`:

1. **Create a Web Service** on Render
2. **Settings**:
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && cd frontend && npm install && npm run build
     ```
   - **Start Command**: 
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Environment Variables**:
     - `USE_MOCK=true` (for demo mode)
     - `PYTHON_VERSION=3.11.0`
     - `NODE_VERSION=18.18.0`

3. **Deploy**

### Environment Variables

- `USE_MOCK`: Set to `true` for demo mode with mock LLM (default: `true`)
- `PORT`: Server port (Render sets this automatically)
- `REACT_APP_API_URL`: Frontend API URL (optional, defaults to same origin)

## 📁 Project Structure

```
.
├── app/
│   ├── agents/          # Planner and Evaluator agents
│   ├── debate/          # Pro, Contra, Judge agents
│   ├── synthesis/       # Final Decision Synthesizer
│   ├── retrieval/       # RAG pipeline
│   ├── orchestration/   # Main orchestrator
│   ├── action/          # Action executor
│   ├── ingestion/       # Document processing
│   ├── main.py          # FastAPI application
│   └── mock_setup.py    # Mock initialization
├── frontend/            # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment config
└── README.md
```

## 🧪 Testing

### Run Unit Tests

```bash
pytest app/test_pipeline.py -v
```

### Run Quick Test Script

```bash
python test_quick.py
```

## 🔧 Configuration

### Using Real LLM (Production)

1. Create your LLM client in `app/llm_client.py`
2. Create your embedding model in `app/embedding_model.py`
3. Update `app/main.py` to use real implementations:

```python
from app.llm_client import YourLLMClient
from app.embedding_model import YourEmbeddingModel

llm_client = YourLLMClient(api_key=os.getenv("LLM_API_KEY"))
embedding_model = YourEmbeddingModel()
# ... initialize orchestrator with real components
```

4. Set `USE_MOCK=false` in environment variables

## 📖 API Endpoints

### POST `/ask`

Query the AI assistant.

**Request**:
```json
{
  "query": "What is the leave policy?",
  "metadata_filter": {"department": "HR"}  // Optional
}
```

**Response**:
```json
{
  "action": "answer|clarify|escalate|flag",
  "message": "Full response with recommendation...",
  "flagged_documents": ["doc1.pdf", "doc2.pdf"]
}
```

### GET `/health`

Health check endpoint.

## 🎨 Frontend Features

- Modern, responsive UI
- Real-time query processing
- Action-based response display
- Flagged documents warning
- Flow diagram visualization

## 📝 License

MIT

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
