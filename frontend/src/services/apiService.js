import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Increased to 60 seconds for general requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create a separate client for long operations (file uploads, agentic RAG)
const longOperationClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for heavy operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

const apiService = {
  // Health check
  async getHealth() {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // File upload endpoints
  async uploadCSV(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await longOperationClient.post('/upload/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async uploadExcel(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await longOperationClient.post('/upload/excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async uploadPDF(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await longOperationClient.post('/upload/pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Stock analysis
  async fetchStockData(symbol) {
    const response = await apiClient.post('/stock/fetch', { symbol });
    return response.data;
  },

  // Chat functionality
  async sendChatMessage(message, mode = 'agentic', contextData = null) {
    // Use long operation client for agentic mode, regular client for others
    const client = mode === 'agentic' ? longOperationClient : apiClient;
    
    const response = await client.post('/chat', {
      message,
      mode,
      context_data: contextData,
    });
    return response.data;
  },

  // RAG operations
  async getRAGStats() {
    const response = await apiClient.get('/rag/stats');
    return response.data;
  },

  async searchDocuments(query, nResults = 10) {
    const response = await apiClient.post(`/rag/search?query=${encodeURIComponent(query)}&n_results=${nResults}`);
    return response.data;
  },

  async clearRAGDatabase() {
    const response = await apiClient.delete('/rag/clear');
    return response.data;
  },

  // Market data
  async getMarketOverview() {
    const response = await apiClient.get('/analysis/market-overview');
    return response.data;
  },

  // Helper method to handle file uploads based on file type
  async uploadFile(file) {
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    switch (fileExtension) {
      case 'csv':
        return await this.uploadCSV(file);
      case 'xlsx':
      case 'xls':
        return await this.uploadExcel(file);
      case 'pdf':
        return await this.uploadPDF(file);
      default:
        throw new Error(`Unsupported file type: ${fileExtension}`);
    }
  },
};

export default apiService;
