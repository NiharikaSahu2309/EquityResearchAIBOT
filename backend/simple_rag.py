import os
import json
import hashlib
from typing import List, Dict, Any
import pandas as pd
import PyPDF2
import io
from groq import Groq
from datetime import datetime

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
        """Enhanced search with better relevance scoring and query expansion"""
        try:
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            # Financial keywords and synonyms for query expansion
            financial_synonyms = {
                'revenue': ['sales', 'income', 'turnover', 'receipts'],
                'profit': ['earnings', 'income', 'margin', 'pbt', 'pat'],
                'loss': ['deficit', 'negative', 'decline'],
                'growth': ['increase', 'expansion', 'rise', 'improvement'],
                'decline': ['decrease', 'fall', 'drop', 'reduction'],
                'ratio': ['metric', 'indicator', 'measure'],
                'debt': ['borrowing', 'liability', 'loan'],
                'equity': ['shares', 'stock', 'ownership'],
                'dividend': ['payout', 'distribution'],
                'cash': ['liquid', 'money', 'funds'],
                'investment': ['capex', 'expenditure', 'spending'],
                'market': ['trading', 'exchange', 'sector'],
                'performance': ['results', 'outcome', 'achievement'],
                'analysis': ['evaluation', 'assessment', 'review'],
                'financial': ['monetary', 'fiscal', 'economic'],
                'quarter': ['q1', 'q2', 'q3', 'q4', 'quarterly'],
                'year': ['annual', 'yearly', 'fy'],
                'percentage': ['percent', '%', 'rate'],
                'million': ['mn', 'crore', 'cr'],
                'billion': ['bn', 'thousand crore']
            }
            
            # Expand query with synonyms
            expanded_words = set(query_words)
            for word in query_words:
                if word in financial_synonyms:
                    expanded_words.update(financial_synonyms[word])
                # Also check if word is a synonym of any key
                for key, synonyms in financial_synonyms.items():
                    if word in synonyms:
                        expanded_words.add(key)
                        expanded_words.update(synonyms)
            
            results = []
            
            for doc_id, doc in self.documents.items():
                for i, chunk in enumerate(doc['chunks']):
                    chunk_lower = chunk.lower()
                    chunk_words = set(chunk_lower.split())
                    
                    # Multiple scoring criteria
                    scores = {}
                    
                    # 1. Exact word match score
                    exact_matches = len(query_words.intersection(chunk_words))
                    scores['exact'] = exact_matches / len(query_words) if query_words else 0
                    
                    # 2. Expanded word match score (synonyms)
                    expanded_matches = len(expanded_words.intersection(chunk_words))
                    scores['expanded'] = expanded_matches / len(expanded_words) if expanded_words else 0
                    
                    # 3. Partial word match score (contains)
                    partial_matches = 0
                    for q_word in query_words:
                        if len(q_word) > 3:  # Only for words longer than 3 chars
                            for c_word in chunk_words:
                                if q_word in c_word or c_word in q_word:
                                    partial_matches += 0.5
                    scores['partial'] = partial_matches / len(query_words) if query_words else 0
                    
                    # 4. Phrase matching score
                    phrase_score = 0
                    if len(query_words) > 1:
                        # Check for consecutive word sequences
                        query_phrases = []
                        query_list = query_lower.split()
                        for j in range(len(query_list) - 1):
                            query_phrases.append(' '.join(query_list[j:j+2]))
                        
                        for phrase in query_phrases:
                            if phrase in chunk_lower:
                                phrase_score += 1
                        scores['phrase'] = phrase_score / len(query_phrases) if query_phrases else 0
                    
                    # 5. Numerical value matching (for financial data)
                    numerical_score = 0
                    import re
                    query_numbers = re.findall(r'\d+\.?\d*', query)
                    chunk_numbers = re.findall(r'\d+\.?\d*', chunk)
                    if query_numbers and chunk_numbers:
                        for q_num in query_numbers:
                            if q_num in chunk_numbers:
                                numerical_score += 1
                    scores['numerical'] = numerical_score / len(query_numbers) if query_numbers else 0
                    
                    # Weighted final score
                    final_score = (
                        scores['exact'] * 0.4 +         # Exact matches most important
                        scores['expanded'] * 0.25 +     # Synonym matches
                        scores['partial'] * 0.15 +      # Partial matches
                        scores['phrase'] * 0.15 +       # Phrase matching
                        scores['numerical'] * 0.05      # Number matching
                    )
                    
                    # Only include results with meaningful relevance
                    if final_score > 0.1:  # Lowered threshold for more results
                        results.append({
                            'content': chunk,
                            'metadata': {
                                'filename': doc['filename'],
                                'file_type': doc['file_type'],
                                'chunk_index': i,
                                'source': f"{doc['filename']} (chunk {i+1})"
                            },
                            'relevance_score': final_score,
                            'score_breakdown': scores
                        })
            
            # Sort by relevance score
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return results[:n_results]
            
        except Exception as e:
            return [{"error": f"Search error: {str(e)}"}]
    
    def get_context_for_query(self, query: str, max_context_length: int = 8000) -> str:
        """Get relevant context for a query with enhanced search"""
        search_results = self.search_documents(query, n_results=8)  # Get more results
        
        context = ""
        current_length = 0
        
        for result in search_results:
            if 'error' in result:
                continue
                
            content = result['content']
            source = result['metadata'].get('source', 'Unknown')
            relevance = result.get('relevance_score', 0)
            
            # Add content if it fits within the limit
            addition = f"\n[Source: {source} | Relevance: {relevance:.2f}]\n{content}\n"
            if current_length + len(addition) <= max_context_length:
                context += addition
                current_length += len(addition)
            else:
                # Try to fit partial content if space allows
                remaining_space = max_context_length - current_length - 200  # Leave some buffer
                if remaining_space > 500:  # Only if meaningful space left
                    truncated_content = content[:remaining_space] + "..."
                    addition = f"\n[Source: {source} | Relevance: {relevance:.2f}]\n{truncated_content}\n"
                    context += addition
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
                You are an expert financial analyst assistant. Provide a CONCISE, SUMMARIZED answer using ONLY the most relevant information from the provided context.
                
                Context from uploaded documents:
                {context}
                
                Conversation History:
                {self._format_conversation_history()}
                
                User Question: {query}
                
                CRITICAL INSTRUCTIONS:
                1. Focus ONLY on the most relevant information from the provided context
                2. Provide a SUMMARIZED answer (3-5 sentences maximum)
                3. ALWAYS cite the specific source file when using context information
                4. If context contains relevant data, prioritize it over general knowledge
                5. Use bullet points for key metrics or data points
                6. If no relevant context is found, clearly state this and provide brief general guidance
                7. Highlight the most important insights first
                
                Format your response as:
                **Key Finding:** [Main insight from context]
                **Source:** [Filename from context]
                **Summary:** [2-3 sentence summary]
                
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
                model="llama-3.1-8b-instant",  # Updated to currently supported model
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
