import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from '../pages/Home';
import WhatsAppIntegration from '../components/whatsapp/WhatsAppIntegration';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>African Voice AI</h1>
          <nav>
            <ul>
              <li>
                <Link to="/">Home</Link>
              </li>
              <li>
                <Link to="/whatsapp">WhatsApp</Link>
              </li>
            </ul>
          </nav>
        </header>
        
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/whatsapp" element={<WhatsAppIntegration />} />
          </Routes>
        </main>
        
        <footer>
          <p>&copy; {new Date().getFullYear()} African Voice AI Platform</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
