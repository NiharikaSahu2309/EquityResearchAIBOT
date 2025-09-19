import os
import json
import hashlib
from typing import List, Dict, Any
import pandas as pd
import PyPDF2
import io
from groq import Groq

class SimpleRAGPipeline:
    def __init__(self, persist_directory="./simple_rag_db"):
        """Initialize simple RAG pipeline with file-based storage"""
        self.persist_directory = persist_directory
        self.documents = {}  # In-memory document store
        self.document_file = os.path.join(persist_directory, "documents.json")
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Load existing documents
        self.load_documents()
    
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
            numeric_cols = df.select_dtypes(include=['number']).columns
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
            
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                text += "Numeric Analysis:\n"
                for col in numeric_cols:
                    text += f"- {col}: Mean={df[col].mean():.2f}, Std={df[col].std():.2f}\n"
            
            return text
        except Exception as e:
            return f"Error processing Excel: {str(e)}"
    
    def add_document(self, file_content, filename: str, file_type: str):
        """Add a document to the simple storage"""
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
            
            # Split text into chunks (simple approach)
            chunks = self.split_text(text, chunk_size=1000)
            
            # Store document
            doc_id = hashlib.md5(filename.encode()).hexdigest()
            self.documents[doc_id] = {
                'filename': filename,
                'file_type': file_type,
                'chunks': chunks,
                'full_text': text
            }
            
            # Save to file
            self.save_documents()
            
            return f"Successfully added {len(chunks)} chunks from {filename}"
            
        except Exception as e:
            return f"Error adding document: {str(e)}"
    
    def split_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Simple text splitting"""
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= chunk_size:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict]:
        """Simple keyword-based search"""
        try:
            query_words = set(query.lower().split())
            results = []
            
            for doc_id, doc in self.documents.items():
                for i, chunk in enumerate(doc['chunks']):
                    chunk_words = set(chunk.lower().split())
                    
                    # Simple relevance scoring based on word overlap
                    overlap = len(query_words.intersection(chunk_words))
                    if overlap > 0:
                        relevance_score = overlap / len(query_words)
                        results.append({
                            'content': chunk,
                            'metadata': {
                                'filename': doc['filename'],
                                'file_type': doc['file_type'],
                                'chunk_index': i,
                                'source': f"{doc['filename']} (chunk {i+1})"
                            },
                            'relevance_score': relevance_score
                        })
            
            # Sort by relevance score
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return results[:n_results]
            
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
        """Clear all documents"""
        try:
            self.documents = {}
            self.save_documents()
            return "Database cleared successfully"
        except Exception as e:
            return f"Error clearing database: {str(e)}"
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the document collection"""
        try:
            total_chunks = sum(len(doc['chunks']) for doc in self.documents.values())
            return {
                "total_documents": total_chunks,
                "total_files": len(self.documents),
                "collection_name": "simple_rag_docs"
            }
        except Exception as e:
            return {"error": f"Error getting stats: {str(e)}"}
    
    def save_documents(self):
        """Save documents to file"""
        try:
            with open(self.document_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving documents: {e}")
    
    def load_documents(self):
        """Load documents from file"""
        try:
            if os.path.exists(self.document_file):
                with open(self.document_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
        except Exception as e:
            print(f"Error loading documents: {e}")
            self.documents = {}

class SimpleChatBot:
    def __init__(self, rag_pipeline: SimpleRAGPipeline, groq_client):
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

# Alias the classes for compatibility
RAGPipeline = SimpleRAGPipeline
ChatBot = SimpleChatBot
