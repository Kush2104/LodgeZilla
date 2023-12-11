// App.js

import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './pages/Login';
import HostPage from './pages/HostPage';
import TouristPage from './pages/TouristPage';
import { AuthProvider } from './services/AuthContext';

const App = () => {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/host" element={<HostPage />} />
          <Route path="/tourist" element={<TouristPage />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
};

export default App;
