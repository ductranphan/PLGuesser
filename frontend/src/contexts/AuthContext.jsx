import { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, register as apiRegister, logout as apiLogout, getCurrentUser, getStoredUser, isAuthenticated } from '../services/api';

// Create the context
const AuthContext = createContext(null);

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// AuthProvider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load user from localStorage on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedUser = getStoredUser();
        if (storedUser && isAuthenticated()) {
          // Verify token is still valid by fetching current user
          try {
            const currentUser = await getCurrentUser();
            setUser(currentUser);
          } catch (err) {
            // Token invalid, clear storage
            apiLogout();
            setUser(null);
          }
        }
      } catch (err) {
        console.error('Error initializing auth:', err);
        apiLogout();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Register a new user
   * @param {Object} userData - {username, email, password}
   * @returns {Promise<void>}
   */
  const register = async (userData) => {
    try {
      setError(null);
      setLoading(true);
      const newUser = await apiRegister(userData);
      
      // After registration, automatically log in
      await login(userData.username, userData.password);
      
      return newUser;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Registration failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Login user
   * @param {string} username - Username
   * @param {string} password - Password
   * @returns {Promise<void>}
   */
  const login = async (username, password) => {
    try {
      setError(null);
      setLoading(true);
      await apiLogin(username, password);
      
      // Fetch and set user data
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Login failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Logout user
   */
  const logout = () => {
    try {
      apiLogout();
      setUser(null);
      setError(null);
    } catch (err) {
      console.error('Error during logout:', err);
      // Clear state even if API call fails
      setUser(null);
      setError(null);
    }
  };

  /**
   * Clear error message
   */
  const clearError = () => {
    setError(null);
  };

  // Value object to provide to consumers
  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user && isAuthenticated(),
    login,
    register,
    logout,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
