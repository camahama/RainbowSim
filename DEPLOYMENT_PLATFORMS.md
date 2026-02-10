# 🚀 RainbowSim - Platform-Specific Deployment Guides

Choose your preferred deployment platform below.

---

## ⭐ Railway (Recommended - Fastest)

Railway is the easiest option for Python web apps. Deploy in minutes!

### Prerequisites
- GitHub account
- Railway account (free tier available)

### Steps

1. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/yourusername/RainbowSim.git
   git branch -M main
   git add .
   git commit -m "RainbowSim web app"
   git push -u origin main
   ```

2. **Create Railway Project**
   - Visit https://railway.app
   - Click "Deploy from GitHub"
   - Authorize Railway to access GitHub
   - Select your RainbowSim repository

3. **Railway Auto-Configuration**
   - Railway auto-detects Python project
   - Uses `Procfile` and `runtime.txt` ✅ Already configured!
   - Automatically builds and deploys

4. **Monitor Deployment**
   - Go to Project → Deployments
   - Watch build logs in real-time
   - Status changes from "Building" → "Deploying" → "Success"

5. **Access Your App**
   - Railway provides a public URL (e.g., `https://rainbowsim.railway.app`)
   - Share this link!

### Redeploy After Changes
```bash
git push origin main  # Railway auto-redeploys
```

### View Logs
- Dashboard → Deployments → Click deployment → Logs

### Troubleshooting
- **Build fails**: Check logs for Python errors
- **App crashes**: Ensure `Procfile` path is correct
- **Slow startup**: First build takes 2-5 minutes

---

## 🦸 Heroku

Traditional choice with good documentation.

### Prerequisites
- GitHub account
- Heroku account (free tier has limitations)
- Heroku CLI installed: `brew install heroku/brew/heroku`

### Steps

1. **Initialize Git & Push to GitHub** (Optional but recommended)
   ```bash
   git remote add origin https://github.com/yourusername/RainbowSim.git
   git branch -M main
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

2. **Create Heroku App**
   ```bash
   heroku login
   heroku create rainbowsim-unique-name
   ```
   
   Replace `rainbowsim-unique-name` with your preferred name (must be globally unique).

3. **Deploy Code**
   ```bash
   git push heroku main
   ```

4. **Open Your App**
   ```bash
   heroku open
   ```
   
   Or manually visit: `https://rainbowsim-unique-name.herokuapp.com`

### Redeploy After Changes
```bash
git push heroku main
```

### View Logs
```bash
heroku logs --tail
```

### Common Issues

**App crashes on startup**
```bash
heroku logs --tail  # Check error messages
```

**Module not found errors**
- Ensure all .py files are in rainbow_web/
- Check imports are correct

**Cold start is slow**
- Normal for Heroku free tier
- Consider upgrading to paid tier

### Clean Up
```bash
heroku apps:destroy --app rainbowsim-unique-name
```

---

## 📄 GitHub Pages (Free Hosting)

Free hosting but requires manual build uploads.

### Prerequisites
- GitHub account
- Build already created locally

### Steps

1. **Build Locally**
   ```bash
   cd rainbow_web
   pygbag main.py --build web
   cd ..
   ```

2. **Create Deployment Branch**
   ```bash
   git checkout --orphan gh-pages
   git rm -rf .
   ```

3. **Copy Built Files**
   ```bash
   cp -r rainbow_web/web/* .
   ```

4. **Commit & Push**
   ```bash
   git add .
   git commit -m "Deploy web app"
   git push -u origin gh-pages
   ```

5. **Enable GitHub Pages**
   - Go to your GitHub repository
   - Settings → Pages
   - Source → Select "gh-pages" branch
   - Save

6. **Access Your App**
   - Wait 1-2 minutes for deployment
   - URL: `https://yourusername.github.io/RainbowSim/`

### Update App
Each time you make changes:
```bash
# Rebuild
cd rainbow_web
pygbag main.py --build web
cd ..

# Update gh-pages branch
git checkout gh-pages
cp -r rainbow_web/web/* .
git add .
git commit -m "Update app"
git push origin gh-pages

# Switch back to main
git checkout main
```

### Custom Domain (Optional)
- Buy domain (e.g., GoDaddy, Namecheap)
- Go to repository Settings → Pages
- Add custom domain
- Update DNS records at domain provider

---

## 🐳 Docker Deployment (Advanced)

Use if you need more control or want to deploy to custom platforms.

### Create Dockerfile

Save as `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install Python dependencies
WORKDIR /app/rainbow_web
RUN pip install --no-cache-dir -r requirements.txt

# Build web app
RUN pygbag main.py --build web

# Expose port
EXPOSE 8000

# Run web server
WORKDIR /app/rainbow_web/web
CMD ["python", "-m", "http.server", "8000", "--bind", "0.0.0.0"]
```

### Deploy to Docker Hub

```bash
docker build -t yourusername/rainbowsim .
docker push yourusername/rainbowsim
```

### Deploy to Cloud Platforms

**AWS:**
- Amazon ECS
- AWS Elastic Beanstalk

**Google Cloud:**
- Cloud Run
- Cloud Compute Engine

**Azure:**
- App Service
- Container Instances

---

## 📊 Comparison Table

| Platform | Cost | Ease | Build Time | Auto-Deploy | Custom Domain |
|----------|------|------|------------|-------------|---------------|
| Railway (⭐) | Free | ⭐⭐⭐ | 2-3 min | ✅ Yes | ✅ Yes |
| Heroku | Free*/Paid | ⭐⭐⭐ | 3-5 min | ✅ Yes | ✅ Yes |
| GitHub Pages | Free | ⭐⭐ | Manual | ❌ No | ✅ Yes |
| Docker | Free/Paid | ⭐ | 5-10 min | Manual | ✅ Yes |

*Heroku free tier limited to 512MB RAM and may sleep

---

## 🆘 General Troubleshooting

### Build Fails
1. Clear cache: `rm -rf .pygbag_cache rainbow_web/.pygbag_cache`
2. Reinstall dependencies: `pip install --force-reinstall -r requirements.txt`
3. Check Python version: `python --version` (need 3.8+)

### App Won't Load
1. Check console errors (F12 → Console)
2. Verify all Python files are in rainbow_web/
3. Test locally first: `python rainbow_web/main.py`

### Slow Performance
1. Use minified build: `pygbag rainbow_web/main.py --build web --minify`
2. Check network tab for large files
3. Reduce simulation complexity

### Module Import Errors
1. Ensure all .py files in rainbow_web/
2. Check import statements don't use absolute paths
3. Verify no circular imports

---

## 🎯 Recommendation

For **first-time deployment**: Use **Railway** (easiest, fastest)

For **free hosting**: Use **GitHub Pages** (but requires manual uploading)

For **production**: Use **Heroku** or **Railway** with paid tier for better uptime

---

## 📞 Support Resources

- [Pygbag GitHub](https://github.com/pygame-web/pygbag)
- [Railway Docs](https://docs.railway.app)
- [Heroku Docs](https://devcenter.heroku.com/)
- [GitHub Pages Docs](https://docs.github.com/en/pages)

---

**Ready to deploy? Follow the checklist in DEPLOYMENT_CHECKLIST.md** ✅
