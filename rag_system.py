import os
import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import pandas as pd
import PyPDF2
import io
from typing import List, Dict, Any
import hashlib

class RAGPipeline:
    def __init__(self, persist_directory="./chroma_db"):
        """Initialize RAG pipeline with ChromaDB vector store"""
        self.persist_directory = persist_directory
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("financial_docs")
        except:
            self.collection = self.client.create_collection(
                name="financial_docs",
                metadata={"hnsw:space": "cosine"}
            )
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    def extract_text_from_csv(self, csv_file) -> str:
        """Extract text representation from CSV file"""
        try:
            df = pd.read_csv(csv_file)
            # Create a text summary of the CSV
            text = f"Dataset with {len(df)} rows and {len(df.columns)} columns.\n"
            text += f"Columns: {', '.join(df.columns)}\n\n"
            text += f"Statistical Summary:\n{df.describe().to_string()}\n\n"
            
            # Add sample data
            text += f"Sample Data:\n{df.head(10).to_string()}\n\n"
            
            # Add insights about numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                text += "Numeric Analysis:\n"
                for col in numeric_cols:
                    text += f"- {col}: Mean={df[col].mean():.2f}, Std={df[col].std():.2f}\n"
            
            return text
        except Exception as e:
            return f"Error processing CSV: {str(e)}"
    
    def extract_text_from_excel(self, excel_file) -> str:
        """Extract text representation from Excel file"""
        try:
            df = pd.read_excel(excel_file)
            # Similar to CSV processing
            text = f"Excel dataset with {len(df)} rows and {len(df.columns)} columns.\n"
            text += f"Columns: {', '.join(df.columns)}\n\n"
            text += f"Statistical Summary:\n{df.describe().to_string()}\n\n"
            text += f"Sample Data:\n{df.head(10).to_string()}\n\n"
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                text += "Numeric Analysis:\n"
                for col in numeric_cols:
                    text += f"- {col}: Mean={df[col].mean():.2f}, Std={df[col].std():.2f}\n"
            
            return text
        except Exception as e:
            return f"Error processing Excel: {str(e)}"
    
    def add_document(self, file_content, filename: str, file_type: str):
        """Add a document to the vector store"""
        try:
            # Extract text based on file type
            if file_type == 'pdf':
                text = self.extract_text_from_pdf(file_content)
            elif file_type == 'csv':
                text = self.extract_text_from_csv(file_content)
            elif file_type == 'excel':
                text = self.extract_text_from_excel(file_content)
            else:
                text = str(file_content)
            
            # Split text into chunks
            documents = self.text_splitter.split_text(text)
            
            # Create embeddings and store in ChromaDB
            for i, chunk in enumerate(documents):
                # Create unique ID for each chunk
                chunk_id = hashlib.md5(f"{filename}_{i}_{chunk[:100]}".encode()).hexdigest()
                
                # Generate embedding
                embedding = self.embedding_model.encode(chunk).tolist()
                
                # Add to collection
                self.collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[{
                        "filename": filename,
                        "file_type": file_type,
                        "chunk_index": i,
                        "source": f"{filename} (chunk {i+1})"
                    }],
                    ids=[chunk_id]
                )
            
            return f"Successfully added {len(documents)} chunks from {filename}"
            
        except Exception as e:
            return f"Error adding document: {str(e)}"
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            search_results = []
            for i in range(len(results['documents'][0])):
                search_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'relevance_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                })
            
            return search_results
            
        except Exception as e:
            return [{"error": f"Search error: {str(e)}"}]
    
    def get_context_for_query(self, query: str, max_context_length: int = 3000) -> str:
        """Get relevant context for a query"""
        search_results = self.search_documents(query, n_results=5)
        
        context = ""
        current_length = 0
        
        for result in search_results:
            if 'error' in result:
                continue
                
            content = result['content']
            source = result['metadata'].get('source', 'Unknown')
            
            # Add content if it fits within the limit
            addition = f"\n[Source: {source}]\n{content}\n"
            if current_length + len(addition) <= max_context_length:
                context += addition
                current_length += len(addition)
            else:
                break
        
        return context if context else "No relevant context found."
    
    def clear_database(self):
        """Clear all documents from the database"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection("financial_docs")
            self.collection = self.client.create_collection(
                name="financial_docs",
                metadata={"hnsw:space": "cosine"}
            )
            return "Database cleared successfully"
        except Exception as e:
            return f"Error clearing database: {str(e)}"
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the document collection"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": "financial_docs"
            }
        except Exception as e:
            return {"error": f"Error getting stats: {str(e)}"}

class ChatBot:
    def __init__(self, rag_pipeline: RAGPipeline, groq_client):
        self.rag_pipeline = rag_pipeline
        self.groq_client = groq_client
        self.conversation_history = []
    
    def get_response(self, query: str, use_rag: bool = True) -> str:
        """Get response from chatbot with optional RAG context"""
        try:
            if use_rag:
                # Get relevant context from RAG pipeline
                context = self.rag_pipeline.get_context_for_query(query)
                
                prompt = f"""
                You are an expert financial analyst assistant. Use the provided context to answer the user's question accurately and comprehensively.
                
                Context from uploaded documents:
                {context}
                
                Conversation History:
                {self._format_conversation_history()}
                
                User Question: {query}
                
                Instructions:
                1. Answer based on the provided context when relevant
                2. If the context doesn't contain relevant information, use your general financial knowledge
                3. Always cite sources when using information from the context
                4. Be concise but thorough
                5. If you're unsure, say so rather than making up information
                
                Answer:
                """
            else:
                prompt = f"""
                You are an expert financial analyst assistant. Answer the user's question based on your financial knowledge.
                
                Conversation History:
                {self._format_conversation_history()}
                
                User Question: {query}
                
                Answer:
                """
            
            # Get response from GROQ
            completion = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",  # Updated to supported model
                messages=[
                    {"role": "system", "content": "You are an expert financial analyst with deep knowledge of markets, investments, and financial analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            response = completion.choices[0].message.content
            
            # Add to conversation history
            self.conversation_history.append({
                "query": query,
                "response": response,
                "used_rag": use_rag
            })
            
            # Keep only last 5 conversations to manage context length
            if len(self.conversation_history) > 5:
                self.conversation_history = self.conversation_history[-5:]
            
            return response
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _format_conversation_history(self) -> str:
        """Format conversation history for context"""
        if not self.conversation_history:
            return "No previous conversation."
        
        history = ""
        for conv in self.conversation_history[-3:]:  # Last 3 conversations
            history += f"Q: {conv['query']}\nA: {conv['response'][:200]}...\n\n"
        
        return history
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        return "Conversation history cleared."
