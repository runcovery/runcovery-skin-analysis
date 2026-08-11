# Deployment Guide for Render

## Prerequisites
- GitHub account
- Render account (free): https://render.com

## Step-by-Step Deployment

### 1. Push to GitHub

```bash
cd /Users/MAC/skin-scan

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Skin Scan API"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/skin-scan.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render

1. Go to https://render.com and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select the `skin-scan` repository
5. Render will auto-detect the `render.yaml` config

**Configure:**
- **Name:** `skin-scan-api` (or your preferred name)
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Build Command:** `pip install -e .`
- **Start Command:** `uvicorn src.app.main:app --host 0.0.0.0 --port $PORT`
- **Plan:** Free

### 3. Environment Variables

**Good news:** The `render.yaml` file already has all necessary environment variables configured!

No API keys needed - the skin analysis runs 100% locally using OpenCV and MediaPipe. Completely free!

### 4. Deploy

Click **"Create Web Service"**

Render will:
1. Clone your repo
2. Install dependencies
3. Start the server
4. Give you a URL like: `https://skin-scan-api.onrender.com`

**First deployment takes 5-10 minutes.**

### 5. Test Your Deployment

Once deployed, test the endpoints:

```bash
# Health check
curl https://YOUR_APP_NAME.onrender.com/health

# Should return: {"ok":true}
```

```bash
# Test scan endpoint
curl -X POST https://YOUR_APP_NAME.onrender.com/scan \
  -F "image=@path/to/face.jpg"
```

### 6. Access Web UI

Your app is now live at:
```
https://YOUR_APP_NAME.onrender.com
```

The web interface will be available at the root URL.

## Important Notes

### Free Tier Limitations
- **Sleeps after 15 min of inactivity** (wakes up on first request, takes 30-60 sec)
- 750 hours/month of runtime
- Perfect for beta testing

### Performance
- First request after sleep: ~60 seconds (cold start)
- Subsequent requests: Fast

### Monitoring
- View logs in Render dashboard
- Check "Events" tab for deployment status
- "Logs" tab shows real-time application logs

## Troubleshooting

### Build fails
Check that `pyproject.toml` has all dependencies listed.

### Memory issues
MediaPipe + OpenCV can be heavy. Free tier has 512MB RAM.
- Reduce MAX_IMAGE_SIZE to 1024 if needed
- Consider upgrading to paid tier ($7/mo for 1GB RAM)

### Import errors
Make sure all imports use relative paths (already configured).

## Upgrading to Paid Tier

If you need:
- No sleep (always-on)
- More RAM/CPU
- Custom domain

Upgrade to **Starter** ($7/mo):
- 1GB RAM
- Always-on
- Better performance

## Custom Domain

Once deployed:
1. Buy domain (Namecheap, ~$10/year)
2. In Render → Settings → Custom Domain
3. Add your domain
4. Update DNS records (Render provides instructions)

Example: `api.yourskinapp.com`

## Next Steps After Deployment

1. ✅ Get your live URL
2. Share with beta testers
3. Collect feedback
4. Monitor logs for errors
5. Add analytics (optional)

## Need Help?

- Render docs: https://render.com/docs
- Join Render Discord for support
- Check logs in dashboard for errors
