# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Node.js packages (for frontend)
cd frontend
npm install
cd ..
```

### Step 2: Build Frontend

```bash
cd frontend
npm run build
cd ..
```

### Step 3: Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### Step 4: Open in Browser

Visit: `http://localhost:8000`

The app is now running with mock data!

## 🧪 Test It

Try asking:
- "What is the leave policy?"
- "Check HR compliance requirements"
- "What are the company policies?"

## 📦 Deploy to Render

1. Push to GitHub
2. Connect to Render
3. Deploy!

See `DEPLOYMENT.md` for detailed instructions.

## 🎯 What's Next?

- Replace mock LLM with real implementation
- Add your vector store
- Configure production settings
