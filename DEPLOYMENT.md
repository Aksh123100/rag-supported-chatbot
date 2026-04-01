# 🚀 Deployment Guide: Render (Free Tier)

This guide will help you deploy your RAG chatbot to production for **FREE**.

## Prerequisites

✅ Git installed  
✅ GitHub account  
✅ Render account (sign up at https://render.com)  
✅ API Keys (Groq + Voyage AI)

---

## Step 1: Push to GitHub

```bash
cd C:\users\akshs\rag-support-chatbot

# Initialize git (if not already done)
git init
git add .
git commit -m "Production-ready RAG chatbot"

# Create GitHub repo and push
# Go to https://github.com/new
# Create new repo: "rag-support-chatbot"
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/rag-support-chatbot.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend to Render

1. Go to https://dashboard.render.com/
2. Click **"New +" → "Web Service"**
3. Connect your GitHub repository
4. Configure:

**Basic Settings:**
- Name: `rag-chatbot-backend`
- Region: `Oregon (US West)`
- Branch: `main`
- Root Directory: `backend`
- Runtime: `Python 3`
- Build Command: `chmod +x build.sh && ./build.sh`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Advanced Settings → Environment Variables:**
```
USE_GROQ=True
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile
VOYAGE_API_KEY=your-voyage-api-key-here
APP_NAME=RAG Support Chatbot
DEBUG=False
API_PREFIX=/api/v1
CHROMA_PERSIST_DIRECTORY=/opt/render/project/src/data/chroma_db
CHROMA_COLLECTION_NAME=support_docs
```

**Health Check:**
- Health Check Path: `/health`

5. Click **"Create Web Service"**
6. Wait ~5 minutes for deployment
7. **Copy your backend URL**: `https://rag-chatbot-backend.onrender.com`

---

## Step 3: Deploy Frontend to Render

1. Click **"New +" → "Static Site"**
2. Select same repository
3. Configure:

**Basic Settings:**
- Name: `rag-chatbot-frontend`
- Branch: `main`
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`

**Environment Variables:**
```
VITE_API_URL=https://rag-chatbot-backend.onrender.com
```
*(Replace with YOUR backend URL from Step 2)*

4. Click **"Create Static Site"**
5. Wait ~3 minutes for deployment
6. **Your website is live!** `https://rag-chatbot-frontend.onrender.com`

---

## Step 4: Test Your Live Website

1. Open: `https://rag-chatbot-frontend.onrender.com`
2. Ask: "What is your return policy?"
3. ✅ You should see a response with sources!

---

## 🎉 Done! Your Chatbot is Live 24/7

**Your URLs:**
- Frontend: `https://rag-chatbot-frontend.onrender.com`
- Backend API: `https://rag-chatbot-backend.onrender.com`
- API Docs: `https://rag-chatbot-backend.onrender.com/docs` (disabled in production)

---

## ⚠️ Free Tier Limitations

- Backend **spins down after 15 min of inactivity** (first request takes ~30 sec)
- 750 hours/month free (enough for 24/7)
- No custom domain on free tier
- Limited to 512MB RAM

**To upgrade:** Render paid plans start at $7/month for always-on service.

---

## Optional: Custom Domain

1. Buy domain (Namecheap, GoDaddy, etc.)
2. In Render dashboard → Settings → Custom Domain
3. Add your domain
4. Update DNS records as instructed

---

## Troubleshooting

**Backend fails to build?**
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `build.sh` has correct line endings (LF not CRLF)

**Frontend can't connect to backend?**
- Verify `VITE_API_URL` matches your backend URL
- Check CORS settings in backend

**Chatbot not responding?**
- Wait 30 seconds after first request (cold start)
- Check `/health` endpoint
- Verify API keys are valid

---

## Next Steps

1. ✅ Add more documents to `backend/data/sample_docs/`
2. ✅ Monitor usage: https://dashboard.render.com
3. ✅ Set up uptime monitoring (UptimeRobot)
4. ✅ Customize frontend UI
5. ✅ Add authentication for admin features

**Need help?** Check Render docs: https://render.com/docs
