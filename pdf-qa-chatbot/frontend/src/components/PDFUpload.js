import React, { useState, useCallback } from 'react';
import { uploadPDF } from '../services/api';
import './PDFUpload.css';

// PUBLIC_INTERFACE
const PDFUpload = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(async (e) => {
    e.preventDefault();
    setIsDragging(false);
    setError(null);

    const file = e.dataTransfer.files[0];
    if (!file || !file.type.includes('pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    try {
      setUploadProgress(0);
      const result = await uploadPDF(file);
      setUploadProgress(100);
      onUploadSuccess(result);
    } catch (error) {
      setError(error.message);
    }
  }, [onUploadSuccess]);

  const handleFileSelect = useCallback(async (e) => {
    const file = e.target.files[0];
    if (!file || !file.type.includes('pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    try {
      setUploadProgress(0);
      const result = await uploadPDF(file);
      setUploadProgress(100);
      onUploadSuccess(result);
    } catch (error) {
      setError(error.message);
    }
  }, [onUploadSuccess]);

  return (
    <div className="pdf-upload-container">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          className="file-input"
          id="file-input"
        />
        <label htmlFor="file-input" className="upload-label">
          <div className="upload-content">
            <i className="upload-icon">📄</i>
            <p>Drag and drop a PDF file here or click to select</p>
          </div>
        </label>
      </div>
      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="progress-bar">
          <div
            className="progress"
            style={{ width: `${uploadProgress}%` }}
          ></div>
        </div>
      )}
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default PDFUpload;