// /src/frontend/pages/Home.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import AudioRecorder from '../components/speech/AudioRecorder';
import TranscriptionDisplay from '../components/speech/TranscriptionDisplay';
import TextToSpeech from '../components/speech/TextToSpeech';
import { useLanguage } from '../context/LanguageContext';
import './Home.css';

const Home = () => {
  const [transcription, setTranscription] = useState('');
  const [isTranscribing, setIsTranscribing] = useState(false);
  const { language } = useLanguage();
  
  const handleTranscriptionStart = () => {
    setIsTranscribing(true);
    setTranscription('');
  };
  
  const handleTranscriptionComplete = (text) => {
    setTranscription(text);
    setIsTranscribing(false);
  };
  
  return (
    <div className="home-page">
      <section className="hero-section">
        <h1>African Voice AI Platform</h1>
        <p>Speak your language, be understood everywhere</p>
        
        <div className="demo-container">
          <h2>Try it now</h2>
          <p>Record your voice in {language}</p>
          
          <AudioRecorder 
            onTranscriptionStart={handleTranscriptionStart}
            onTranscriptionComplete={handleTranscriptionComplete} 
          />
          
          <TranscriptionDisplay 
            transcription={transcription} 
            isLoading={isTranscribing} 
          />
          
          {transcription && <TextToSpeech text={transcription} />}
        </div>
        
        <div className="cta-buttons">
          <Link to="/chat" className="cta-button">
            Start Chatting
          </Link>
          <Link to="/whatsapp" className="cta-button whatsapp-cta">
            Try WhatsApp Integration
          </Link>
        </div>
      </section>
      
      <section className="features-section">
        <h2>Features</h2>
        
        <div className="feature-cards">
          <div className="feature-card">
            <h3>Speech Recognition</h3>
            <p>Accurate transcription in multiple African languages</p>
          </div>
          
          <div className="feature-card">
            <h3>Text to Speech</h3>
            <p>Natural-sounding voices in your preferred language</p>
          </div>
          
          <div className="feature-card">
            <h3>AI Assistant</h3>
            <p>Intelligent responses powered by advanced language models</p>
          </div>
          
          <div className="feature-card">
            <h3>WhatsApp Integration</h3>
            <p>Send voice messages in different languages via WhatsApp</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;