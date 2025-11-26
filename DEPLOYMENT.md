# Deploying to Render

This guide explains how to deploy the Autonomous QA Agent to Render.

## Prerequisites

1. **GitHub Repository**: Push your code to a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Groq API Key**: Get your API key from [console.groq.com](https://console.groq.com)

## Deployment Steps

### 1. Prepare Your Repository

Ensure these files are in your repository:
- `requirements.txt` - Python dependencies
- `render.yaml` - Render Blueprint configuration
- `start_backend.sh` - Backend startup script
- `start_frontend.sh` - Frontend startup script

### 2. Connect to Render

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select the repository containing your QA agent code

### 3. Configure Environment Variables

Render will read the `render.yaml` file. You need to set:

**For Backend Service:**
- `GROQ_API_KEY`: Your Groq API key (keep this secret!)
- `RENDER`: Set to `true` (Render sets this automatically)

**For Frontend Service:**
- `BACKEND_URL`: Automatically set from backend service

### 4. Deploy

1. Click **"Apply"** to create both services
2. Render will:
   - Install dependencies from `requirements.txt`
   - Create persistent disk storage (1GB) for ChromaDB
   - Start both backend and frontend services
3. Wait for deployment to complete (~5-10 minutes)

### 5. Verify Deployment

**Backend Health Check:**
```bash
curl https://qa-agent-backend.onrender.com/api/health
```

**Frontend Access:**
Open `https://qa-agent-frontend.onrender.com` in your browser

## Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit Frontend              │
│    (qa-agent-frontend.onrender.com)     │
└──────────────────┬──────────────────────┘
                   │ HTTP Requests
                   ▼
┌─────────────────────────────────────────┐
│          FastAPI Backend                │
│     (qa-agent-backend.onrender.com)     │
│                                          │
│  ┌────────────┐      ┌──────────────┐  │
│  │  Groq LLM  │      │  ChromaDB    │  │
│  │  (Cloud)   │      │  (Disk: 1GB) │  │
│  └────────────┘      └──────────────┘  │
└─────────────────────────────────────────┘
```

## Usage Workflow

1. **Upload Documents**: Use frontend to upload support documents (MD, TXT, JSON, HTML)
2. **Build Knowledge Base**: Click "Build Knowledge Base" to process and embed documents
3. **Generate Test Cases**: Enter requirements and generate test cases
4. **Create Scripts**: Select test cases and generate Selenium scripts
5. **Download Scripts**: Download generated Python scripts

## Important Notes

### Free Tier Limitations
- 750 hours/month per service
- Services spin down after 15 minutes of inactivity
- Cold start takes ~30 seconds when service wakes up
- Persistent disk: 1GB included

### Persistent Storage
- ChromaDB data is stored on persistent disk at `/opt/render/project/data`
- Data persists across deployments
- Uploaded documents and generated scripts are also persisted

### Environment Detection
The application automatically detects Render environment and uses appropriate paths:
- **Local**: `./data/uploads`, `./data/vector_db`, `./data/outputs`
- **Render**: `/opt/render/project/data/uploads`, `/opt/render/project/data/chroma_db`, `/opt/render/project/data/outputs`

## Troubleshooting

### Service Won't Start
- Check logs in Render Dashboard
- Verify `GROQ_API_KEY` is set correctly
- Ensure `requirements.txt` has all dependencies

### ChromaDB Errors
- Verify persistent disk is mounted at `/opt/render/project/data`
- Check disk space usage in Render Dashboard

### Frontend Can't Connect to Backend
- Verify `BACKEND_URL` environment variable is set
- Check backend service is running and healthy

## Updating Your Deployment

1. Push changes to your GitHub repository
2. Render automatically redeploys on push (if auto-deploy is enabled)
3. Or manually trigger deploy from Render Dashboard

## Cost Optimization

**Free Tier Strategy:**
- Use free tier for development/testing
- Services auto-sleep after 15 minutes of inactivity
- Wake up on first request (30s cold start)

**Upgrade Considerations:**
- **Starter Plan ($7/month per service)**: No sleep, faster performance
- **Larger Disk**: If you need more than 1GB for ChromaDB

## Support

For issues:
1. Check Render logs in Dashboard
2. Review application logs for errors
3. Verify environment variables are set correctly
