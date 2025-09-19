import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import PyPDF2
import io
import os
from dotenv import load_dotenv
from groq import Groq
import yfinance as yf
from datetime import datetime, timedelta

# Try to import RAG system, make it optional
try:
    from rag_system import RAGPipeline, ChatBot
    from agentic_rag import FinancialAnalysisAgent
    HAS_RAG = True
    RAG_TYPE = "ChromaDB + Agentic RAG"
except ImportError:
    try:
        from simple_rag import RAGPipeline, ChatBot
        from agentic_rag import FinancialAnalysisAgent
        HAS_RAG = True
        RAG_TYPE = "Simple + Agentic RAG"
    except ImportError as e:
        HAS_RAG = False
        RAG_ERROR = str(e)
        # Create dummy classes for when RAG is not available
        class RAGPipeline:
            pass
        class ChatBot:
            pass

# Optional imports for additional visualization
try:
    import seaborn as sns
    import matplotlib.pyplot as plt
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

# Load environment variables
load_dotenv()

# Initialize GROQ client
client = Groq(
    api_key=os.getenv('GROQ_API_KEY')
)

# Page configuration
st.set_page_config(
    page_title="Equity Research Assistant Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/equity-research-bot',
        'Report a bug': "https://github.com/your-repo/equity-research-bot/issues",
        'About': "# Equity Research Assistant Bot\nAI-powered financial analysis with RAG capabilities"
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --warning-color: #ff7f0e;
        --error-color: #d62728;
        --background-color: #f8f9fa;
        --sidebar-bg: #ffffff;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #1f77b4 0%, #17a2b8 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin-bottom: 0;
        opacity: 0.9;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .status-success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .status-info {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
    }
    
    .sidebar-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #495057;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Chat styling */
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    .chat-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    
    .chat-assistant {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        margin-right: 20%;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* File upload area */
    .upload-area {
        border: 2px dashed #007bff;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #0056b3;
        background: #e6f3ff;
    }
    
    /* Progress indicators */
    .progress-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        color: var(--primary-color);
    }
    
    /* Hide default streamlit styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .chat-user, .chat-assistant {
            margin-left: 0;
            margin-right: 0;
        }
    }
</style>
""", unsafe_allow_html=True)

class EquityResearchBot:
    def __init__(self):
        self.data = None
        self.analysis_results = {}
    
    def load_csv_file(self, uploaded_file):
        """Load CSV file and return DataFrame"""
        try:
            df = pd.read_csv(uploaded_file)
            return df, "CSV file loaded successfully!"
        except Exception as e:
            return None, f"Error loading CSV: {str(e)}"
    
    def load_excel_file(self, uploaded_file):
        """Load Excel file and return DataFrame"""
        try:
            df = pd.read_excel(uploaded_file)
            return df, "Excel file loaded successfully!"
        except Exception as e:
            return None, f"Error loading Excel: {str(e)}"
    
    def load_pdf_file(self, uploaded_file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text, "PDF file loaded successfully!"
        except Exception as e:
            return None, f"Error loading PDF: {str(e)}"
    
    def analyze_with_groq(self, prompt, context=""):
        """Send analysis request to GROQ API"""
        try:
            full_prompt = f"""
            You are an expert equity research analyst. Analyze the following data and provide insights:
            
            Context: {context}
            
            Request: {prompt}
            
            Please provide a comprehensive analysis including:
            1. Key findings
            2. Investment recommendations
            3. Risk assessment
            4. Market outlook
            """
            
            completion = client.chat.completions.create(
                model="llama3-8b-8192",  # Updated to supported model
                messages=[
                    {"role": "system", "content": "You are an expert equity research analyst with deep knowledge of financial markets, valuation methods, and investment strategies."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error with GROQ analysis: {str(e)}"
    
    def create_financial_charts(self, df):
        """Create financial visualization charts"""
        charts = []
        
        # Detect common financial columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # Time series chart if date column exists
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols and len(numeric_cols) > 0:
                fig = px.line(df, x=date_cols[0], y=numeric_cols[0], 
                             title=f"{numeric_cols[0]} Over Time")
                charts.append(fig)
            
            # Correlation heatmap
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                fig = px.imshow(corr_matrix, 
                               title="Correlation Matrix",
                               color_continuous_scale="RdBu_r")
                charts.append(fig)
            
            # Distribution plot
            fig = px.histogram(df, x=numeric_cols[0], 
                              title=f"Distribution of {numeric_cols[0]}")
            charts.append(fig)
        
        return charts
    
    def get_stock_data(self, symbol, period="1y"):
        """Fetch stock data using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            info = ticker.info
            return data, info
        except Exception as e:
            return None, f"Error fetching stock data: {str(e)}"

def main():
    # Custom header
    st.markdown("""
    <div class="main-header">
        <h1>📈 Equity Research Assistant Bot</h1>
        <p>AI-powered financial analysis with advanced document processing and real-time insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show RAG system status with enhanced styling
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if HAS_RAG:
            st.markdown(f'<div class="status-badge status-success">✅ RAG System: {RAG_TYPE}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-badge status-warning">⚠️ RAG Unavailable</div>', unsafe_allow_html=True)
    
    with col2:
        # Show current time and session info
        current_time = datetime.now().strftime("%H:%M:%S")
        st.markdown(f'<div class="status-badge status-info">🕒 Session: {current_time}</div>', unsafe_allow_html=True)
    
    with col3:
        # Quick stats
        if 'session_stats' not in st.session_state:
            st.session_state.session_stats = {'files_processed': 0, 'queries_made': 0}
        
        stats = st.session_state.session_stats
        st.markdown(f'<div class="status-badge status-info">📊 Files: {stats["files_processed"]} | Queries: {stats["queries_made"]}</div>', unsafe_allow_html=True)
    
    # Initialize the bot
    if 'bot' not in st.session_state:
        st.session_state.bot = EquityResearchBot()
    
    # Initialize RAG pipeline and chatbot if available
    if HAS_RAG:
        if 'rag_pipeline' not in st.session_state:
            st.session_state.rag_pipeline = RAGPipeline()
        
        if 'chatbot' not in st.session_state:
            st.session_state.chatbot = ChatBot(st.session_state.rag_pipeline, client)
        
        # Initialize Agentic RAG
        if 'agentic_rag' not in st.session_state:
            try:
                st.session_state.agentic_rag = FinancialAnalysisAgent(st.session_state.rag_pipeline, client)
            except Exception as e:
                st.session_state.agentic_rag = None
                st.warning(f"Agentic RAG initialization failed: {e}")
        
        # Enhanced tabs with icons and descriptions
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Data Analysis", 
            "🤖 AI Chatbot", 
            "⚙️ RAG Management",
            "📈 Market Dashboard"
        ])
        
        with tab1:
            data_analysis_tab()
        
        with tab2:
            chatbot_tab()
        
        with tab3:
            rag_management_tab()
            
        with tab4:
            market_dashboard_tab()
    else:
        # Enhanced error message with actionable steps
        st.error("🔧 RAG functionality is currently unavailable")
        
        with st.expander("💡 How to enable RAG features"):
            st.markdown("""
            **To unlock the full potential of the Equity Research Assistant:**
            
            1. **Install required packages:**
            ```bash
            pip install chromadb langchain sentence-transformers tiktoken
            ```
            
            2. **Restart the application:**
            ```bash
            streamlit run app.py
            ```
            
            3. **Features you'll unlock:**
            - 🤖 AI Chatbot with document context
            - 🔍 Semantic search through your documents
            - 💬 Conversation history and follow-ups
            - 📚 Knowledge base management
            """)
        
        # Show basic data analysis tab only
        data_analysis_tab_basic()

def data_analysis_tab_basic():
    """Basic data analysis functionality when RAG is not available"""
    
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">📁 File Upload Center</div>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['csv', 'xlsx', 'xls', 'pdf'],
            accept_multiple_files=True,
            help="Upload CSV, Excel, or PDF files for analysis",
            key="basic_upload"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">🔧 Configuration</div>', unsafe_allow_html=True)
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Financial Analysis", "Stock Performance", "Risk Assessment", "Market Comparison"]
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">📊 Stock Lookup</div>', unsafe_allow_html=True)
        stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL)")
        if st.button("Fetch Stock Data"):
            if stock_symbol:
                with st.spinner("Fetching stock data..."):
                    stock_data, stock_info = st.session_state.bot.get_stock_data(stock_symbol)
                    if stock_data is not None:
                        st.session_state.stock_data = stock_data
                        st.session_state.stock_info = stock_info
                        st.session_state.current_stock_symbol = stock_symbol  # Store the symbol
                        st.success(f"Stock data for {stock_symbol} loaded!")
                        st.session_state.session_stats['queries_made'] += 1
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Main content area with enhanced layout
    if uploaded_files:
        st.markdown("### 📋 File Processing Center")
        
        for idx, uploaded_file in enumerate(uploaded_files):
            with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    data, message = st.session_state.bot.load_csv_file(uploaded_file)
                    if data is not None:
                        st.success(f"✅ {message}")
                        st.dataframe(data.head(10), use_container_width=True)
                        st.session_state.current_data = data
                        st.session_state.session_stats['files_processed'] += 1
                        
                        charts = st.session_state.bot.create_financial_charts(data)
                        if charts:
                            for i, chart in enumerate(charts):
                                st.plotly_chart(chart, use_container_width=True, key=f"basic_chart_{idx}_{i}")
                    else:
                        st.error(f"❌ {message}")
                
                elif file_extension in ['xlsx', 'xls']:
                    data, message = st.session_state.bot.load_excel_file(uploaded_file)
                    if data is not None:
                        st.success(f"✅ {message}")
                        st.dataframe(data.head(10), use_container_width=True)
                        st.session_state.current_data = data
                        st.session_state.session_stats['files_processed'] += 1
                        
                        charts = st.session_state.bot.create_financial_charts(data)
                        if charts:
                            for i, chart in enumerate(charts):
                                st.plotly_chart(chart, use_container_width=True, key=f"basic_excel_chart_{idx}_{i}")
                    else:
                        st.error(f"❌ {message}")
                
                elif file_extension == 'pdf':
                    text, message = st.session_state.bot.load_pdf_file(uploaded_file)
                    if text is not None:
                        st.success(f"✅ {message}")
                        preview_text = text[:2000] + "..." if len(text) > 2000 else text
                        st.text_area("Content", preview_text, height=200, key=f"basic_pdf_{idx}")
                        st.session_state.pdf_content = text
                        st.session_state.session_stats['files_processed'] += 1
                    else:
                        st.error(f"❌ {message}")
    
    else:
        # Enhanced empty state
        st.markdown("""
        <div class="upload-area">
            <h3>📁 Ready to Start Your Analysis?</h3>
            <p>Upload your financial documents using the sidebar to begin</p>
            <p><strong>Supported formats:</strong> CSV, Excel (XLS/XLSX), PDF</p>
            <p><em>💡 Tip: You can upload multiple files at once!</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show current stock data if available
    if hasattr(st.session_state, 'stock_data') and st.session_state.stock_data is not None:
        st.markdown("---")
        st.markdown("### 📊 Stock Analysis")
        
        stock_data = st.session_state.stock_data
        stock_info = getattr(st.session_state, 'stock_info', {})
        
        if stock_info:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Company", stock_info.get('longName', 'N/A')[:20] + "...")
            with col2:
                st.metric("Price", f"${stock_info.get('regularMarketPrice', 0):.2f}")
            with col3:
                st.metric("Market Cap", f"${stock_info.get('marketCap', 0)/1e9:.1f}B")
            with col4:
                st.metric("P/E Ratio", f"{stock_info.get('trailingPE', 0):.2f}")
        
        st.dataframe(stock_data.tail(10), use_container_width=True)
        
        # Create stock charts
        if len(stock_data) > 0:
            charts = st.session_state.bot.create_financial_charts(stock_data)
            for chart in charts:
                st.plotly_chart(chart, use_container_width=True)

def data_analysis_tab():
    """Enhanced data analysis functionality with better UI"""
    
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">📁 File Upload Center</div>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose your financial files",
            type=['csv', 'xlsx', 'xls', 'pdf'],
            accept_multiple_files=True,
            help="📋 Supported formats: CSV, Excel (XLS/XLSX), PDF\n🔒 All files are processed locally for security"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) ready for processing")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Configuration section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">🔧 Analysis Configuration</div>', unsafe_allow_html=True)
        
        analysis_type = st.selectbox(
            "Select Analysis Focus",
            ["📊 Financial Performance", "📈 Stock Analysis", "⚠️ Risk Assessment", "🔍 Market Comparison"],
            help="Choose the type of analysis to perform on your data"
        )
        
        chart_style = st.selectbox(
            "Chart Style",
            ["Modern", "Classic", "Minimal"],
            help="Select your preferred visualization style"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Stock lookup section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">📊 Live Stock Data</div>', unsafe_allow_html=True)
        
        stock_symbol = st.text_input(
            "Stock Symbol", 
            placeholder="e.g., AAPL, MSFT, GOOGL",
            help="Enter any publicly traded stock symbol"
        )
        
        period = st.selectbox(
            "Time Period",
            ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=5,  # Default to 1y
            help="Select the time period for historical data"
        )
        
        if st.button("🚀 Fetch Stock Data", type="primary", use_container_width=True):
            if stock_symbol:
                with st.spinner("🔄 Fetching real-time data..."):
                    stock_data, stock_info = st.session_state.bot.get_stock_data(stock_symbol, period)
                    if stock_data is not None:
                        st.session_state.stock_data = stock_data
                        st.session_state.stock_info = stock_info
                        st.session_state.current_symbol = stock_symbol
                        st.success(f"✅ {stock_symbol} data loaded!")
                        st.rerun()
            else:
                st.warning("⚠️ Please enter a stock symbol")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area with enhanced layout
    if uploaded_files:
        st.markdown("### 📋 File Processing Center")
        
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files):
            progress = (idx + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing: {uploaded_file.name}")
            
            with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                # File info
                file_size = len(uploaded_file.getvalue()) / 1024  # KB
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <strong>📊 File Details:</strong><br>
                    📁 Size: {file_size:.1f} KB | 📋 Type: {file_extension.upper()} | 🕒 Processing: In Progress
                </div>
                """, unsafe_allow_html=True)
                
                if file_extension == 'csv':
                    data, message = st.session_state.bot.load_csv_file(uploaded_file)
                    if data is not None:
                        st.success(f"✅ {message}")
                        
                        # Enhanced data preview
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown("**� Data Preview:**")
                            st.dataframe(data.head(10), use_container_width=True)
                        
                        with col2:
                            st.markdown("**📈 Quick Stats:**")
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value">{len(data):,}</div>
                                <div class="metric-label">Total Rows</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{len(data.columns)}</div>
                                <div class="metric-label">Columns</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.session_state.current_data = data
                        st.session_state.session_stats['files_processed'] += 1
                        
                        # Add to RAG pipeline if available
                        if HAS_RAG:
                            uploaded_file.seek(0)
                            rag_message = st.session_state.rag_pipeline.add_document(
                                uploaded_file, uploaded_file.name, 'csv'
                            )
                            st.info(f"🧠 RAG: {rag_message}")
                        
                        # Enhanced charts
                        charts = st.session_state.bot.create_financial_charts(data)
                        if charts:
                            st.markdown("**📊 Visualizations:**")
                            for i, chart in enumerate(charts):
                                chart.update_layout(
                                    template="plotly_white",
                                    font_family="Arial",
                                    title_font_size=16,
                                    showlegend=True
                                )
                                st.plotly_chart(chart, use_container_width=True, key=f"chart_{idx}_{i}")
                    else:
                        st.error(f"❌ {message}")
                
                elif file_extension in ['xlsx', 'xls']:
                    data, message = st.session_state.bot.load_excel_file(uploaded_file)
                    if data is not None:
                        st.success(f"✅ {message}")
                        
                        # Similar enhanced display for Excel
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown("**📊 Data Preview:**")
                            st.dataframe(data.head(10), use_container_width=True)
                        
                        with col2:
                            st.markdown("**📈 Quick Stats:**")
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value">{len(data):,}</div>
                                <div class="metric-label">Total Rows</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{len(data.columns)}</div>
                                <div class="metric-label">Columns</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.session_state.current_data = data
                        st.session_state.session_stats['files_processed'] += 1
                        
                        if HAS_RAG:
                            uploaded_file.seek(0)
                            rag_message = st.session_state.rag_pipeline.add_document(
                                uploaded_file, uploaded_file.name, 'excel'
                            )
                            st.info(f"🧠 RAG: {rag_message}")
                        
                        charts = st.session_state.bot.create_financial_charts(data)
                        if charts:
                            st.markdown("**📊 Visualizations:**")
                            for i, chart in enumerate(charts):
                                chart.update_layout(template="plotly_white")
                                st.plotly_chart(chart, use_container_width=True, key=f"excel_chart_{idx}_{i}")
                    else:
                        st.error(f"❌ {message}")
                
                elif file_extension == 'pdf':
                    text, message = st.session_state.bot.load_pdf_file(uploaded_file)
                    if text is not None:
                        st.success(f"✅ {message}")
                        
                        # Enhanced PDF preview
                        word_count = len(text.split())
                        char_count = len(text)
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown("**📄 Document Preview:**")
                            preview_text = text[:2000] + "..." if len(text) > 2000 else text
                            st.text_area("Content", preview_text, height=200, key=f"pdf_{idx}")
                        
                        with col2:
                            st.markdown("**📊 Document Stats:**")
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value">{word_count:,}</div>
                                <div class="metric-label">Words</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{char_count:,}</div>
                                <div class="metric-label">Characters</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.session_state.pdf_content = text
                        st.session_state.session_stats['files_processed'] += 1
                        
                        if HAS_RAG:
                            uploaded_file.seek(0)
                            rag_message = st.session_state.rag_pipeline.add_document(
                                uploaded_file, uploaded_file.name, 'pdf'
                            )
                            st.info(f"🧠 RAG: {rag_message}")
                    else:
                        st.error(f"❌ {message}")
        
        progress_bar.progress(1.0)
        status_text.text("✅ All files processed successfully!")
    
    else:
        # Enhanced empty state
        st.markdown("""
        <div class="upload-area">
            <h3>📁 Ready to Start Your Analysis?</h3>
            <p>Upload your financial documents using the sidebar to begin</p>
            <p><strong>Supported formats:</strong> CSV, Excel (XLS/XLSX), PDF</p>
            <p><em>💡 Tip: You can upload multiple files at once!</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Stock data display and AI analysis section
    if hasattr(st.session_state, 'stock_data') and st.session_state.stock_data is not None:
        st.markdown("---")
        
        # Create two columns for stock data and AI analysis
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Get stock symbol from session state or use a default
            stock_symbol = getattr(st.session_state, 'current_stock_symbol', 'Stock')
            st.header(f"📈 Stock Data: {stock_symbol}")
            
            # Stock price chart
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=st.session_state.stock_data.index,
                open=st.session_state.stock_data['Open'],
                high=st.session_state.stock_data['High'],
                low=st.session_state.stock_data['Low'],
                close=st.session_state.stock_data['Close'],
                name=stock_symbol
            ))
            fig.update_layout(title=f"{stock_symbol} Stock Price", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            fig_volume = px.bar(
                x=st.session_state.stock_data.index,
                y=st.session_state.stock_data['Volume'],
                title=f"{stock_symbol} Trading Volume"
            )
            st.plotly_chart(fig_volume, use_container_width=True)
        
        with col2:
            st.header("🤖 AI Analysis")
        
        # Analysis prompt
        analysis_prompt = st.text_area(
            "What would you like to analyze?",
            placeholder="e.g., Analyze the financial performance, identify trends, assess investment potential...",
            height=100
        )
        
        if st.button("🚀 Analyze with AI", type="primary"):
            if analysis_prompt:
                context = ""
                
                # Prepare context from uploaded data
                if 'current_data' in st.session_state:
                    context += f"Data overview: {st.session_state.current_data.describe().to_string()}\n"
                
                if 'pdf_content' in st.session_state:
                    context += f"PDF content (excerpt): {st.session_state.pdf_content[:500]}...\n"
                
                if 'stock_data' in st.session_state:
                    latest_price = st.session_state.stock_data['Close'].iloc[-1]
                    price_change = st.session_state.stock_data['Close'].iloc[-1] - st.session_state.stock_data['Close'].iloc[-2]
                    context += f"Stock: {stock_symbol}, Latest Price: ${latest_price:.2f}, Change: ${price_change:.2f}\n"
                
                with st.spinner("Analyzing with AI..."):
                    analysis = st.session_state.bot.analyze_with_groq(analysis_prompt, context)
                    st.markdown("### 📊 Analysis Results")
                    st.markdown(analysis)
        
        # Quick analysis buttons
        st.header("⚡ Quick Analysis")
        
        if st.button("📈 Market Trends"):
            with st.spinner("Analyzing market trends..."):
                analysis = st.session_state.bot.analyze_with_groq(
                    "Analyze current market trends and provide investment insights",
                    "Focus on equity markets and growth opportunities"
                )
                st.markdown(analysis)
        
        if st.button("⚠️ Risk Assessment"):
            context = ""
            if 'current_data' in st.session_state:
                context = f"Data overview: {st.session_state.current_data.describe().to_string()}"
            
            with st.spinner("Assessing risks..."):
                analysis = st.session_state.bot.analyze_with_groq(
                    "Provide a comprehensive risk assessment for the given data",
                    context
                )
                st.markdown(analysis)
        
        if 'stock_info' in st.session_state:
            st.header("📋 Stock Information")
            info = st.session_state.stock_info
            
            # Display key metrics
            metrics_col1, metrics_col2 = st.columns(2)
            
            with metrics_col1:
                st.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else "N/A")
                st.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A")
            
            with metrics_col2:
                st.metric("52W High", f"${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if info.get('fiftyTwoWeekHigh') else "N/A")
                st.metric("52W Low", f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if info.get('fiftyTwoWeekLow') else "N/A")

def chatbot_tab():
    """Enhanced chatbot interface with agentic RAG capabilities"""
    st.markdown("## 🤖 AI Financial Assistant")
    
    # Display system capabilities
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Chat Interface")
        st.markdown("Ask sophisticated financial questions and get precise, data-driven answers!")
        
        # Display RAG database stats
        stats = st.session_state.rag_pipeline.get_collection_stats()
        if 'error' not in stats:
            st.info(f"📚 Knowledge Base: {stats['total_documents']} document chunks loaded")
    
    with col2:
        st.markdown("### 🧠 Agentic Capabilities")
        agentic_available = hasattr(st.session_state, 'agentic_rag') and st.session_state.agentic_rag is not None
        
        if agentic_available:
            st.success("✅ Agentic RAG: Active")
            st.markdown("""
            **Advanced Features:**
            - 🎯 Multi-step analysis planning
            - 🧮 Automatic calculations
            - 📈 Trend analysis
            - ⚠️ Risk assessment
            - 🔍 Entity comparison
            - 📊 Data synthesis
            """)
        else:
            st.warning("⚠️ Agentic RAG: Limited")
            st.markdown("Basic RAG functionality available")
    
    # Analysis mode selection
    st.markdown("### ⚙️ Analysis Mode")
    analysis_mode = st.radio(
        "Choose your analysis approach:",
        ["🤖 Agentic Analysis (Recommended)", "💬 Standard Chat", "🔍 Document Search"],
        help="Agentic Analysis provides multi-step reasoning and calculations"
    )
    
    # Chat interface
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant" and "metadata" in message:
                    # Enhanced display for agentic responses
                    metadata = message["metadata"]
                    
                    st.markdown(message["content"])
                    
                    # Show analysis details in expander
                    if "plan" in metadata and metadata["plan"]:
                        with st.expander("🔍 Analysis Plan & Details"):
                            st.markdown("**Analysis Steps:**")
                            for step in metadata["plan"]:
                                st.markdown(f"**Step {step['step']}**: {step['description']} ({step['tool']})")
                            
                            if "confidence" in metadata:
                                confidence = metadata["confidence"]
                                st.metric("Confidence Score", f"{confidence:.2%}")
                            
                            if "sources" in metadata and metadata["sources"]:
                                st.markdown("**Sources Used:**")
                                for source in metadata["sources"]:
                                    st.markdown(f"- 📄 {source}")
                else:
                    st.markdown(message["content"])
    
    # Chat input
    user_question = st.chat_input("Ask me anything about your financial data...")
    
    if user_question:
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": user_question})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_question)
        
        # Prepare context data
        context_data = {}
        if hasattr(st.session_state, 'current_data') and st.session_state.current_data is not None:
            context_data['uploaded_data'] = st.session_state.current_data
        
        if hasattr(st.session_state, 'stock_data') and st.session_state.stock_data is not None:
            context_data['stock_data'] = st.session_state.stock_data
            context_data['stock_info'] = getattr(st.session_state, 'stock_info', {})
        
        if hasattr(st.session_state, 'pdf_content'):
            context_data['pdf_content'] = st.session_state.pdf_content
        
        # Generate response based on selected mode
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your question..."):
                try:
                    if analysis_mode == "🤖 Agentic Analysis (Recommended)" and st.session_state.get('agentic_rag'):
                        # Use Agentic RAG
                        result = st.session_state.agentic_rag.process_query(user_question, context_data)
                        
                        if result['success']:
                            response = result['answer']
                            
                            # Add metadata for enhanced display
                            metadata = {
                                'plan': result.get('plan', []),
                                'confidence': result.get('confidence', 0.0),
                                'sources': result.get('sources', []),
                                'intermediate_results': result.get('intermediate_results', {})
                            }
                            
                            st.markdown(response)
                            
                            # Display confidence and sources
                            if metadata['confidence'] > 0:
                                conf_col1, conf_col2 = st.columns(2)
                                with conf_col1:
                                    st.metric("Analysis Confidence", f"{metadata['confidence']:.1%}")
                                with conf_col2:
                                    st.metric("Sources Used", len(metadata['sources']))
                            
                            # Add to chat history with metadata
                            st.session_state.chat_messages.append({
                                "role": "assistant", 
                                "content": response,
                                "metadata": metadata
                            })
                            
                        else:
                            error_response = result['answer']
                            st.error(error_response)
                            st.session_state.chat_messages.append({
                                "role": "assistant", 
                                "content": error_response
                            })
                    
                    elif analysis_mode == "🔍 Document Search":
                        # Use document search only
                        search_results = st.session_state.rag_pipeline.search_documents(user_question, n_results=5)
                        
                        if search_results and 'error' not in search_results[0]:
                            response = f"Found {len(search_results)} relevant results:\n\n"
                            
                            for i, result in enumerate(search_results[:3]):  # Show top 3
                                response += f"**Result {i+1}** (Relevance: {result['relevance_score']:.2f}):\n"
                                response += f"{result['content'][:300]}...\n\n"
                            
                            st.markdown(response)
                            st.session_state.chat_messages.append({"role": "assistant", "content": response})
                        else:
                            error_msg = "No relevant documents found for your query."
                            st.warning(error_msg)
                            st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                    
                    else:
                        # Standard chat mode
                        response = st.session_state.chatbot.get_response(user_question)
                        st.markdown(response)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
                
                except Exception as e:
                    error_response = f"I encountered an error while processing your question: {str(e)}"
                    st.error(error_response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_response})
    
    # Quick question buttons
    st.markdown("### ⚡ Quick Analysis Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Comprehensive Analysis"):
            question = "Provide a comprehensive financial analysis of all uploaded data including key metrics, trends, and investment insights"
            st.session_state.chat_messages.append({"role": "user", "content": question})
            st.rerun()
    
    with col2:
        if st.button("⚠️ Risk Assessment"):
            question = "Conduct a detailed risk assessment of the financial data and provide risk mitigation recommendations"
            st.session_state.chat_messages.append({"role": "user", "content": question})
            st.rerun()
    
    with col3:
        if st.button("📈 Performance Analysis"):
            question = "Analyze performance trends and calculate key financial ratios and growth metrics"
            st.session_state.chat_messages.append({"role": "user", "content": question})
            st.rerun()
    
    # Chat management
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Clear Chat History"):
            st.session_state.chat_messages = []
            if hasattr(st.session_state, 'chatbot'):
                st.session_state.chatbot.clear_conversation()
            st.rerun()
    
    with col2:
        if st.button("💾 Export Chat"):
            if st.session_state.chat_messages:
                chat_export = "\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.chat_messages])
                st.download_button(
                    "📥 Download Chat",
                    chat_export,
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    with col3:
        if st.button("📊 Chat Analytics"):
            if st.session_state.chat_messages:
                total_messages = len(st.session_state.chat_messages)
                user_messages = len([m for m in st.session_state.chat_messages if m['role'] == 'user'])
                assistant_messages = len([m for m in st.session_state.chat_messages if m['role'] == 'assistant'])
                
                st.info(f"📈 Chat Stats: {total_messages} total messages ({user_messages} questions, {assistant_messages} responses)")
    
    # Example queries for new users
    if not st.session_state.chat_messages:
        st.markdown("### 💡 Example Questions to Get Started")
        
        example_questions = [
            "Analyze the financial performance trends in my uploaded data",
            "What are the key risk factors for the companies in my portfolio?",
            "Calculate the growth rate and profitability metrics",
            "Compare the performance of different stocks or time periods",
            "Provide investment recommendations based on the data"
        ]
        
        for question in example_questions:
            if st.button(f"💬 {question}", key=f"example_{hash(question)}"):
                st.session_state.chat_messages.append({"role": "user", "content": question})
                st.rerun()

def rag_management_tab():
    """RAG pipeline management interface"""
    st.header("⚙️ RAG Knowledge Base Management")
    
    # Display current stats
    stats = st.session_state.rag_pipeline.get_collection_stats()
    if 'error' not in stats:
        st.metric("📚 Total Document Chunks", stats['total_documents'])
    else:
        st.error(stats['error'])
    
    # File upload for RAG
    st.subheader("📁 Add Documents to Knowledge Base")
    
    uploaded_files_rag = st.file_uploader(
        "Upload files for RAG knowledge base",
        type=['csv', 'xlsx', 'xls', 'pdf'],
        accept_multiple_files=True,
        key="rag_upload",
        help="These files will be added to the knowledge base for the chatbot"
    )
    
    if uploaded_files_rag:
        for uploaded_file in uploaded_files_rag:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            with st.spinner(f"Processing {uploaded_file.name}..."):
                message = st.session_state.rag_pipeline.add_document(
                    uploaded_file, uploaded_file.name, 
                    'excel' if file_extension in ['xlsx', 'xls'] else file_extension
                )
                st.success(message)
    
    # Search functionality
    st.subheader("🔍 Search Knowledge Base")
    
    # Enhanced search interface
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_query = st.text_input("Search for specific content in your documents:", 
                                   placeholder="e.g., financial ratios, stock analysis, market trends...")
    
    with search_col2:
        search_mode = st.selectbox("Display Mode", ["📊 Table View", "📄 Detailed View"], index=0)
    
    # Advanced search options
    with st.expander("🔧 Advanced Search Options"):
        col1, col2, col3 = st.columns(3)
        with col1:
            num_results = st.slider("Number of results", 1, 20, 5)
        with col2:
            min_relevance = st.slider("Minimum relevance score", 0.0, 1.0, 0.0, 0.1)
        with col3:
            content_type = st.selectbox("Content type filter", ["All", "CSV", "PDF", "Excel"])
    
    if search_query:
        with st.spinner("🔍 Searching knowledge base..."):
            results = st.session_state.rag_pipeline.search_documents(search_query, n_results=num_results)
            
            if results and 'error' not in results[0]:
                # Filter by relevance score and content type
                filtered_results = [
                    r for r in results 
                    if r['relevance_score'] >= min_relevance and 
                    (content_type == "All" or content_type.lower() in r['metadata'].get('source', '').lower())
                ]
                
                if filtered_results:
                    st.success(f"📊 Found {len(filtered_results)} relevant results (filtered from {len(results)} total)")
                    
                    if search_mode == "📊 Table View":
                        # Create a structured table view
                        import pandas as pd
                        
                        # Prepare data for table
                        table_data = []
                        for i, result in enumerate(filtered_results):
                            # Truncate content for table view
                            content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                            
                            table_data.append({
                                "Rank": i + 1,
                                "Relevance": f"{result['relevance_score']:.3f}",
                                "Source": result['metadata'].get('filename', 'Unknown'),
                                "Type": result['metadata'].get('source', 'Unknown').split('.')[-1].upper() if '.' in result['metadata'].get('source', '') else 'Unknown',
                                "Content Preview": content_preview,
                                "Full Content": result['content']  # Hidden column for details
                            })
                        
                        # Display as interactive table
                        df = pd.DataFrame(table_data)
                        display_df = df[["Rank", "Relevance", "Source", "Type", "Content Preview"]]
                        
                        # Style the dataframe
                        st.markdown("### 📋 Search Results Table")
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            height=400,
                            column_config={
                                "Rank": st.column_config.NumberColumn("🏆 Rank", width="small"),
                                "Relevance": st.column_config.TextColumn("📊 Score", width="small"),
                                "Source": st.column_config.TextColumn("📁 Source", width="medium"),
                                "Type": st.column_config.TextColumn("📄 Type", width="small"),
                                "Content Preview": st.column_config.TextColumn("📝 Preview", width="large")
                            }
                        )
                        
                        # Detailed view for selected results
                        st.markdown("### 🔍 Detailed Content Viewer")
                        selected_result = st.selectbox(
                            "Select a result to view full content:",
                            options=range(len(filtered_results)),
                            format_func=lambda x: f"Result {x+1}: {filtered_results[x]['metadata'].get('filename', 'Unknown')} (Score: {filtered_results[x]['relevance_score']:.3f})"
                        )
                        
                        if selected_result is not None:
                            result = filtered_results[selected_result]
                            
                            # Display detailed result in a nice format
                            with st.container():
                                st.markdown(f"""
                                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #007bff; margin: 1rem 0;">
                                    <h4 style="color: #007bff; margin-bottom: 0.5rem;">📄 {result['metadata'].get('filename', 'Unknown')}</h4>
                                    <p style="margin: 0.25rem 0;"><strong>Relevance Score:</strong> {result['relevance_score']:.3f}</p>
                                    <p style="margin: 0.25rem 0;"><strong>Content Type:</strong> {result['metadata'].get('source', 'Unknown').split('.')[-1].upper() if '.' in result['metadata'].get('source', '') else 'Unknown'}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Try to parse structured data if it's CSV-like
                                content = result['content']
                                if any(delimiter in content for delimiter in [',', '\t', '|']) and '\n' in content:
                                    st.markdown("**📊 Structured Data Preview:**")
                                    try:
                                        # Try to parse as CSV-like data
                                        lines = content.split('\n')
                                        if len(lines) > 1:
                                            # Detect delimiter
                                            delimiter = ',' if ',' in lines[0] else '\t' if '\t' in lines[0] else '|' if '|' in lines[0] else ','
                                            
                                            # Create a mini DataFrame
                                            import io
                                            try:
                                                df_preview = pd.read_csv(io.StringIO(content), delimiter=delimiter, nrows=10)
                                                st.dataframe(df_preview, use_container_width=True)
                                                st.caption(f"Showing first {min(len(df_preview), 10)} rows of structured data")
                                            except:
                                                # Fallback to text display
                                                st.text_area("Full Content", content, height=300, key=f"content_detail_{selected_result}")
                                        else:
                                            st.text_area("Full Content", content, height=300, key=f"content_detail_{selected_result}")
                                    except:
                                        st.text_area("Full Content", content, height=300, key=f"content_detail_{selected_result}")
                                else:
                                    st.markdown("**📝 Full Content:**")
                                    st.text_area("", content, height=300, key=f"content_detail_{selected_result}", label_visibility="collapsed")
                    
                    else:  # Detailed View mode
                        st.markdown("### 📄 Detailed Search Results")
                        
                        for i, result in enumerate(filtered_results):
                            with st.expander(
                                f"📋 Result {i+1} - {result['metadata'].get('filename', 'Unknown')} "
                                f"(Relevance: {result['relevance_score']:.3f})", 
                                expanded=(i == 0)  # Expand first result by default
                            ):
                                # Metadata section
                                meta_col1, meta_col2, meta_col3 = st.columns(3)
                                with meta_col1:
                                    st.metric("Relevance Score", f"{result['relevance_score']:.3f}")
                                with meta_col2:
                                    st.metric("Source File", result['metadata'].get('filename', 'Unknown'))
                                with meta_col3:
                                    file_type = result['metadata'].get('source', 'Unknown').split('.')[-1].upper() if '.' in result['metadata'].get('source', '') else 'Unknown'
                                    st.metric("File Type", file_type)
                                
                                st.markdown("---")
                                
                                # Content section
                                content = result['content']
                                
                                # Check if content looks like structured data
                                if any(delimiter in content for delimiter in [',', '\t', '|']) and '\n' in content and len(content.split('\n')) > 2:
                                    st.markdown("**📊 Structured Data:**")
                                    try:
                                        lines = content.split('\n')
                                        delimiter = ',' if ',' in lines[0] else '\t' if '\t' in lines[0] else '|' if '|' in lines[0] else ','
                                        
                                        import io
                                        df_preview = pd.read_csv(io.StringIO(content), delimiter=delimiter, nrows=15)
                                        st.dataframe(df_preview, use_container_width=True)
                                        
                                        if len(df_preview) >= 15:
                                            st.caption("Showing first 15 rows. Full content available below.")
                                        
                                        # Option to show raw content
                                        if st.checkbox(f"Show raw content for result {i+1}", key=f"raw_{i}"):
                                            st.text_area("Raw Content", content, height=200, key=f"raw_content_{i}")
                                    
                                    except Exception as e:
                                        st.markdown("**📝 Content:**")
                                        st.text_area("", content, height=200, key=f"content_{i}", label_visibility="collapsed")
                                        st.caption(f"Could not parse as structured data: {str(e)}")
                                else:
                                    st.markdown("**📝 Content:**")
                                    st.text_area("", content, height=200, key=f"content_{i}", label_visibility="collapsed")
                
                else:
                    st.warning(f"⚠️ No results found matching your criteria (relevance ≥ {min_relevance}, type: {content_type})")
                    if len(results) > 0:
                        st.info(f"💡 Try lowering the relevance threshold or changing the content type filter. Found {len(results)} results before filtering.")
            
            else:
                if results and 'error' in results[0]:
                    st.error(f"❌ Search error: {results[0]['error']}")
                else:
                    st.info("🔍 No results found for your query. Try different keywords or check if documents are properly loaded.")
    
    # Database management
    st.subheader("🛠️ Database Management")
    
    # Show current database contents
    with st.expander("📚 View Knowledge Base Contents", expanded=False):
        stats = st.session_state.rag_pipeline.get_collection_stats()
        if 'error' not in stats:
            st.success(f"📊 Knowledge Base contains {stats['total_documents']} document chunks")
            
            # Try to get a sample of documents to show what's in the database
            if st.button("📋 Show Document Inventory", key="show_inventory"):
                try:
                    # Get all documents with a broad search
                    sample_results = st.session_state.rag_pipeline.search_documents("", n_results=50)
                    
                    if sample_results and 'error' not in sample_results[0]:
                        # Create inventory table
                        inventory_data = []
                        file_stats = {}
                        
                        for i, result in enumerate(sample_results):
                            filename = result['metadata'].get('filename', 'Unknown')
                            source = result['metadata'].get('source', 'Unknown')
                            content_length = len(result['content'])
                            
                            # Count chunks per file
                            if filename not in file_stats:
                                file_stats[filename] = {'chunks': 0, 'total_chars': 0, 'type': source.split('.')[-1].upper() if '.' in source else 'Unknown'}
                            
                            file_stats[filename]['chunks'] += 1
                            file_stats[filename]['total_chars'] += content_length
                            
                            inventory_data.append({
                                "Chunk ID": i + 1,
                                "Filename": filename,
                                "File Type": source.split('.')[-1].upper() if '.' in source else 'Unknown',
                                "Content Length": content_length,
                                "Content Preview": result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                            })
                        
                        # File summary table
                        st.markdown("#### 📁 File Summary")
                        summary_data = []
                        for filename, stats_info in file_stats.items():
                            summary_data.append({
                                "Filename": filename,
                                "Type": stats_info['type'],
                                "Chunks": stats_info['chunks'],
                                "Total Characters": f"{stats_info['total_chars']:,}",
                                "Avg Chunk Size": f"{stats_info['total_chars'] // stats_info['chunks']:,}"
                            })
                        
                        summary_df = pd.DataFrame(summary_data)
                        st.dataframe(
                            summary_df,
                            use_container_width=True,
                            column_config={
                                "Filename": st.column_config.TextColumn("📁 File", width="large"),
                                "Type": st.column_config.TextColumn("📄 Type", width="small"),
                                "Chunks": st.column_config.NumberColumn("🧩 Chunks", width="small"),
                                "Total Characters": st.column_config.TextColumn("📊 Size", width="medium"),
                                "Avg Chunk Size": st.column_config.TextColumn("📏 Avg/Chunk", width="medium")
                            }
                        )
                        
                        # Detailed chunk inventory
                        st.markdown("#### 🧩 Detailed Chunk Inventory")
                        
                        # Filter options
                        col1, col2 = st.columns(2)
                        with col1:
                            selected_file = st.selectbox(
                                "Filter by file:",
                                ["All Files"] + list(file_stats.keys())
                            )
                        with col2:
                            show_content = st.checkbox("Show full content preview", value=False)
                        
                        # Filter data
                        filtered_inventory = inventory_data
                        if selected_file != "All Files":
                            filtered_inventory = [item for item in inventory_data if item["Filename"] == selected_file]
                        
                        if filtered_inventory:
                            inventory_df = pd.DataFrame(filtered_inventory)
                            
                            if not show_content:
                                # Show summary view
                                display_columns = ["Chunk ID", "Filename", "File Type", "Content Length", "Content Preview"]
                            else:
                                # Show detailed view with more content
                                display_columns = ["Chunk ID", "Filename", "File Type", "Content Length"]
                            
                            st.dataframe(
                                inventory_df[display_columns],
                                use_container_width=True,
                                height=400,
                                column_config={
                                    "Chunk ID": st.column_config.NumberColumn("🆔 ID", width="small"),
                                    "Filename": st.column_config.TextColumn("📁 File", width="medium"),
                                    "File Type": st.column_config.TextColumn("📄 Type", width="small"),
                                    "Content Length": st.column_config.NumberColumn("📏 Length", width="small"),
                                    "Content Preview": st.column_config.TextColumn("📝 Preview", width="large")
                                }
                            )
                            
                            if show_content:
                                st.markdown("#### 📝 Full Content Viewer")
                                selected_chunk = st.selectbox(
                                    "Select chunk to view full content:",
                                    options=range(len(filtered_inventory)),
                                    format_func=lambda x: f"Chunk {filtered_inventory[x]['Chunk ID']}: {filtered_inventory[x]['Filename']}"
                                )
                                
                                if selected_chunk is not None:
                                    chunk_data = filtered_inventory[selected_chunk]
                                    full_result = sample_results[chunk_data['Chunk ID'] - 1]
                                    
                                    st.markdown(f"""
                                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745;">
                                        <strong>📄 {chunk_data['Filename']} - Chunk {chunk_data['Chunk ID']}</strong><br>
                                        <em>Type: {chunk_data['File Type']} | Length: {chunk_data['Content Length']} characters</em>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Check if it's structured data
                                    content = full_result['content']
                                    if any(delimiter in content for delimiter in [',', '\t', '|']) and '\n' in content:
                                        try:
                                            lines = content.split('\n')
                                            delimiter = ',' if ',' in lines[0] else '\t' if '\t' in lines[0] else '|' if '|' in lines[0] else ','
                                            
                                            import io
                                            df_chunk = pd.read_csv(io.StringIO(content), delimiter=delimiter)
                                            st.markdown("**📊 Structured Data:**")
                                            st.dataframe(df_chunk, use_container_width=True)
                                        except:
                                            st.markdown("**📝 Raw Content:**")
                                            st.text_area("", content, height=300, key=f"chunk_content_{selected_chunk}", label_visibility="collapsed")
                                    else:
                                        st.markdown("**📝 Content:**")
                                        st.text_area("", content, height=300, key=f"chunk_content_{selected_chunk}", label_visibility="collapsed")
                        else:
                            st.info("No chunks found for the selected file.")
                    
                    else:
                        st.warning("No results found in the knowledge base.")
                
                except Exception as e:
                    st.error(f"Could not retrieve database contents: {str(e)}")
        else:
            st.error(f"Database error: {stats.get('error', 'Unknown error')}")
    
    # Management actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Knowledge Base", type="secondary"):
            if st.session_state.get('confirm_clear', False):
                message = st.session_state.rag_pipeline.clear_database()
                st.success(message)
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm clearing the knowledge base")
    
    with col2:
        if st.button("📊 Refresh Stats"):
            st.rerun()

def market_dashboard_tab():
    """Enhanced market dashboard with real-time data and insights"""
    st.markdown("## 📈 Market Dashboard")
    
    # Market overview section
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">📊</div>
            <div class="metric-label">Market Status</div>
            <div class="metric-sublabel">Live Trading</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">🔥</div>
            <div class="metric-label">Trending</div>
            <div class="metric-sublabel">Top Movers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">💹</div>
            <div class="metric-label">Volatility</div>
            <div class="metric-sublabel">Medium</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">📈</div>
            <div class="metric-label">Sentiment</div>
            <div class="metric-sublabel">Bullish</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Stock watchlist section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Stock Watchlist")
        
        # Popular stocks for demo
        popular_stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA']
        
        watchlist_container = st.container()
        
        with watchlist_container:
            for i, symbol in enumerate(popular_stocks):
                with st.expander(f"🔍 {symbol} - Click for details", expanded=False):
                    if st.button(f"📈 Load {symbol} Data", key=f"load_{symbol}"):
                        with st.spinner(f"Fetching {symbol} data..."):
                            stock_data, stock_info = st.session_state.bot.get_stock_data(symbol)
                            if stock_data is not None:
                                st.session_state.stock_data = stock_data
                                st.session_state.stock_info = stock_info
                                st.session_state.current_stock_symbol = symbol  # Store the symbol
                                st.success(f"✅ {symbol} data loaded successfully!")
                                st.session_state.session_stats['queries_made'] += 1
                                
                                # Quick stock info
                                if stock_info:
                                    st.markdown(f"""
                                    **Company:** {stock_info.get('longName', 'N/A')}  
                                    **Sector:** {stock_info.get('sector', 'N/A')}  
                                    **Market Cap:** ${stock_info.get('marketCap', 0):,.0f}
                                    """)
                                
                                # Mini chart
                                if len(stock_data) > 0:
                                    import plotly.graph_objects as go
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(
                                        x=stock_data.index,
                                        y=stock_data['Close'],
                                        mode='lines',
                                        name=f'{symbol} Close Price',
                                        line=dict(color='#1f77b4', width=2)
                                    ))
                                    fig.update_layout(
                                        title=f"{symbol} Price Trend (Last 30 Days)",
                                        height=300,
                                        template="plotly_white",
                                        showlegend=False,
                                        margin=dict(l=20, r=20, t=40, b=20)
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error(f"❌ Failed to load {symbol} data")
    
    with col2:
        st.markdown("### 🔧 Market Tools")
        
        # Custom stock lookup
        st.markdown("**📊 Custom Stock Lookup**")
        custom_symbol = st.text_input(
            "Enter Stock Symbol",
            placeholder="e.g., AAPL, GOOGL, TSLA",
            key="custom_stock_input"
        )
        
        if st.button("🔍 Analyze Stock", key="analyze_custom"):
            if custom_symbol:
                with st.spinner(f"Analyzing {custom_symbol.upper()}..."):
                    stock_data, stock_info = st.session_state.bot.get_stock_data(custom_symbol.upper())
                    if stock_data is not None:
                        st.session_state.stock_data = stock_data
                        st.session_state.stock_info = stock_info
                        st.session_state.current_stock_symbol = custom_symbol.upper()  # Store the symbol
                        st.success(f"✅ Analysis complete for {custom_symbol.upper()}!")
                        st.session_state.session_stats['queries_made'] += 1
                    else:
                        st.error(f"❌ Could not find data for {custom_symbol.upper()}")
            else:
                st.warning("⚠️ Please enter a stock symbol")
        
        st.markdown("---")
        
        # Market news section (placeholder)
        st.markdown("### 📰 Market News")
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #007bff;">
            <strong>📈 Market Update</strong><br>
            <small>Real-time news integration coming soon...</small><br><br>
            <em>Connect your preferred news API to get live market updates here.</em>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Refresh Dashboard", key="refresh_dashboard"):
            st.rerun()
        
        if st.button("📊 Export Analysis", key="export_analysis"):
            st.info("📁 Export functionality coming soon!")
        
        if st.button("📈 Generate Report", key="generate_report"):
            st.info("📄 Report generation coming soon!")
    
    # Current stock data display
    if hasattr(st.session_state, 'stock_data') and st.session_state.stock_data is not None:
        st.markdown("---")
        st.markdown("### 📊 Current Stock Analysis")
        
        stock_data = st.session_state.stock_data
        stock_info = getattr(st.session_state, 'stock_info', {})
        
        # Stock info cards
        if stock_info:
            info_col1, info_col2, info_col3, info_col4 = st.columns(4)
            
            with info_col1:
                current_price = stock_info.get('regularMarketPrice', 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">${current_price:.2f}</div>
                    <div class="metric-label">Current Price</div>
                </div>
                """, unsafe_allow_html=True)
            
            with info_col2:
                market_cap = stock_info.get('marketCap', 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">${market_cap/1e9:.1f}B</div>
                    <div class="metric-label">Market Cap</div>
                </div>
                """, unsafe_allow_html=True)
            
            with info_col3:
                pe_ratio = stock_info.get('trailingPE', 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{pe_ratio:.2f}</div>
                    <div class="metric-label">P/E Ratio</div>
                </div>
                """, unsafe_allow_html=True)
            
            with info_col4:
                volume = stock_info.get('regularMarketVolume', 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{volume/1e6:.1f}M</div>
                    <div class="metric-label">Volume</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Enhanced stock charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if len(stock_data) > 0:
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots
                
                # Price chart with volume
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.1,
                    subplot_titles=('Price Movement', 'Volume'),
                    row_width=[0.7, 0.3]
                )
                
                # Price line
                fig.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=stock_data['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='#1f77b4', width=2)
                ), row=1, col=1)
                
                # Volume bars
                fig.add_trace(go.Bar(
                    x=stock_data.index,
                    y=stock_data['Volume'],
                    name='Volume',
                    marker_color='rgba(31, 119, 180, 0.6)'
                ), row=2, col=1)
                
                fig.update_layout(
                    title="Stock Price & Volume Analysis",
                    height=500,
                    template="plotly_white",
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            # Moving averages chart
            if len(stock_data) > 20:
                stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
                stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
                
                fig_ma = go.Figure()
                fig_ma.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=stock_data['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='#1f77b4', width=2)
                ))
                fig_ma.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=stock_data['MA20'],
                    mode='lines',
                    name='20-day MA',
                    line=dict(color='#ff7f0e', width=1)
                ))
                if len(stock_data) > 50:
                    fig_ma.add_trace(go.Scatter(
                        x=stock_data.index,
                        y=stock_data['MA50'],
                        mode='lines',
                        name='50-day MA',
                        line=dict(color='#2ca02c', width=1)
                    ))
                
                fig_ma.update_layout(
                    title="Moving Averages Analysis",
                    height=500,
                    template="plotly_white",
                    showlegend=True
                )
                
                st.plotly_chart(fig_ma, use_container_width=True)

if __name__ == "__main__":
    main()
