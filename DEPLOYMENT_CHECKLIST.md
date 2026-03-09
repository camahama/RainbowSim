# ✅ RainbowSim Deployment Checklist

Use this checklist to ensure everything is ready before deploying.

## Pre-Deployment (Local Testing)

- [ ] Run setup: `./setup.sh`
- [ ] Test locally: `cd rainbow_web && python main.py`
- [ ] Click through all 6 simulations in the menu
- [ ] Verify no errors in terminal
- [ ] Test on mobile/tablet if possible

## Build Process

- [ ] Build for web: `pygbag rainbow_web/main.py --build web`
- [ ] Build completes without errors
- [ ] Verify `/rainbow_web/web/` directory exists
- [ ] Test built version: `cd rainbow_web/web && python -m http.server 8000`
- [ ] Open http://localhost:8000 in browser
- [ ] All simulations work in browser version

## Code Cleanup

- [ ] Remove debug print statements (if any)
- [ ] Clean up unused imports
- [ ] Verify all Python files are in `rainbow_web/`
- [ ] Check for hardcoded file paths (should be relative)

## Repository Setup

- [ ] Initialize Git (if not done): `git init`
- [ ] Create `.gitignore` ✅ Done!
- [ ] Create `.github/workflows/` ✅ Done!
- [ ] Commit files: `git add . && git commit -m "Initial commit"`
- [ ] Push to GitHub (create repo first)

## Deployment Choice

### If Deploying to Railway (Recommended)

- [ ] Create Railway account: https://railway.app
- [ ] Verify `Procfile` exists ✅ Done!
- [ ] Verify `runtime.txt` exists ✅ Done!
- [ ] Connect Railway to your GitHub repo
- [ ] Railway detects and deploys automatically
- [ ] Get your Railway URL
- [ ] Test the live URL

### If Deploying to Heroku

- [ ] Install Heroku CLI: `brew install heroku/brew/heroku`
- [ ] Create Heroku account: https://heroku.com
- [ ] Login: `heroku login`
- [ ] Create app: `heroku create your-app-name`
- [ ] Deploy: `git push heroku main`
- [ ] Get your Heroku URL: `heroku apps:info`
- [ ] Test the live URL

### If Using GitHub Pages

- [ ] Build locally: `pygbag rainbow_web/main.py --build web`
- [ ] Create deployment branch: `git checkout --orphan gh-pages`
- [ ] Copy `/web` contents to root: `cp -r rainbow_web/web/* .`
- [ ] Commit and push: `git add . && git push -u origin gh-pages`
- [ ] Enable Pages in GitHub Settings → Pages
- [ ] Verify URL is available

## Post-Deployment

- [ ] Test all 6 simulations on live URL
- [ ] Test on different browsers
- [ ] Check console for JavaScript errors (F12)
- [ ] Test on mobile device
- [ ] Verify loading time is acceptable
- [ ] Share URL with others!

## Performance Optimization (Optional)

- [ ] Build minified version: `pygbag rainbow_web/main.py --build web --minify`
- [ ] Enable browser caching (platform-specific)
- [ ] Test with slow internet connection
- [ ] Monitor performance metrics

## Documentation

- [ ] Update `rainbow_web/README.md` with your deployment URL
- [ ] Add screenshots to documentation
- [ ] Document any customizations made
- [ ] Add your name/license information

## Backup & Maintenance

- [ ] Create GitHub backup of entire repository
- [ ] Document any system requirements
- [ ] Plan for future updates
- [ ] Consider version control tags

---

## Quick Reference

### Setup
```bash
./setup.sh
```

### Build
```bash
cd rainbow_web
pygbag main.py --build web
```

### Test Locally
```bash
cd rainbow_web/web
python -m http.server 8000
```

### Deploy
```bash
git push origin main  # Railway auto-deploys
# OR
git push heroku main  # For Heroku
```

---

## After Successful Deployment

✨ Your app is now live! Consider:

- [ ] Add link to your website/portfolio
- [ ] Share on social media with screenshot
- [ ] Document how it works
- [ ] Gather feedback from users
- [ ] Plan feature additions

---

**Status**: Your setup is ✅ **COMPLETE**

All files have been configured. Just follow the checklist above and deploy!
