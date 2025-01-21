import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PDFUpload from '../components/PDFUpload';
import { uploadPDF } from '../services/api';

// Mock the API module
jest.mock('../services/api', () => ({
  uploadPDF: jest.fn()
}));

describe('PDFUpload Component', () => {
  const mockOnUploadSuccess = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders upload area with correct text', () => {
    render(<PDFUpload onUploadSuccess={mockOnUploadSuccess} />);
    expect(screen.getByText(/Drag and drop a PDF file here or click to select/i)).toBeInTheDocument();
  });

  test('handles file selection through input', async () => {
    uploadPDF.mockResolvedValueOnce({ success: true });
    render(<PDFUpload onUploadSuccess={mockOnUploadSuccess} />);

    const file = new File(['dummy content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/Drag and drop a PDF file here or click to select/i);

    await act(async () => {
      await userEvent.upload(input, file);
    });

    expect(uploadPDF).toHaveBeenCalledWith(file);
    await waitFor(() => {
      expect(mockOnUploadSuccess).toHaveBeenCalledWith({ success: true });
    });
  });

  test('shows error message for non-PDF files', async () => {
    render(<PDFUpload onUploadSuccess={mockOnUploadSuccess} />);

    const file = new File(['dummy content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/Drag and drop a PDF file here or click to select/i);

    await act(async () => {
      await userEvent.upload(input, file);
    });

    await waitFor(() => {
      expect(screen.getByText(/Please upload a PDF file/i)).toBeInTheDocument();
    });
    expect(uploadPDF).not.toHaveBeenCalled();
    expect(mockOnUploadSuccess).not.toHaveBeenCalled();
  });

  test('handles drag and drop interactions', async () => {
    uploadPDF.mockResolvedValueOnce({ success: true });
    render(<PDFUpload onUploadSuccess={mockOnUploadSuccess} />);

    const uploadArea = screen.getByLabelText(/Drag and drop a PDF file here or click to select/i).parentElement;

    // Test drag over
    await act(async () => {
      fireEvent.dragOver(uploadArea);
    });
    expect(uploadArea).toHaveClass('dragging');

    // Test drag leave
    await act(async () => {
      fireEvent.dragLeave(uploadArea);
    });
    expect(uploadArea).not.toHaveClass('dragging');

    // Test drop
    const file = new File(['dummy content'], 'test.pdf', { type: 'application/pdf' });
    const dataTransfer = {
      files: [file],
      types: ['Files']
    };

    await act(async () => {
      fireEvent.drop(uploadArea, { dataTransfer });
    });

    expect(uploadPDF).toHaveBeenCalledWith(file);
    await waitFor(() => {
      expect(mockOnUploadSuccess).toHaveBeenCalledWith({ success: true });
    });
  });

  test('handles upload error', async () => {
    const errorMessage = 'Upload failed';
    uploadPDF.mockRejectedValueOnce(new Error(errorMessage));
    render(<PDFUpload onUploadSuccess={mockOnUploadSuccess} />);

    const file = new File(['dummy content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/Drag and drop a PDF file here or click to select/i);

    await act(async () => {
      await userEvent.upload(input, file);
    });

    expect(await screen.findByText(errorMessage)).toBeInTheDocument();
    expect(mockOnUploadSuccess).not.toHaveBeenCalled();
  });
});
