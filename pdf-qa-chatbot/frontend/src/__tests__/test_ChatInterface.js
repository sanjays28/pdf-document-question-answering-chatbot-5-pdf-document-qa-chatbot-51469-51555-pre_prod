import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatInterface from '../components/ChatInterface';
import { askQuestion } from '../services/api';

jest.mock('../services/api');

describe('ChatInterface Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders chat interface with input field and send button', () => {
    render(<ChatInterface />);
    expect(screen.getByPlaceholderText(/Ask a question about the PDF.../i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  test('handles user input and message submission', async () => {
    const mockResponse = { answer: 'This is a test response' };
    askQuestion.mockResolvedValueOnce(mockResponse);
    
    render(<ChatInterface />);
    
    const input = screen.getByPlaceholderText(/Ask a question about the PDF.../i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await userEvent.type(input, 'Test question');
    expect(input).toHaveValue('Test question');
    
    fireEvent.click(sendButton);
    
    expect(askQuestion).toHaveBeenCalledWith('Test question');
    expect(input).toHaveValue('');
    
    await waitFor(() => {
      expect(screen.getByText('Test question')).toBeInTheDocument();
      expect(screen.getByText(mockResponse.answer)).toBeInTheDocument();
    });
  });

  test('displays error message when API call fails', async () => {
    const errorMessage = 'Error getting answer: Failed to get answer';
    askQuestion.mockRejectedValueOnce(new Error('Failed to get answer'));
    
    render(<ChatInterface />);
    
    const input = screen.getByPlaceholderText(/Ask a question about the PDF.../i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await userEvent.type(input, 'Test question');
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  test('disables input and button while loading', async () => {
    const mockResponse = { answer: 'Response' };
    let resolvePromise;
    const promise = new Promise(resolve => {
      resolvePromise = () => resolve(mockResponse);
    });
    askQuestion.mockImplementation(() => promise);
    
    render(<ChatInterface />);
    
    const input = screen.getByPlaceholderText(/Ask a question about the PDF.../i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await userEvent.type(input, 'Test question');
    fireEvent.click(sendButton);
    
    expect(input).toBeDisabled();
    expect(sendButton).toBeDisabled();
    
    resolvePromise();
    await waitFor(() => {
      expect(input).not.toBeDisabled();
      expect(sendButton).not.toBeDisabled();
    });
  });

  test('does not submit empty messages', async () => {
    render(<ChatInterface />);
    
    const input = screen.getByPlaceholderText(/Ask a question about the PDF.../i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await userEvent.type(input, '   ');
    fireEvent.click(sendButton);
    
    expect(askQuestion).not.toHaveBeenCalled();
  });

  test('shows loading indicator while waiting for response', async () => {
    const mockResponse = { answer: 'Response' };
    let resolvePromise;
    const promise = new Promise(resolve => {
      resolvePromise = () => resolve(mockResponse);
    });
    askQuestion.mockImplementation(() => promise);
    
    render(<ChatInterface />);
    
    const input = screen.getByPlaceholderText(/Ask a question about the PDF.../i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await userEvent.type(input, 'Test question');
    fireEvent.click(sendButton);
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    
    resolvePromise();
    await waitFor(() => {
      expect(screen.queryByRole('status')).not.toBeInTheDocument();
    });
  });
});
