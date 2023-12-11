// AuthContext.js

import { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [jwtToken, setJwtToken] = useState(null);

  const login = (token) => {
    setJwtToken(token);
  };

  const logout = () => {
    setJwtToken(null);
  };

  return (
    <AuthContext.Provider value={{ jwtToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
