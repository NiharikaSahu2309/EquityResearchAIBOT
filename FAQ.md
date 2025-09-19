# Equity Research Assistant Bot - Frequently Asked Questions

## General Questions

### What is the Equity Research Assistant Bot?
The Equity Research Assistant Bot is an AI-powered financial analysis tool that combines document processing, real-time stock data, and advanced AI to provide comprehensive equity research insights. It uses RAG (Retrieval-Augmented Generation) to answer questions based on your uploaded financial documents.

### What types of files can I upload?
You can upload:
- CSV files with financial data
- Excel files (XLS/XLSX) containing spreadsheets
- PDF files with financial reports, research papers, or documentation
- Any combination of these file types

### How does the RAG system work?
The RAG (Retrieval-Augmented Generation) system:
1. Processes your uploaded documents
2. Splits them into searchable chunks
3. Creates vector embeddings for semantic search
4. Retrieves relevant context when you ask questions
5. Combines retrieved information with AI knowledge to provide accurate answers

## Technical Questions

### What AI model does the system use?
The system uses GROQ's Mixtral-8x7B-32768 model for generating responses, combined with Sentence Transformers for creating document embeddings for the RAG pipeline.

### How is my data stored?
- Document embeddings are stored locally in a ChromaDB vector database
- Your original files are processed but not permanently stored
- All data remains on your local machine
- API calls to GROQ only send processed queries, not your raw data

### Can I clear the knowledge base?
Yes, you can clear the entire knowledge base from the RAG Management tab. This will remove all processed documents but won't affect your original files.

## Financial Analysis Questions

### What kind of financial analysis can the bot perform?
The bot can:
- Analyze financial statements and ratios
- Provide market trend analysis
- Assess investment risks
- Generate investment recommendations
- Compare different financial instruments
- Explain complex financial concepts

### Can it analyze real-time stock data?
Yes, the bot integrates with Yahoo Finance to fetch real-time stock prices, historical data, and company fundamentals for any publicly traded stock.

### What visualizations are available?
The system creates:
- Interactive price charts (candlestick, line charts)
- Volume analysis charts
- Correlation heatmaps
- Distribution plots
- Time series visualizations

## Usage Tips

### How do I get the best results from the chatbot?
1. Upload relevant financial documents first
2. Ask specific questions about your data
3. Use the quick question buttons for common analyses
4. Refer to specific companies, metrics, or time periods in your questions

### What should I do if the bot doesn't understand my question?
1. Try rephrasing your question more specifically
2. Break complex questions into smaller parts
3. Ensure you've uploaded relevant documents
4. Use financial terminology the bot recognizes

### Can I ask follow-up questions?
Yes, the chatbot maintains conversation history and can handle follow-up questions and context from previous interactions.

## Troubleshooting

### What if my file upload fails?
- Check that your file is in a supported format (CSV, Excel, PDF)
- Ensure the file isn't corrupted
- Try uploading one file at a time
- Check the file size (very large files may take longer to process)

### Why are some features not working?
- Ensure all required packages are installed
- Check that your GROQ API key is properly configured in the .env file
- Restart the application if you encounter persistent issues

### How do I update the system?
- Pull the latest code from the repository
- Install any new requirements: `pip install -r requirements.txt`
- Restart the Streamlit application

## Privacy and Security

### Is my financial data secure?
- All processing happens locally on your machine
- Documents are processed into embeddings, not stored as raw text
- API calls only send processed queries, not your sensitive data
- You can clear the knowledge base at any time

### What information is sent to external services?
- Only processed queries and analysis requests are sent to GROQ
- Stock symbols are sent to Yahoo Finance for market data
- No personal financial documents or sensitive data leaves your machine

## Advanced Features

### Can I integrate custom data sources?
The system is designed to be extensible. You can modify the RAG pipeline to accept additional data sources or formats.

### How accurate are the AI responses?
The AI provides responses based on:
- Your uploaded documents (highest priority)
- General financial knowledge
- Real-time market data
Always verify important financial decisions with additional research and professional advice.

### Can I export analysis results?
Currently, you can copy responses from the chat interface. Future versions may include export functionality for reports and analysis results.
