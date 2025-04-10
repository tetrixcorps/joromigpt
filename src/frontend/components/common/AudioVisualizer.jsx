// /src/frontend/components/common/AudioVisualizer.jsx
import React, { useEffect, useRef } from 'react';
import './AudioVisualizer.css';

const AudioVisualizer = () => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  
  useEffect(() => {
    let audioContext;
    let analyser;
    let microphone;
    
    const setupAudio = async () => {
      try {
        // Create audio context
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyserRef.current = analyser;
        
        // Configure analyser
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        dataArrayRef.current = dataArray;
        
        // Get microphone stream
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        microphone = audioContext.createMediaStreamSource(stream);
        microphone.connect(analyser);
        
        // Start visualization
        visualize();
      } catch (err) {
        console.error('Error setting up audio visualizer:', err);
      }
    };
    
    const visualize = () => {
      if (!canvasRef.current) return;
      
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      const width = canvas.width;
      const height = canvas.height;
      
      const draw = () => {
        animationRef.current = requestAnimationFrame(draw);
        
        analyserRef.current.getByteFrequencyData(dataArrayRef.current);
        
        ctx.fillStyle = 'rgb(20, 20, 20)';
        ctx.fillRect(0, 0, width, height);
        
        const barWidth = (width / dataArrayRef.current.length) * 2.5;
        let barHeight;
        let x = 0;
        
        for (let i = 0; i < dataArrayRef.current.length; i++) {
          barHeight = dataArrayRef.current[i] / 2;
          
          ctx.fillStyle = `rgb(${barHeight + 100}, 50, 50)`;
          ctx.fillRect(x, height - barHeight, barWidth, barHeight);
          
          x += barWidth + 1;
        }
      };
      
      draw();
    };
    
    setupAudio();
    
    return () => {
      cancelAnimationFrame(animationRef.current);
      if (microphone) {
        microphone.disconnect();
      }
      if (audioContext) {
        audioContext.close();
      }
    };
  }, []);
  
  return (
    <div className="audio-visualizer">
      <canvas ref={canvasRef} width="300" height="60"></canvas>
    </div>
  );
};

export default AudioVisualizer;