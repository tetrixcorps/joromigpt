// /src/frontend/components/whatsapp/WhatsAppAuth.jsx
import React, { useState, useEffect } from 'react';
import { checkWhatsAppAuth, getWhatsAppQRCode } from '../../services/whatsappService';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import './WhatsAppAuth.css';

const WhatsAppAuth = ({ onAuthSuccess }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        setIsLoading(true);
        const authenticated = await checkWhatsAppAuth();
        setIsAuthenticated(authenticated);
        
        if (authenticated && onAuthSuccess) {
          onAuthSuccess();
        } else if (!authenticated) {
          // If not authenticated, fetch QR code
          const qrUrl = await getWhatsAppQRCode();
          setQrCodeUrl(qrUrl);
        }
      } catch (err) {
        setError('Failed to connect to WhatsApp service. Please try again later.');
        console.error('WhatsApp auth error:', err);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
    
    // Poll for auth status every 5 seconds while QR code is shown
    const intervalId = setInterval(async () => {
      if (!isAuthenticated && qrCodeUrl) {
        const authenticated = await checkWhatsAppAuth();
        if (authenticated) {
          setIsAuthenticated(true);
          if (onAuthSuccess) onAuthSuccess();
          clearInterval(intervalId);
        }
      }
    }, 5000);
    
    return () => clearInterval(intervalId);
  }, [isAuthenticated, onAuthSuccess, qrCodeUrl]);
  
  if (isLoading) {
    return <LoadingSpinner message="Connecting to WhatsApp..." />;
  }
  
  if (error) {
    return <ErrorMessage message={error} />;
  }
  
  if (isAuthenticated) {
    return (
      <div className="whatsapp-auth-success">
        <h3>WhatsApp Connected</h3>
        <p>Your WhatsApp account is successfully connected.</p>
      </div>
    );
  }
  
  return (
    <div className="whatsapp-auth-container">
      <h3>Connect to WhatsApp</h3>
      <p>Scan this QR code with your WhatsApp app to connect:</p>
      <p className="whatsapp-auth-instructions">
        Open WhatsApp on your phone &gt; Settings &gt; Linked Devices &gt; Link a Device
      </p>
      {qrCodeUrl && (
        <div className="whatsapp-qr-container">
          <img 
            src={qrCodeUrl} 
            alt="WhatsApp QR Code" 
            className="whatsapp-qr-code"
          />
        </div>
      )}
    </div>
  );
};

export default WhatsAppAuth;