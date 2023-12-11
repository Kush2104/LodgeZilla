// LogoutButton.js

import React from 'react';
import Button from '@mui/material/Button';
import { useNavigate } from 'react-router-dom';

const LogoutButton = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Add logic to perform logout actions if needed

    // Redirect to the login page
    navigate('/');
  };

  return (
    <Button onClick={handleLogout} style={{ position: 'absolute', top: '10px', right: '10px' }}>
      Logout
    </Button>
  );
};

export default LogoutButton;
