import { useState } from 'react';
import './App.css';
import PDFUpload from './components/PDFUpload';
import ChatInterface from './components/ChatInterface';

function App() {
  const [isFileUploaded, setIsFileUploaded] = useState(false);

  const handleUploadSuccess = () => {
    setIsFileUploaded(true);
  };

  return (
    <div className="App">
      <div className="app-container">
        <h1>PDF Document QA Chatbot</h1>
        {!isFileUploaded ? (
          <PDFUpload onUploadSuccess={handleUploadSuccess} />
        ) : (
          <ChatInterface />
        )}
      </div>
    </div>
  );
}

export default App;
