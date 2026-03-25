# AlphaForge Installation & Setup Guide

## 🚀 Complete Setup Instructions

### Step 1: Install Backend Dependencies

You're already in the virtual environment, so just install the packages:

```bash
pip3 install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pandas, NumPy (data processing)
- yfinance (stock data)
- And all other dependencies

**Wait for installation to complete** (may take 2-3 minutes)

### Step 2: Start the Backend

Once installation is complete:

```bash
python3 api_server.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal running!**

### Step 3: Install Frontend Dependencies

Open a **NEW terminal** (keep the backend running):

```bash
cd frontend
npm install
```

This installs:
- Next.js
- React
- Framer Motion (animations)
- Recharts (charts)
- All UI dependencies

### Step 4: Start the Frontend

```bash
npm run dev
```

You should see:
```
▲ Next.js 14.2.35
- Local:        http://localhost:3000
- Ready in 2.3s
```

### Step 5: Open Your Browser

Navigate to: **http://localhost:3000**

You'll see:
1. ✨ Premium animated splash screen (2 seconds)
2. 🚀 Automatic redirect to dashboard
3. 💎 Glassmorphism UI with smooth animations

## 🎯 Quick Commands Summary

**Terminal 1 (Backend):**
```bash
source venv/bin/activate
pip3 install -r requirements.txt
python3 api_server.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm install
npm run dev
```

**Browser:**
```
http://localhost:3000
```

## 🔧 Troubleshooting

### Issue: "No module named 'fastapi'"
**Solution:** Run `pip3 install -r requirements.txt`

### Issue: "npm: command not found"
**Solution:** Install Node.js from https://nodejs.org/

### Issue: Port 8000 already in use
**Solution:** 
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
```

### Issue: Port 3000 already in use
**Solution:**
```bash
# Use a different port
PORT=3001 npm run dev
```

### Issue: Virtual environment not working
**Solution:**
```bash
# Recreate virtual environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## 📦 What Gets Installed

### Backend (Python)
- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **yfinance** - Stock market data
- **scikit-learn** - Machine learning
- **networkx** - Graph algorithms
- **Pydantic** - Data validation

### Frontend (Node.js)
- **Next.js 14** - React framework
- **Framer Motion** - Animation library
- **Recharts** - Chart library
- **React Flow** - Graph visualization
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## ✅ Verification

Once both servers are running, verify:

1. **Backend API**: http://localhost:8000/docs
   - Should show FastAPI Swagger documentation

2. **Frontend**: http://localhost:3000
   - Should show premium animated UI

3. **API Connection**: Check browser console
   - Should see successful API calls (or mock data fallback)

## 🎨 Features You'll See

- ✨ Glassmorphism cards with backdrop blur
- 🎭 Smooth Framer Motion animations
- 💎 Gradient text and glowing effects
- ⚡ Loading skeletons
- 🌊 Hover effects with scale and lift
- 🎯 Animated navigation
- 💫 Pulsing status indicators
- 🎪 Staggered list animations

## 🚀 Production Deployment

For production:

**Backend:**
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

## 📝 Next Steps

After successful setup:
1. Explore the dashboard
2. Check out different pages (PGM Graph, Feature Impact, etc.)
3. View the API documentation at http://localhost:8000/docs
4. Customize the configuration in `config/config.yaml`

Enjoy your premium fintech experience! 🎉
