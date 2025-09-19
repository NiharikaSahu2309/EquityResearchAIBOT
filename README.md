# EquityResearchAIBOT - AI-Powered Financial Analysis Assistant

An advanced equity research assistant powered by Agentic RAG (Retrieval-Augmented Generation) that helps analyze financial documents, earnings transcripts, and market data with intelligent document understanding and multi-step reasoning.

## 🚀 Features

### **Agentic RAG System**
- **Multi-step Analysis**: Intelligent planning and execution of complex financial queries
- **Enhanced Search**: Advanced semantic search with financial keyword expansion
- **Document Intelligence**: PDF, CSV, and Excel file processing with context extraction
- **Structured Responses**: Summarized, citation-backed answers from uploaded documents

### **Multiple Chat Modes**
- **Agentic Mode**: Advanced reasoning with step-by-step analysis
- **Standard Mode**: Direct Q&A with document context
- **Search Mode**: Document search and retrieval

### **Financial Analysis Tools**
- **Stock Data Integration**: Real-time market data via yfinance
- **Interactive Visualizations**: Plotly-powered charts and graphs
- **Risk Assessment**: Automated financial risk analysis
- **Trend Analysis**: Time-series analysis and pattern recognition

## 🏗️ Architecture

### **Backend (FastAPI)**
- **FastAPI** high-performance API server
- **GROQ** LLM integration with `llama-3.1-8b-instant`
- **Enhanced RAG Pipeline** with multi-criteria relevance scoring
- **ChromaDB** and Simple RAG for document storage
- **Financial synonym expansion** for better search accuracy

### **Frontend (React)**
- **Material-UI** modern interface
- **Real-time chat** with multiple AI modes
- **File upload** support for documents
- **Interactive charts** and data visualization

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **GROQ API Key** (get from [groq.com](https://groq.com))

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/NiharikaSahu2309/EquityResearchAIBOT.git
cd EquityResearchAIBOT
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Environment Configuration
Create a `.env` file in the backend directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## 🚀 Running the Application

### Manual Start
```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Terminal 2: Start Frontend
cd frontend
npm start
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

## 📊 Usage

### 1. **Upload Documents**
- Drag and drop PDF, CSV, or Excel files
- System automatically extracts and indexes content
- Files are processed for semantic search

### 2. **Choose Chat Mode**
- **Agentic**: For complex analysis requiring multi-step reasoning
- **Standard**: For direct questions with document context
- **Search**: For finding specific information in documents

### 3. **Ask Questions**
Example queries:
- "What was the company's revenue growth in Q1?"
- "Analyze the key risks mentioned in the earnings call"
- "Compare the financial performance metrics"

### 4. **Get Structured Responses**
The AI provides:
- **Key Findings**: Main insights from your documents
- **Supporting Data**: Relevant metrics and numbers
- **Sources**: Citation of specific documents
- **Summary**: Concise conclusion

## 🔧 Key Components

### **Enhanced Search Algorithm**
- Multi-criteria relevance scoring
- Financial keyword synonym expansion
- Phrase and numerical matching
- Context window optimization (8K characters)

### **Agentic RAG Features**
- Step-by-step analysis planning
- Tool orchestration (search, calculate, analyze)
- Intelligent result synthesis
- Confidence scoring

### **Document Processing**
- PDF text extraction
- CSV/Excel statistical analysis
- Chunk-based storage with metadata
- Relevance-based retrieval

## 📁 Project Structure

```
EquityResearchAIBOT/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── simple_rag.py        # Enhanced RAG pipeline
│   ├── agentic_rag.py       # Agentic reasoning system
│   ├── rag_system.py        # ChromaDB integration
│   ├── utils.py             # Utility functions
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/                 # React source code
│   ├── public/              # Static assets
│   └── package.json         # Node.js dependencies
├── Stock data/              # Sample datasets
│   ├── indexData.csv
│   ├── indexInfo.csv
│   └── indexProcessed.csv
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

## 🎯 API Endpoints

- `POST /upload` - Upload and process documents
- `POST /chat` - Chat with AI (all modes)
- `GET /stats` - Get database statistics
- `POST /stock-analysis` - Analyze stock data
- `DELETE /clear-database` - Clear document database

## 🔒 Environment Variables

```env
GROQ_API_KEY=your_groq_api_key
PORT=8080
NODE_ENV=development
```

## 📊 Sample Data

The `Stock data/` folder contains sample datasets:
- `indexData.csv`: Market index data with historical prices
- `indexInfo.csv`: Index information and metadata
- `indexProcessed.csv`: Processed index data for analysis

## 🤖 AI Capabilities

### Document Analysis
- **Financial Reports**: Automatic extraction and analysis of financial statements
- **Earnings Transcripts**: Processing of earnings call transcripts
- **Market Research**: Analysis of research reports and market data

### Multi-Modal Analysis
- **Text Analysis**: NLP-powered document understanding
- **Numerical Analysis**: Statistical analysis of financial data
- **Time Series**: Trend analysis and forecasting

### Intelligent Responses
- **Summarized Answers**: Concise, structured responses
- **Source Attribution**: Clear citation of information sources
- **Context Awareness**: Maintains conversation context for follow-up questions

## 🔄 Recent Updates

- ✅ Enhanced search algorithm with financial synonyms
- ✅ Improved prompt engineering for summarized responses
- ✅ Multi-criteria relevance scoring
- ✅ Agentic reasoning with step-by-step analysis
- ✅ Better context extraction and citation
- ✅ Increased context window for comprehensive analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the [Issues](https://github.com/NiharikaSahu2309/EquityResearchAIBOT/issues) page
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

---

**Built with ❤️ for financial research and analysis by Niharika Sahu**
