const API_BASE_URL = 'http://localhost:8000/api';

// PUBLIC_INTERFACE
export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('PDF upload failed');
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Error uploading PDF: ${error.message}`);
  }
};

// PUBLIC_INTERFACE
export const askQuestion = async (question) => {
  try {
    const response = await fetch(`${API_BASE_URL}/question`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error('Failed to get answer');
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Error getting answer: ${error.message}`);
  }
};