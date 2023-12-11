// apiService.js

const API_BASE_URL = 'http://127.0.0.1:8000/auth';

export const createUser = async (userData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (response.ok) {
      const responseData = await response.json();
      return responseData;
    } else {
      throw new Error('Failed to create user');
    }
  } catch (error) {
    console.error('Error during user creation:', error);
    throw error;
  }
};

export const login = async (user_id, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/token?user_id=${user_id}&password=${password}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail);
      }
    } catch (error) {
      throw new Error('Error during login');
    }
  };

