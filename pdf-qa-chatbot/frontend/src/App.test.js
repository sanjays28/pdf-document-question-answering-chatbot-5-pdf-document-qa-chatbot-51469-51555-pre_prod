import { render, screen, act } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  test('renders app title and PDF upload component initially', () => {
    render(<App />);
    expect(screen.getByText('PDF Document QA Chatbot')).toBeInTheDocument();
    expect(screen.getByText(/Drag and drop a PDF file here or click to select/i)).toBeInTheDocument();
  });

  test('shows chat interface after successful file upload', async () => {
    render(<App />);
    
    // Simulate successful file upload
    await act(async () => {
      const uploadComponent = screen.getByText(/Drag and drop a PDF file here or click to select/i).closest('div');
      const onUploadSuccess = uploadComponent.props.onUploadSuccess;
      onUploadSuccess({ success: true });
    });

    // Verify chat interface is shown
    expect(screen.getByPlaceholderText(/Ask a question about the PDF.../i)).toBeInTheDocument();
    expect(screen.queryByText(/Drag and drop a PDF file here or click to select/i)).not.toBeInTheDocument();
  });
});
