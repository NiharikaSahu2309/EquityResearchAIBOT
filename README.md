# ResearchGPT - AI-Powered Equity Research Assistant

An advanced financial research assistant powered by Agentic RAG (Retrieval-Augmented Generation) that helps analyze financial documents, earnings transcripts, and market data with intelligent document understanding and multi-step reasoning.

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
git clone https://github.com/kunal-s/app-researchgpt.git
cd app-researchgpt
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
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## 🚀 Running the Application

### Option 1: Manual Start
```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Terminal 2: Start Frontend
cd frontend
npm start
```

### Option 2: Using Scripts
```bash
# Windows
start_app.bat

# macOS/Linux
./start.sh
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
- "What was Suzlon's revenue growth in Q1 FY26?"
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
app-researchgpt/
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
1. Check the [Issues](https://github.com/kunal-s/app-researchgpt/issues) page
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

## 🔄 Recent Updates

- ✅ Enhanced search algorithm with financial synonyms
- ✅ Improved prompt engineering for summarized responses
- ✅ Multi-criteria relevance scoring
- ✅ Agentic reasoning with step-by-step analysis
- ✅ Better context extraction and citation
- ✅ Increased context window for comprehensive analysis

---

**Built with ❤️ for financial research and analysis**
   - Ask questions about your uploaded documents
   - Use quick question buttons for common analyses
   - Maintain conversation history for follow-up questions

4. **Manage Knowledge Base**:
   - Use the RAG Management tab to add more documents
   - Search through your document collection
   - Clear the knowledge base when needed

5. **Stock Research**:
   - Enter a stock symbol (e.g., AAPL, MSFT, GOOGL) in any tab
   - Get real-time stock data and analysis

## File Support

### CSV Files
- Automatic data type detection
- Statistical summaries
- Interactive charts and visualizations

### Excel Files (XLS/XLSX)
- Full spreadsheet support
- Multiple sheet handling
- Data preprocessing and cleaning

### PDF Files
- Text extraction and analysis
- Financial report processing
- Document summarization

## AI Analysis Capabilities

- **Document-Based Q&A**: Ask questions about uploaded financial reports, data, and documents
- **Financial Performance Analysis**: Comprehensive analysis of financial metrics and ratios
- **Market Trend Identification**: Identify and analyze market patterns and trends
- **Risk Assessment and Management**: Evaluate investment risks and mitigation strategies
- **Investment Recommendations**: AI-powered investment suggestions based on data
- **Comparative Analysis**: Compare different stocks, sectors, or time periods
- **Technical Indicator Analysis**: Analysis of technical trading indicators
- **Conversation Memory**: Maintain context across multiple questions
- **Real-time Data Integration**: Combine uploaded documents with live market data

## Sample Data

The `Stock data/` folder contains sample datasets:
- `indexData.csv`: Market index data
- `indexInfo.csv`: Index information
- `indexProcessed.csv`: Processed index data

## API Integration

### GROQ API
- Model: Llama3-8B-8192 (updated from deprecated Mixtral)
- Specialized financial analysis prompts
- Context-aware responses with RAG integration
- Conversation memory and follow-up handling

### RAG Pipeline
- Vector database: ChromaDB (local storage)
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
- Document chunking and semantic search
- Privacy-first: all processing happens locally

### Yahoo Finance API
- Real-time stock prices
- Historical data
- Company fundamentals

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
