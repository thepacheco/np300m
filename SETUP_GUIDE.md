# 🚀 GitHub & Render.com Setup Guide

Complete step-by-step guide to get your trading system online and accessible from your iPad!

## 📋 What You'll Need

- [ ] GitHub account (free) - https://github.com
- [ ] Render.com account (free) - https://render.com
- [ ] Git installed on your computer (or use GitHub Desktop)

---

## PART 1: Create GitHub Account & Repository

### Step 1: Sign Up for GitHub

1. Go to https://github.com/signup
2. Enter your email, create password, choose username
3. Verify your email
4. Choose "Free" plan

### Step 2: Create a New Repository

1. Click the **+** icon in top right → **New repository**
2. Repository name: `trading-analysis-system` (or whatever you want)
3. Description: `Live trading analysis for IRA investments`
4. Choose **Public** (so Render can access it) or **Private** (need to connect GitHub to Render)
5. Check **"Add a README file"** - we'll replace it
6. Click **Create repository**

### Step 3: Upload Your Files to GitHub

**Option A: Using GitHub Web Interface (Easiest)**

1. In your new repository, click **"Add file"** → **"Upload files"**
2. Drag and drop ALL these files:
   - `trading_system.py`
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `README.md`
   - `.gitignore`
   - Your `backtest.py` (optional, for reference)

3. Write commit message: "Initial commit - Trading system"
4. Click **"Commit changes"**

**Option B: Using Git Command Line**

```bash
# Navigate to your project folder
cd /path/to/your/trading-system

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Trading system"

# Connect to GitHub (replace YOUR-USERNAME and REPO-NAME)
git remote add origin https://github.com/YOUR-USERNAME/REPO-NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Option C: Using GitHub Desktop (Visual)**

1. Download GitHub Desktop: https://desktop.github.com
2. Install and sign in with your GitHub account
3. File → Add Local Repository → Choose your folder
4. Write commit message and click "Commit to main"
5. Click "Publish repository" in top right

---

## PART 2: Deploy to Render.com

### Step 1: Sign Up for Render

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account** (this is important!)
4. Authorize Render to access your GitHub

### Step 2: Create a New Web Service

1. Click **"New +"** button in top right
2. Select **"Web Service"**
3. Connect your GitHub repository:
   - If you don't see it, click "Configure account" → Give Render access
   - Select your `trading-analysis-system` repository
4. Click **"Connect"**

### Step 3: Configure the Service

Fill out the form:

**Basics:**
- **Name**: `trading-analysis` (or whatever - this will be in your URL)
- **Region**: Choose closest to you (e.g., Oregon if in US West)
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app` (should auto-fill from Procfile)

**Instance Type:**
- Choose **"Free"** ($0/month)
  - ⚠️ Note: Free tier sleeps after 15 min of inactivity
  - Takes 30-60 seconds to wake up when you visit
  - Perfect for personal use!

**Advanced (Optional):**
- Auto-Deploy: **Yes** (updates when you push to GitHub)

### Step 4: Deploy!

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for first deployment
3. Watch the logs - you'll see:
   ```
   Installing requirements...
   Starting server...
   Your service is live!
   ```

### Step 5: Get Your URL

Once deployed, you'll see:
```
https://trading-analysis-XXXX.onrender.com
```

**This is your iPad URL!** 🎉

Bookmark it on your iPad for easy access.

---

## PART 3: Access from Your iPad

### Testing Your App

1. Open Safari on your iPad
2. Go to your Render URL: `https://trading-analysis-XXXX.onrender.com`
3. **First load**: May take 30-60 seconds (free tier wakes up)
4. You should see the trading dashboard!

### Add to Home Screen (Makes it feel like an app)

1. In Safari, tap the **Share** button (square with arrow)
2. Scroll down and tap **"Add to Home Screen"**
3. Name it: "Trading Analysis"
4. Tap **"Add"**
5. Now you have an app icon on your iPad! 📱

### Bookmark for Quick Access

1. In Safari, tap the **Share** button
2. Tap **"Add Bookmark"**
3. Save to "Favorites" for easy access

---

## PART 4: Making Updates

### When You Want to Change Code

**Method 1: GitHub Web Interface**
1. Go to your repository on github.com
2. Click on the file you want to edit (e.g., `app.py`)
3. Click the pencil icon (Edit)
4. Make your changes
5. Click "Commit changes"
6. Render will auto-deploy in ~5 minutes

**Method 2: Git Command Line**
```bash
# Make your changes to files

# Add changes
git add .

# Commit
git commit -m "Updated settings panel"

# Push to GitHub
git push

# Render auto-deploys!
```

### When You Want to Change Settings

Just use the web interface! Settings save to `trading_config.json` automatically.

---

## 🎯 Usage Workflow

### Daily Use:

1. **Morning** (before market opens):
   - Open app on iPad
   - Click **UPDATE** to refresh
   - Click **ANALYZE** (takes 2-5 min)
   - Click **RESULTS** to see recommendations

2. **Review Results**:
   - Look for scores 70+
   - Check the reasoning
   - Verify news sentiment
   - Note the price targets

3. **Set Alerts in Your Broker**:
   - Use the "Current Price" as entry
   - Set alerts at "Today High" and "Week Target"
   - Enter position when alert triggers
   - Use "Stop Loss" and "Take Profit" levels

4. **Track Performance**:
   - Keep a simple spreadsheet
   - Track which recommendations work
   - Adjust settings as needed

---

## 🔧 Troubleshooting

### "Application Error" on Render

**Check Logs:**
1. Go to Render dashboard
2. Click your service
3. Click "Logs" tab
4. Look for errors

**Common Issues:**
- Missing dependency → Add to `requirements.txt`
- Python version → Render uses Python 3.7+ by default
- Port binding → Code uses correct `app.run(host='0.0.0.0')`

### App is Slow

**Free Tier Limitations:**
- Sleeps after 15 min inactivity
- First request takes 30-60 sec to wake
- **Solution**: Upgrade to paid tier ($7/mo) for always-on

### Can't Connect to GitHub

1. Go to Render dashboard
2. Settings → GitHub connection
3. Reconnect your account
4. Give Render access to your repository

### Analysis Times Out

**Too many stocks:**
1. Open settings
2. Disable some sectors
3. Reduce "Top Opportunities" to 10
4. Save settings

### Wrong Data

**Yahoo Finance issues:**
- Sometimes data is delayed
- Try running UPDATE again
- Check specific stock on yahoo.com

---

## 📊 Monitoring & Maintenance

### Check Render Status
- Dashboard shows uptime
- Logs show any errors
- Free tier gets 750 hours/month (enough for daily use)

### Update Dependencies
If packages get outdated:
1. Edit `requirements.txt` on GitHub
2. Update version numbers
3. Commit changes
4. Render will rebuild

### Backup Your Config
Download `trading_config.json` occasionally:
1. Can't access directly on Render
2. But your settings persist between deploys
3. To reset: delete file via code update

---

## 💡 Tips for Success

1. **Bookmark the URL** - Don't lose it!
2. **Test with Paper Money** - Before real trades
3. **Run Analysis Daily** - Before market open
4. **Check Multiple Timeframes** - Don't just look at "today"
5. **Verify News** - Sentiment analysis is simple, double-check
6. **Start Small** - Don't use full capital at once
7. **Track Results** - See what scores actually work

---

## 🆘 Getting Help

### Render Support
- https://render.com/docs
- Community forum
- Live chat for paid users

### GitHub Help
- https://docs.github.com
- GitHub Community
- Lots of YouTube tutorials

### Code Issues
- Check the README.md
- Review comments in code
- Test locally first: `python app.py`

---

## 🎓 Next Steps

Once everything is working:

1. **Week 1**: Just observe, don't trade
2. **Week 2**: Paper trade recommendations
3. **Week 3**: Small real trades ($100-200)
4. **Week 4+**: Scale up if profitable

**Remember:**
- This is a tool, not magic
- Markets are unpredictable
- Risk management is crucial
- Never invest what you can't afford to lose

---

## ✅ Checklist

Setup Complete When:
- [ ] GitHub account created
- [ ] Repository created with all files
- [ ] Render account created
- [ ] Service deployed successfully
- [ ] Can access URL from iPad
- [ ] App added to iPad home screen
- [ ] Settings configured
- [ ] Test analysis run successfully
- [ ] Results displaying correctly

---

**You're all set!** 🚀

Your trading system is now accessible from anywhere via your iPad. Happy trading! 📈

Remember: **Trade smart, not hard.** Start small, learn the system, and only risk what you can afford to lose.
