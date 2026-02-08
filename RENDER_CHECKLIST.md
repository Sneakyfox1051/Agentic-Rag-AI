# Render Deployment Checklist

## ✅ Pre-Deployment Checklist

### Files Required
- [x] `render.yaml` - Render configuration
- [x] `requirements.txt` - Python dependencies
- [x] `Procfile` - Process file
- [x] `runtime.txt` - Python version
- [x] `.gitignore` - Git ignore rules
- [x] `app/main.py` - FastAPI application
- [x] `app/mock_setup.py` - Mock initialization
- [x] `frontend/package.json` - Frontend dependencies
- [x] `frontend/src/` - React source files

### Configuration Verified
- [x] CORS enabled in `app/main.py`
- [x] Static file serving configured
- [x] Frontend build path correct
- [x] Health check endpoint exists
- [x] Mock setup enabled by default
- [x] Environment variables set in `render.yaml`

### Build Process
- [x] Python dependencies listed in `requirements.txt`
- [x] Node.js version specified (18.18.0)
- [x] Build command includes frontend build
- [x] Start command uses `$PORT` variable

## 🚀 Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect GitHub repository
   - Render will auto-detect `render.yaml`
   - Review settings and click "Apply"

3. **Monitor Deployment**
   - Watch build logs
   - Check for any errors
   - Verify health endpoint: `/health`

4. **Test Application**
   - Visit your Render URL
   - Test query endpoint
   - Verify frontend loads

## 🔍 Verification Commands

After deployment, test these endpoints:

```bash
# Health check
curl https://your-app.onrender.com/health

# API test
curl -X POST https://your-app.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

## ⚠️ Common Issues & Solutions

### Build Fails - Node.js not found
**Solution**: Node.js version is specified in `render.yaml` and `.nvmrc`

### Build Fails - Frontend build error
**Solution**: Check `frontend/package.json` and ensure all dependencies are listed

### Runtime Error - Port binding
**Solution**: Verify `$PORT` is used in start command (already configured)

### Frontend not loading
**Solution**: Check that build directory exists and static files are served correctly

### CORS errors
**Solution**: CORS is configured to allow all origins (update for production)

## 📝 Post-Deployment

1. Test all endpoints
2. Monitor logs for errors
3. Set up custom domain (optional)
4. Configure production environment variables
5. Set up monitoring/alerts

## 🎯 Success Criteria

- [ ] Application builds successfully
- [ ] Health endpoint returns 200
- [ ] Frontend loads at root URL
- [ ] API endpoint responds correctly
- [ ] Mock LLM works (for testing)
