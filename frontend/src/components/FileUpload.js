import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { ExpandMore, CloudUpload, CheckCircle, Error } from '@mui/icons-material';
import Plot from 'react-plotly.js';
import toast from 'react-hot-toast';

import apiService from '../services/apiService';

const FileUpload = () => {
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, success, error
  const [uploadResult, setUploadResult] = useState(null);
  const [charts, setCharts] = useState([]);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploadStatus('uploading');
    
    try {
      const result = await apiService.uploadFile(file);
      
      if (result.success) {
        setUploadResult(result);
        setUploadStatus('success');
        
        // Process charts if available
        if (result.charts && result.charts.length > 0) {
          const parsedCharts = result.charts.map(chartJson => {
            try {
              return JSON.parse(chartJson);
            } catch (e) {
              console.error('Failed to parse chart:', e);
              return null;
            }
          }).filter(Boolean);
          setCharts(parsedCharts);
        }
        
        toast.success(`File uploaded successfully: ${file.name}`);
      } else {
        throw new Error(result.message || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('error');
      setUploadResult({ error: error.message });
      toast.error(`Upload failed: ${error.message}`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/pdf': ['.pdf'],
    },
    multiple: false,
  });

  const renderDataPreview = () => {
    if (!uploadResult?.data_preview) return null;

    const { data_preview } = uploadResult;

    if (data_preview.text_length) {
      // PDF preview
      return (
        <Box>
          <Typography variant="h6" gutterBottom>
            Document Preview
          </Typography>
          <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Text Length: {data_preview.text_length} characters | 
              Word Count: {data_preview.word_count} words
            </Typography>
            <Typography variant="body2" sx={{ mt: 1, fontFamily: 'monospace' }}>
              {data_preview.preview}
            </Typography>
          </Paper>
        </Box>
      );
    }

    if (data_preview.shape) {
      // CSV/Excel preview
      return (
        <Box>
          <Typography variant="h6" gutterBottom>
            Data Preview
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Chip label={`${data_preview.shape[0]} rows × ${data_preview.shape[1]} columns`} />
          </Box>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Column Information</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer component={Paper} sx={{ maxHeight: 200 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Column</TableCell>
                      <TableCell>Data Type</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(data_preview.dtypes || {}).map(([column, dtype]) => (
                      <TableRow key={column}>
                        <TableCell>{column}</TableCell>
                        <TableCell>{dtype}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>

          {data_preview.head && (
            <Accordion sx={{ mt: 1 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>Sample Data</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        {data_preview.columns?.map((column) => (
                          <TableCell key={column}>{column}</TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {data_preview.head.map((row, index) => (
                        <TableRow key={index}>
                          {data_preview.columns?.map((column) => (
                            <TableCell key={column}>
                              {row[column] !== null && row[column] !== undefined 
                                ? String(row[column]) 
                                : 'N/A'}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </AccordionDetails>
            </Accordion>
          )}
        </Box>
      );
    }

    return null;
  };

  const renderCharts = () => {
    if (charts.length === 0) return null;

    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Data Visualizations
        </Typography>
        {charts.map((chart, index) => (
          <Paper key={index} sx={{ p: 2, mb: 2 }} className="chart-container">
            <Plot
              data={chart.data}
              layout={{
                ...chart.layout,
                autosize: true,
                margin: { l: 50, r: 50, t: 50, b: 50 },
              }}
              useResizeHandler
              style={{ width: '100%', height: '400px' }}
              config={{ responsive: true, displayModeBar: false }}
            />
          </Paper>
        ))}
      </Box>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        File Upload & Analysis
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload CSV, Excel, or PDF files for financial analysis. Supported formats: .csv, .xlsx, .xls, .pdf
      </Typography>

      {/* Upload Zone */}
      <Paper
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
        sx={{
          p: 4,
          mb: 3,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.400',
          bgcolor: isDragActive ? 'primary.light' : 'grey.50',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'primary.light',
          },
        }}
      >
        <input {...getInputProps()} />
        <Box display="flex" flexDirection="column" alignItems="center">
          <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          
          {uploadStatus === 'uploading' ? (
            <>
              <CircularProgress size={24} sx={{ mb: 2 }} />
              <Typography>Uploading and processing file...</Typography>
            </>
          ) : (
            <>
              <Typography variant="h6" gutterBottom>
                {isDragActive ? 'Drop the file here' : 'Drag & drop a file here, or click to select'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Supports CSV, Excel (.xlsx, .xls), and PDF files
              </Typography>
            </>
          )}
        </Box>
      </Paper>

      {/* Upload Status */}
      {uploadStatus === 'success' && (
        <Alert 
          severity="success" 
          icon={<CheckCircle />}
          sx={{ mb: 3 }}
        >
          {uploadResult?.message || 'File uploaded and processed successfully!'}
        </Alert>
      )}

      {uploadStatus === 'error' && (
        <Alert 
          severity="error" 
          icon={<Error />}
          sx={{ mb: 3 }}
        >
          {uploadResult?.error || 'Upload failed. Please try again.'}
        </Alert>
      )}

      {/* Results */}
      {uploadResult && uploadStatus === 'success' && (
        <Box>
          {renderDataPreview()}
          {renderCharts()}
        </Box>
      )}
    </Box>
  );
};

export default FileUpload;
