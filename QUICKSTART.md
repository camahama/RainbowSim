# 🌈 RainbowSim Web App - Quick Start Guide

## What I've Set Up For You

I've configured your RainbowSim project with everything needed to build and deploy a web app using **Pygbag** (Pygame → WebAssembly compiler). Your project now includes:

✅ **Pygbag Configuration** (`pyproject.toml`, `requirements.txt`)  
✅ **Deployment Guides** (Railway, Heroku, GitHub Pages)  
✅ **Build Scripts** (automated setup and build)  
✅ **GitHub Actions Workflows** (automatic building on push)  

---

## 🚀 Quick Start (3 Steps)

### Step 1: Setup
```bash
chmod +x setup.sh
./setup.sh
```

This creates a virtual environment and installs dependencies.

### Step 2: Run Locally
```bash
cd rainbow_web
python main.py
```

### Step 3: Build for Web
```bash
cd rainbow_web
pygbag main.py --build web
python -m http.server 8000 --directory web
```

Then open: **http://localhost:8000**

---

## 📋 Deployment (GitHub Pages)

**Completely free, no extra accounts needed!**

1. Build locally: `cd rainbow_web && pygbag main.py --build web`
2. Create `gh-pages` branch: `git checkout --orphan gh-pages`
3. Copy built files: `cp -r rainbow_web/web/* .`
4. Push: `git add . && git commit -m "Deploy" && git push -u origin gh-pages`
5. Enable Pages in GitHub Settings → Pages
6. Your app is live at: `https://yourusername.github.io/RainbowSim`

**Return to main branch:**
```bash
git checkout main
```

---

## 📁 Your Project Structure

```
RainbowSim/
├── rainbow_web/                 # Web app source
│   ├── main.py                 # Menu system
│   ├── refraction.py           # Simulation modules
│   ├── prism.py
│   ├── raytrace.py
│   ├── droplet.py
│   ├── droplet2.py
│   ├── rainbow.py
│   ├── pyproject.toml          # Build config ✅ NEW
│   ├── requirements.txt         # Dependencies ✅ NEW
│   ├── README.md               # Documentation ✅ NEW
│   └── web/                    # Built web app (created by pygbag)
├── setup.sh                    # Auto-setup script ✅ NEW
├── build.sh                    # Quick build script ✅ NEW
├── Procfile                    # Cloud deployment config ✅ NEW
├── runtime.txt                 # Python version ✅ NEW
├── app.json                    # Heroku config ✅ NEW
├── .gitignore                  # Git ignore ✅ NEW
└── .github/workflows/          # GitHub Actions ✅ NEW
    ├── build.yml              # Auto-build on push
    └── deploy-railway.yml     # Auto-deploy to Railway
```

---

## 📖 Detailed Guides

For detailed information, see:

- **[rainbow_web/BUILD_INSTRUCTIONS.md](rainbow_web/BUILD_INSTRUCTIONS.md)** - Full deployment guide with all options
- **[rainbow_web/README.md](rainbow_web/README.md)** - Feature descriptions and troubleshooting

---

## 🔧 Common Tasks

### Test the build locally
```bash
cd rainbow_web/web
python -m http.server 8000
```
Then open http://localhost:8000

### Rebuild after making changes
```bash
cd rainbow_web
pygbag main.py --build web
```

### Deploy to Railway
```bash
git push origin main
# Railway auto-deploys if connected
```

### View live app
After deployment, visit the URL provided by Railway/Heroku

---

## ⚠️ Important Notes

1. **First Build Takes Time**: Pygbag's initial build can take 5-10 minutes (compiles to WebAssembly)
2. **Browser Requirements**: Needs modern browser (Chrome, Firefox, Safari, Edge)
3. **Interactive Features**: All pygame graphics work in browser, but some system-dependent features may not
4. **Performance**: Web version may be slightly slower than desktop

---

## 🔄 Future Updates

After making changes to your code:

```bash
# Rebuild
cd rainbow_web
pygbag main.py --build web
cd ..

# Update gh-pages branch
git checkout gh-pages
cp -r rainbow_web/web/* .
git add . && git commit -m "Update app" && git push

# Switch back to main
git checkout main
```

---

## 🆘 Troubleshooting

**"Modules not found" error:**
- Ensure all .py files are in `rainbow_web/` directory

**Slow web performance:**
- Use minified build: `pygbag main.py --build web --minify`
- Close other browser tabs

**Build fails:**
- Delete `.pygbag_cache` folder and rebuild
- Ensure Python 3.8+ is installed

See [rainbow_web/BUILD_INSTRUCTIONS.md](rainbow_web/BUILD_INSTRUCTIONS.md#debugging) for more debugging tips.

---

## 🎯 Next Steps

1. **Test locally**: `python rainbow_web/main.py`
2. **Build for web**: `cd rainbow_web && pygbag main.py --build web` (takes 5-10 min first time)
3. **Deploy to GitHub Pages**: Follow the deployment steps above
4. **Share**: Get your GitHub Pages URL and share with others!

---

## 📞 Still Need Help?

Check these resources:
- [Pygbag GitHub](https://github.com/pygame-web/pygbag)
- [Railway Docs](https://docs.railway.app)
- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)

**Happy physics simulating! 🚀**
