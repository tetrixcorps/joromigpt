// /src/frontend/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import Home from './pages/Home';
import Chat from './pages/Chat';
import Settings from './pages/Settings';
import { LanguageProvider } from './context/LanguageContext';
import './styles/global.css';

const App = () => {
  return (
    <LanguageProvider>
      <Router>
        <div className="app">
          <Header />
          
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
          
          <Footer />
        </div>
      </Router>
    </LanguageProvider>
  );
};

export default App;