# 🚀 Deploy to Render - Step by Step

Your code is now on GitHub: https://github.com/Sneakyfox1051/Agentic-Rag-AI

## Deploy on Render (5 minutes)

### Step 1: Go to Render Dashboard
Visit: https://dashboard.render.com

### Step 2: Create New Blueprint
1. Click the **"New +"** button (top right)
2. Select **"Blueprint"** from the dropdown

### Step 3: Connect GitHub
1. If not connected, click **"Connect GitHub"**
2. Authorize Render to access your repositories
3. Select **"Sneakyfox1051/Agentic-Rag-AI"** repository

### Step 4: Review Configuration
Render will automatically detect `render.yaml` and show:
- **Service Name**: `agentic-rag-api`
- **Build Command**: (auto-filled from render.yaml)
- **Start Command**: (auto-filled from render.yaml)
- **Environment Variables**: 
  - `USE_MOCK=true`
  - `PYTHON_VERSION=3.11.0`
  - `NODE_VERSION=18.18.0`

### Step 5: Deploy
1. Click **"Apply"** button
2. Wait 5-10 minutes for build to complete
3. Watch the build logs in real-time

### Step 6: Access Your App
Once deployed, you'll get a URL like:
`https://agentic-rag-api.onrender.com`

## ✅ Verify Deployment

### Test Health Endpoint
```bash
curl https://agentic-rag-api.onrender.com/health
```

Should return:
```json
{"status":"ok","orchestrator_initialized":true}
```

### Test the Frontend
1. Visit your Render URL in browser
2. You should see the Agentic RAG AI interface
3. Try asking: "What is the leave policy?"

## 📊 Monitor Your Deployment

- **Logs**: Click on your service → "Logs" tab
- **Metrics**: View in dashboard
- **Settings**: Configure environment variables, custom domain, etc.

## 🎉 Success!

Your app is now live! The deployment includes:
- ✅ React frontend
- ✅ FastAPI backend
- ✅ Mock LLM (no API keys needed)
- ✅ All agent components working

## 🔄 Update Your App

To update:
1. Make changes locally
2. `git add .`
3. `git commit -m "your message"`
4. `git push origin main`
5. Render will auto-deploy (or trigger manually)

## 💡 Tips

- First deployment takes 5-10 minutes
- Free tier spins down after 15 min inactivity
- First request after spin-down takes ~30 seconds
- Upgrade to paid plan for always-on service

## 🆘 Need Help?

- Check build logs for errors
- Verify environment variables
- Test `/health` endpoint
- See `DEPLOYMENT.md` for troubleshooting

---

**Your Repository**: https://github.com/Sneakyfox1051/Agentic-Rag-AI
**Render Dashboard**: https://dashboard.render.com
