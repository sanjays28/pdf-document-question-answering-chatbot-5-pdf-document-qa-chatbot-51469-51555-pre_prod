import React, { useState, useRef, useEffect } from 'react';
import { askQuestion } from '../services/api';
import './ChatInterface.css';

// PUBLIC_INTERFACE
const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const question = inputValue.trim();
    setInputValue('');
    setMessages(prev => [...prev, { type: 'user', content: question }]);
    setIsLoading(true);

    try {
      const response = await askQuestion(question);
      setMessages(prev => [...prev, { type: 'bot', content: response }]);
    } catch (error) {
      setMessages(prev => [...prev, { type: 'error', content: error.message }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.type}`}
          >
            <div className="message-content">
              {message.type === 'bot' && <span className="bot-icon">🤖</span>}
              {message.type === 'user' && <span className="user-icon">👤</span>}
              <p>{message.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot">
            <div className="message-content">
              <span className="bot-icon">🤖</span>
              <div className="typing-indicator" role="status" aria-label="Loading response">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="input-container">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask a question about the PDF..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !inputValue.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
