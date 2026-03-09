# RainbowSim Web App - Build Instructions

This guide will help you build and deploy your RainbowSim physics simulator as a web app using Pygbag.

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git (for deployment)

## Local Development Setup

### 1. Install Dependencies

```bash
cd rainbow_web
pip install -r requirements.txt
```

### 2. Run Locally

To test the app locally before building:

```bash
python main.py
```

Or run with Pygbag's web server:

```bash
pygbag main.py
```

This will start a local server at `http://localhost:8000`

## Building the Web App

### Option 1: Build with Pygbag

```bash
pygbag main.py --build web
```

This creates an `/web` directory with all necessary files for deployment.

### Option 2: Build for Production

```bash
pygbag main.py --build web --minify
```

This creates a minified version suitable for production.

## Deployment Options

### Option 1: Deploy to Railway (Recommended)

Railway makes it easy to deploy web apps without complex configuration.

#### Steps:

1. **Create a Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Prepare Your Repository**
   - Create a `.gitignore` in the project root:
     ```
     venv/
     __pycache__/
     .DS_Store
     build/
     dist/
     *.egg-info
     ```
   - Initialize git (if not already done):
     ```bash
     git init
     git add .
     git commit -m "Initial commit"
     ```

3. **Create a Procfile**
   Create `rainbow_web/Procfile`:
   ```
   web: python -m http.server $PORT --directory web
   ```

4. **Connect to Railway**
   - In Railway dashboard, create new project
   - Select "Deploy from GitHub"
   - Authorize and select your repository
   - Railway will auto-detect and deploy

5. **Access Your App**
   - Visit the provided Railway URL (e.g., `https://yourapp.railway.app`)

### Option 2: Deploy to Heroku

#### Steps:

1. **Install Heroku CLI**
   ```bash
   brew install heroku/brew/heroku  # macOS
   # or visit heroku.com/downloads for other OS
   ```

2. **Create a Heroku App**
   ```bash
   heroku login
   heroku create rainbowsim-app
   ```

3. **Create Procfile** (rainbow_web/Procfile):
   ```
   web: python -m http.server $PORT --directory web
   ```

4. **Add runtime.txt** (rainbow_web/runtime.txt):
   ```
   python-3.11.4
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 3: Deploy to GitHub Pages

1. **Build the web app**
   ```bash
   pygbag main.py --build web
   ```

2. **Create a deployment repository**
   ```bash
   mkdir rainbowsim-web
   cd rainbowsim-web
   git init
   ```

3. **Copy built files**
   ```bash
   cp -r ../rainbow_web/web/* .
   ```

4. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Build web app"
   git remote add origin https://github.com/yourusername/rainbowsim-web.git
   git branch -M main
   git push -u origin main
   ```

5. **Enable GitHub Pages**
   - Go to repository Settings → Pages
   - Set source to "Deploy from branch" → main
   - Your site will be at `https://yourusername.github.io/rainbowsim-web`

## Debugging

### Test the built web files locally

```bash
cd web
python -m http.server 8000
# Visit http://localhost:8000
```

### Check for console errors

- Open browser DevTools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for failed resource loading

### Common Issues

**Issue: Modules not found**
- Ensure all Python files (refraction.py, prism.py, etc.) are in the `rainbow_web/` directory
- Check that imports use relative paths

**Issue: Slow performance**
- Use `--minify` flag when building
- Consider reducing animation frame rate in simulation code
- Use `await asyncio.sleep(0.01)` instead of `0` to yield control less frequently

**Issue: Canvas not rendering**
- Verify Pygame initialization completes
- Check browser console for errors
- Ensure asyncio.sleep() is called in main loop

## Performance Tips

1. **Optimize Graphics**
   - Use `pygame.SCALED` for display flag
   - Batch draw calls when possible
   - Use pygame's built-in drawing functions (faster than manual pixel ops)

2. **Handle Large Datasets**
   - Limit ray count for interactive simulations
   - Use numpy for mathematical operations (available in Pygbag)

3. **Mobile Support**
   - Test on mobile browsers
   - Ensure touch events work if needed
   - Optimize for varying screen sizes

## Updating Your App

After making changes:

1. **Local test:**
   ```bash
   python main.py
   ```

2. **Rebuild for web:**
   ```bash
   pygbag main.py --build web
   ```

3. **Deploy:**
   - For Railway/Heroku: Simply push to GitHub (auto-deploys if configured)
   - For GitHub Pages: Rebuild and push the `/web` folder

## Additional Resources

- [Pygbag Documentation](https://github.com/pygame-web/pygbag)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Railway Deployment Guide](https://railway.app)
- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)
