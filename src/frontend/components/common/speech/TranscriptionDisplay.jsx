// /src/frontend/components/speech/TranscriptionDisplay.jsx
import React from 'react';
import './TranscriptionDisplay.css';

const TranscriptionDisplay = ({ transcription, isLoading }) => {
  if (isLoading) {
    return <div className="transcription-loading">Listening...</div>;
  }
  
  if (!transcription) {
    return <div className="transcription-placeholder">Your transcription will appear here</div>;
  }
  
  return (
    <div className="transcription-display">
      <p>{transcription}</p>
    </div>
  );
};

export default TranscriptionDisplay;