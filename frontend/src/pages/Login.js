import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Signup from '../components/SignUp'; // Import the Signup component
import {login} from "../services/UserApi"
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import {useAuth} from '../services/AuthContext'

const Login = () => {
  const { login: setAuthToken } = useAuth();
  const [isLoginView, setIsLoginView] = useState(true);
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleNameChange = (e) => {
    setName(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const handleLogin = async () => {
    try {
      const data = await login(name, password);
      setAuthToken(data.access_token);

      // Decode the JWT token to get user information
      const decodedToken = JSON.parse(atob(data.access_token.split('.')[1]));

      // Redirect based on user type
      if (decodedToken.userType === 'tourist') {
        navigate('/tourist');
      } else if (decodedToken.userType === 'host') {
        navigate('/host');
      }
    } catch (error) {
      console.error(error.message);
      // Display an error message to the user
    }
  };


  const handleSignup = () => {
    setIsLoginView(false);    
  };

  const handleCancel = () => {
    setIsLoginView(true);
  };

  const handleCreateUser = (userData) => {
    // Add your logic to create the user (send data to the server, etc.)
    console.log('Creating user with data:', userData);

    // After creating the user, navigate back to the login view
    setIsLoginView(true);
  };

  return (
    <div style={{ textAlign: 'center', backgroundColor: '#dcdcdc', height: '100vh'}}>
      <img src="/images/LodgeZillaLogo.png" alt="LodgeZilla Logo" style={{ scale:100, marginBottom: '10px'}} />
      {isLoginView ? (
        <>
          <h2>User Login</h2>
          <form>
            <div>
              <TextField
                label="User Name"
                variant="outlined"
                value={name}
                onChange={handleNameChange}
                placeholder="Enter User Name"
                />
            </div>
            <div>
                <TextField
                  label="Password"
                  variant="outlined"
                  value={password}
                  onChange={handlePasswordChange}
                  placeholder="Enter Password"
                />
            </div>
            <div>
              <Button type="button" onClick={handleLogin} style={{marginTop: '30px', marginRight: '10px'}}>
                Login
              </Button>
              <Button type="button" onClick={handleSignup} style={{marginTop: '30px'}}>
                Sign Up
              </Button>
            </div>
          </form>
        </>
      ) : (
        <Signup onCancel={handleCancel} onSignup={handleCreateUser} />
      )}
    </div>
  );
};

export default Login;

