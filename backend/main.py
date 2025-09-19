"""
FastAPI Backend for Equity Research Assistant
High-performance API server to replace Streamlit
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import io
import os
from datetime import datetime, timedelta
import yfinance as yf
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Import our custom modules
import sys
sys.path.append('..')
from utils import DataProcessor, FinancialAnalyzer

# Simple equity research bot class
class EquityResearchBot:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.analyzer = FinancialAnalyzer()
    
    def load_csv_file(self, file_content):
        """Load and process CSV file"""
        try:
            data = pd.read_csv(file_content)
            data = self.data_processor.clean_financial_data(data)
            return data, f"Successfully loaded {len(data)} rows"
        except Exception as e:
            return None, f"Error loading CSV: {str(e)}"
    
    def load_excel_file(self, file_content):
        """Load and process Excel file"""
        try:
            data = pd.read_excel(file_content)
            data = self.data_processor.clean_financial_data(data)
            return data, f"Successfully loaded {len(data)} rows"
        except Exception as e:
            return None, f"Error loading Excel: {str(e)}"
    
    def load_pdf_file(self, file_content):
        """Extract text from PDF file"""
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(file_content)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text, f"Successfully extracted {len(text)} characters"
        except Exception as e:
            return None, f"Error loading PDF: {str(e)}"
    
    def get_stock_data(self, symbol):
        """Fetch stock data using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1y")
            if hist.empty:
                return None, f"No data found for symbol {symbol}"
            return hist, info
        except Exception as e:
            return None, f"Error fetching stock data: {str(e)}"
    
    def create_financial_charts(self, data):
        """Create financial charts from data"""
        charts = []
        try:
            if 'Close' in data.columns:
                # Price chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='blue')
                ))
                fig.update_layout(
                    title='Stock Price Over Time',
                    xaxis_title='Date',
                    yaxis_title='Price ($)',
                    height=400
                )
                charts.append(fig)
                
                # Volume chart if available
                if 'Volume' in data.columns:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(
                        x=data.index,
                        y=data['Volume'],
                        name='Volume',
                        marker_color='green'
                    ))
                    fig2.update_layout(
                        title='Trading Volume',
                        xaxis_title='Date',
                        yaxis_title='Volume',
                        height=400
                    )
                    charts.append(fig2)
            
            elif len(data.select_dtypes(include=[np.number]).columns) > 0:
                # Generic numeric data chart
                numeric_cols = data.select_dtypes(include=[np.number]).columns[:5]
                fig = go.Figure()
                for col in numeric_cols:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data[col],
                        mode='lines',
                        name=col
                    ))
                fig.update_layout(
                    title='Data Visualization',
                    xaxis_title='Index',
                    yaxis_title='Value',
                    height=400
                )
                charts.append(fig)
        
        except Exception as e:
            print(f"Chart creation error: {e}")
        
        return charts

# Import RAG components
try:
    from rag_system import RAGPipeline, ChatBot
    from agentic_rag import FinancialAnalysisAgent
    HAS_RAG = True
    RAG_TYPE = "ChromaDB + Agentic RAG"
except ImportError:
    try:
        from simple_rag import SimpleRAGPipeline, SimpleChatBot
        from agentic_rag import FinancialAnalysisAgent
        RAGPipeline = SimpleRAGPipeline
        ChatBot = SimpleChatBot
        HAS_RAG = True
        RAG_TYPE = "Simple + Agentic RAG"
    except ImportError:
        HAS_RAG = False
        RAG_TYPE = "Unavailable"

# Initialize FastAPI app
app = FastAPI(
    title="Equity Research Assistant API",
    description="High-performance API for financial analysis and agentic RAG",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for singleton services
equity_bot = None
rag_pipeline = None
chatbot = None
agentic_rag = None
groq_client = None

# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict] = None

class ChatRequest(BaseModel):
    message: str
    mode: str = "agentic"  # agentic, standard, search
    context_data: Optional[Dict] = None

class ChatResponse(BaseModel):
    message: str
    metadata: Optional[Dict] = None
    success: bool = True
    error: Optional[str] = None

class StockRequest(BaseModel):
    symbol: str

class AnalysisRequest(BaseModel):
    query: str
    data: Optional[Dict] = None

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    data_preview: Optional[Dict] = None
    charts: Optional[List[Dict]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global equity_bot, rag_pipeline, chatbot, agentic_rag, groq_client
    
    try:
        # Initialize GROQ client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        groq_client = Groq(api_key=api_key)
        
        # Initialize equity research bot
        equity_bot = EquityResearchBot()
        
        # Initialize RAG pipeline if available
        if HAS_RAG:
            rag_pipeline = RAGPipeline()
            chatbot = ChatBot(rag_pipeline, groq_client)
            
            # Initialize Agentic RAG
            try:
                agentic_rag = FinancialAnalysisAgent(rag_pipeline, groq_client)
                print(f"✅ Agentic RAG initialized successfully")
            except Exception as e:
                print(f"⚠️ Agentic RAG initialization failed: {e}")
                agentic_rag = None
        
        print(f"🚀 Backend services initialized. RAG Status: {RAG_TYPE}")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Equity Research Assistant API",
        "status": "running",
        "rag_available": HAS_RAG,
        "rag_type": RAG_TYPE,
        "agentic_available": agentic_rag is not None
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "api_status": "healthy",
        "groq_client": groq_client is not None,
        "equity_bot": equity_bot is not None,
        "rag_pipeline": rag_pipeline is not None,
        "agentic_rag": agentic_rag is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and process CSV file"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file content
        content = await file.read()
        print(f"File size: {len(content)} bytes")
        
        # Process with equity bot
        data, message = equity_bot.load_csv_file(io.BytesIO(content))
        
        if data is None:
            print(f"Data processing failed: {message}")
            raise HTTPException(status_code=400, detail=message)
        
        print(f"Data loaded successfully: {data.shape}")
        
        # Create charts
        try:
            charts = equity_bot.create_financial_charts(data)
            print(f"Created {len(charts)} charts")
        except Exception as chart_error:
            print(f"Chart creation failed: {chart_error}")
            charts = []
        
        # Convert charts to JSON for frontend
        chart_json = []
        try:
            for chart in charts:
                # Convert to JSON string then parse back to dict for Pydantic
                chart_dict = json.loads(chart.to_json())
                chart_json.append(chart_dict)
        except Exception as json_error:
            print(f"Chart JSON conversion failed: {json_error}")
            chart_json = []
        
        # Add to RAG pipeline if available
        rag_message = ""
        if rag_pipeline:
            try:
                rag_message = rag_pipeline.add_document(
                    io.BytesIO(content), file.filename, 'csv'
                )
            except Exception as e:
                print(f"RAG processing error: {e}")
                rag_message = f"RAG error: {str(e)}"
        
        return FileUploadResponse(
            success=True,
            message=f"{message}. {rag_message}",
            data_preview={
                "shape": data.shape,
                "columns": data.columns.tolist(),
                "head": data.head().to_dict('records'),
                "dtypes": data.dtypes.astype(str).to_dict()
            },
            charts=chart_json
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/upload/excel")
async def upload_excel(file: UploadFile = File(...)):
    """Upload and process Excel file"""
    try:
        if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            raise HTTPException(status_code=400, detail="File must be Excel format")
        
        content = await file.read()
        data, message = equity_bot.load_excel_file(io.BytesIO(content))
        
        if data is None:
            raise HTTPException(status_code=400, detail=message)
        
        charts = equity_bot.create_financial_charts(data)
        chart_json = [chart.to_json() for chart in charts]
        
        # Add to RAG
        rag_message = ""
        if rag_pipeline:
            try:
                rag_message = rag_pipeline.add_document(
                    io.BytesIO(content), file.filename, 'excel'
                )
            except Exception as e:
                rag_message = f"RAG error: {str(e)}"
        
        return FileUploadResponse(
            success=True,
            message=f"{message}. {rag_message}",
            data_preview={
                "shape": data.shape,
                "columns": data.columns.tolist(),
                "head": data.head().to_dict('records'),
                "dtypes": data.dtypes.astype(str).to_dict()
            },
            charts=chart_json
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        content = await file.read()
        text, message = equity_bot.load_pdf_file(io.BytesIO(content))
        
        if text is None:
            raise HTTPException(status_code=400, detail=message)
        
        # Add to RAG
        rag_message = ""
        if rag_pipeline:
            try:
                rag_message = rag_pipeline.add_document(
                    io.BytesIO(content), file.filename, 'pdf'
                )
            except Exception as e:
                rag_message = f"RAG error: {str(e)}"
        
        return FileUploadResponse(
            success=True,
            message=f"{message}. {rag_message}",
            data_preview={
                "text_length": len(text),
                "word_count": len(text.split()),
                "preview": text[:500] + "..." if len(text) > 500 else text
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stock/fetch")
async def fetch_stock_data(request: StockRequest):
    """Fetch stock data for given symbol"""
    try:
        stock_data, stock_info = equity_bot.get_stock_data(request.symbol)
        
        if stock_data is None:
            raise HTTPException(status_code=404, detail=stock_info)
        
        # Create stock charts
        charts = equity_bot.create_financial_charts(stock_data)
        
        # Convert charts to JSON for frontend (same fix as upload endpoints)
        chart_json = []
        try:
            for chart in charts:
                # Convert to JSON string then parse back to dict for Pydantic
                chart_dict = json.loads(chart.to_json())
                chart_json.append(chart_dict)
        except Exception as json_error:
            print(f"Chart JSON conversion failed: {json_error}")
            chart_json = []
        
        return {
            "success": True,
            "symbol": request.symbol,
            "stock_info": stock_info,
            "stock_data": {
                "shape": stock_data.shape,
                "columns": stock_data.columns.tolist(),
                "data": stock_data.tail(30).to_dict('records'),  # Last 30 days
                "latest_price": float(stock_data['Close'].iloc[-1]),
                "price_change": float(stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2])
            },
            "charts": chart_json
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Enhanced chat endpoint with agentic RAG"""
    try:
        if request.mode == "agentic" and agentic_rag:
            # Use Agentic RAG
            result = agentic_rag.process_query(request.message, request.context_data or {})
            
            if result['success']:
                # Clean up intermediate results for frontend
                clean_intermediate_results = {}
                if result.get('intermediate_results', {}).get('steps'):
                    for step_key, step_data in result['intermediate_results']['steps'].items():
                        clean_intermediate_results[f"Step {step_key}"] = {
                            'step_description': step_data.get('description', ''),
                            'tool': step_data.get('tool', ''),
                            'result': str(step_data.get('result', ''))[:500] + "..." if len(str(step_data.get('result', ''))) > 500 else str(step_data.get('result', '')),
                            'success': step_data.get('success', False)
                        }
                
                # Clean up plan for frontend
                clean_plan = []
                if result.get('plan'):
                    for step in result['plan']:
                        if isinstance(step, dict):
                            clean_plan.append(step.get('description', str(step)))
                        else:
                            clean_plan.append(str(step))
                
                return ChatResponse(
                    message=result['answer'],
                    metadata={
                        'plan': clean_plan,
                        'confidence': result.get('confidence', 0.0),
                        'sources': result.get('sources', []),
                        'intermediate_results': clean_intermediate_results,
                        'mode': 'agentic'
                    },
                    success=True
                )
            else:
                return ChatResponse(
                    message=result['answer'],
                    success=False,
                    error="Agentic analysis failed"
                )
        
        elif request.mode == "search" and rag_pipeline:
            # Document search mode
            search_results = rag_pipeline.search_documents(request.message, n_results=5)
            
            if search_results and 'error' not in search_results[0]:
                response_text = f"Found {len(search_results)} relevant results:\n\n"
                sources = []
                
                for i, result in enumerate(search_results[:3]):
                    response_text += f"**Result {i+1}** (Relevance: {result['relevance_score']:.2f}):\n"
                    response_text += f"{result['content'][:300]}...\n\n"
                    sources.append(result['metadata'].get('filename', 'Unknown'))
                
                return ChatResponse(
                    message=response_text,
                    metadata={
                        'sources': sources,
                        'mode': 'search',
                        'results_count': len(search_results)
                    },
                    success=True
                )
            else:
                return ChatResponse(
                    message="No relevant documents found for your query.",
                    success=False
                )
        
        else:
            # Standard chat mode
            if chatbot:
                response = chatbot.get_response(request.message)
                return ChatResponse(
                    message=response,
                    metadata={'mode': 'standard'},
                    success=True
                )
            else:
                return ChatResponse(
                    message="Chat service unavailable",
                    success=False,
                    error="Chatbot not initialized"
                )
    
    except Exception as e:
        return ChatResponse(
            message=f"An error occurred: {str(e)}",
            success=False,
            error=str(e)
        )

@app.get("/rag/stats")
async def get_rag_stats():
    """Get RAG database statistics"""
    try:
        if not rag_pipeline:
            return {"error": "RAG not available"}
        
        stats = rag_pipeline.get_collection_stats()
        return stats
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/rag/search")
async def search_documents(query: str, n_results: int = 10):
    """Search documents in RAG database"""
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=400, detail="RAG not available")
        
        results = rag_pipeline.search_documents(query, n_results=n_results)
        
        if results and 'error' not in results[0]:
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
        else:
            return {
                "success": False,
                "error": results[0].get('error', 'No results found') if results else 'No results found'
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/rag/clear")
async def clear_rag_database():
    """Clear RAG database"""
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=400, detail="RAG not available")
        
        message = rag_pipeline.clear_database()
        return {"success": True, "message": message}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/market-overview")
async def get_market_overview():
    """Get market overview data"""
    try:
        # Popular stocks for demo
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA']
        market_data = {}
        
        for symbol in symbols:
            try:
                stock_data, stock_info = equity_bot.get_stock_data(symbol)
                if stock_data is not None and not stock_data.empty:
                    latest_price = float(stock_data['Close'].iloc[-1])
                    price_change = float(stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2])
                    change_percent = (price_change / stock_data['Close'].iloc[-2]) * 100
                    
                    market_data[symbol] = {
                        "price": latest_price,
                        "change": price_change,
                        "change_percent": change_percent,
                        "company_name": stock_info.get('longName', symbol),
                        "market_cap": stock_info.get('marketCap', 0)
                    }
            except:
                continue
        
        return {
            "success": True,
            "market_data": market_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
