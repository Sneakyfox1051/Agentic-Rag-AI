# Deployment Guide for Render

## Quick Start

### 1. Prepare Your Repository

Make sure your code is pushed to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy on Render

#### Option A: Using render.yaml (Automatic)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and create the service
5. Click **"Apply"** to deploy

#### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure settings:
   - **Name**: `agentic-rag-api`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && cd frontend && npm install && npm run build
     ```
   - **Start Command**: 
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
5. Add Environment Variables:
   - `USE_MOCK` = `true` (for demo)
   - `PYTHON_VERSION` = `3.11.0`
6. Click **"Create Web Service"**

### 3. Wait for Deployment

Render will:
1. Install Python dependencies
2. Install Node.js dependencies
3. Build the React frontend
4. Start the FastAPI server

This typically takes 5-10 minutes on first deploy.

### 4. Access Your App

Once deployed, your app will be available at:
`https://your-service-name.onrender.com`

## Environment Variables

### For Demo/Testing
- `USE_MOCK=true` - Uses mock LLM (no API keys needed)

### For Production
- `USE_MOCK=false` - Use real LLM
- `LLM_API_KEY=your-key` - Your LLM API key
- `VECTOR_STORE_PATH=/path/to/store` - Path to vector store
- `REACT_APP_API_URL=https://your-api-url.onrender.com` - API URL for frontend

## Troubleshooting

### Build Fails

1. **Node.js not found**: Make sure Node.js is installed in Render
   - Add `NODE_VERSION=18` to environment variables

2. **Python dependencies fail**: Check `requirements.txt` syntax

3. **Frontend build fails**: Check `frontend/package.json` and ensure all dependencies are listed

### Runtime Errors

1. **Port binding error**: Make sure you're using `$PORT` environment variable
2. **CORS errors**: Check that CORS is configured in `app/main.py`
3. **Module not found**: Ensure all imports use `app.` prefix

### Logs

View logs in Render dashboard:
1. Go to your service
2. Click **"Logs"** tab
3. Check for errors

## Updating Your Deployment

1. Push changes to GitHub
2. Render will automatically detect and redeploy
3. Or manually trigger redeploy from Render dashboard

## Custom Domain

1. Go to your service settings
2. Click **"Custom Domains"**
3. Add your domain
4. Update DNS records as instructed

## Monitoring

- **Health Check**: `https://your-app.onrender.com/health`
- **Metrics**: Available in Render dashboard
- **Logs**: Real-time logs in dashboard

## Cost Considerations

- **Free Tier**: 
  - Services spin down after 15 minutes of inactivity
  - First request after spin-down takes ~30 seconds
  - 750 hours/month free

- **Paid Plans**: 
  - Always-on services
  - Faster response times
  - More resources

## Next Steps

1. Set up a real LLM client (OpenAI, Anthropic, etc.)
2. Create and upload vector store
3. Configure production environment variables
4. Set up monitoring and alerts
5. Configure custom domain
