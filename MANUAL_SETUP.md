# Equity Research Assistant Bot - React + FastAPI

## Manual Installation (If automated scripts don't work)

Since you're experiencing PATH issues with Node.js, please follow these manual steps:

### Step 1: Fix Node.js PATH
1. Open Command Prompt as Administrator
2. Run: `setx PATH "%PATH%;C:\Program Files\nodejs" /M`
3. Close all Command Prompt windows and restart them

### Step 2: Verify Node.js Installation
```bash
node --version
npm --version
```

### Step 3: Install Frontend Dependencies
```bash
cd "c:\Users\Niharika Sahu\Documents\GitHub\Equity Research Assistant Bot\frontend"
npm install
```

### Step 4: Start the Application

#### Option A: Use the automated launcher
Double-click on `start_app.bat` in the root directory.

#### Option B: Manual startup
1. **Start Backend (Terminal 1):**
   ```bash
   cd "c:\Users\Niharika Sahu\Documents\GitHub\Equity Research Assistant Bot\backend"
   venv\Scripts\activate
   uvicorn main:app --host 0.0.0.0 --port 8081
   ```

2. **Start Frontend (Terminal 2):**
   ```bash
   cd "c:\Users\Niharika Sahu\Documents\GitHub\Equity Research Assistant Bot\frontend"
   npm start
   ```

3. **Open Browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8081

## Alternative: Using VSCode Terminal

If you're in VSCode, you can use the integrated terminal:

1. Open Terminal in VSCode (Ctrl + `)
2. Split terminal (click the + icon)
3. In first terminal:
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. In second terminal:
   ```bash
   cd frontend
   npm start
   ```

## Features Available

### Backend (FastAPI - Port 8000)
- ✅ File Upload (CSV, Excel, PDF)
- ✅ Stock Analysis with yfinance
- ✅ Document Processing and RAG
- ✅ Agentic RAG for complex queries
- ✅ Chat interface with GROQ API
- ✅ Market overview endpoints

### Frontend (React - Port 3000)
- ✅ Modern Material-UI interface
- ✅ File upload with drag-and-drop
- ✅ Interactive stock charts (Plotly)
- ✅ Real-time chat with bot
- ✅ Document Q&A with RAG
- ✅ Market overview dashboard
- ✅ Responsive design

## Troubleshooting

### If npm install fails:
1. Run Command Prompt as Administrator
2. Try: `npm install --force`
3. Or: `npm cache clean --force && npm install`

### If ports are in use:
- Backend: Change port in backend/main.py (line with uvicorn)
- Frontend: React will automatically use next available port

### If GROQ API doesn't work:
- Check your .env file in backend folder
- Ensure GROQ_API_KEY is set correctly

## Performance Comparison

**Streamlit vs React:**
- Streamlit: ~2-3 second page loads, limited interactivity
- React: <1 second navigation, real-time updates, better UX

**Benefits of React Version:**
- 🚀 Faster loading and navigation
- 🎨 Better UI/UX with Material Design
- 📱 Mobile responsive
- ⚡ Real-time updates without page refresh
- 🔄 Better state management
- 📊 Interactive charts and visualizations
