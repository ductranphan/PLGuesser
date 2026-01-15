import axios from 'axios';

// Base URL for the API (adjust if your backend runs on a different port)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized - token expired or invalid
    if (error.response?.status === 401) {
      const token = localStorage.getItem('token');
      if (token) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // Redirect to login if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// ==================== AUTH API ====================

/**
 * Register a new user
 * @param {Object} userData - {username, email, password}
 * @returns {Promise<Object>} User data (without password)
 */
export const register = async (userData) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

/**
 * Login user and get access token
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {Promise<Object>} {access_token, token_type}
 */
export const login = async (username, password) => {
  // OAuth2PasswordRequestForm expects form data, not JSON
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await api.post('/auth/token', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  // Store token in localStorage
  const { access_token } = response.data;
  localStorage.setItem('token', access_token);
  
  // Fetch and store user data
  const userData = await getCurrentUser();
  localStorage.setItem('user', JSON.stringify(userData));
  
  return response.data;
};

/**
 * Logout user (clear token from localStorage)
 */
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

/**
 * Get current authenticated user
 * @returns {Promise<Object>} User data
 */
export const getCurrentUser = async () => {
  const response = await api.get('/me');
  localStorage.setItem('user', JSON.stringify(response.data));
  return response.data;
};

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

/**
 * Get stored user data from localStorage
 * @returns {Object|null}
 */
export const getStoredUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

// ==================== PLAYERS API ====================

/**
 * List players with optional filters
 * @param {Object} filters - {name, nationality, club, position, limit, offset}
 * @returns {Promise<Array>} Array of player objects
 */
export const getPlayers = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.name) params.append('name', filters.name);
  if (filters.nationality) params.append('nationality', filters.nationality);
  if (filters.club) params.append('club', filters.club);
  if (filters.position) params.append('position', filters.position);
  if (filters.limit) params.append('limit', filters.limit);
  if (filters.offset) params.append('offset', filters.offset);
  
  const response = await api.get('/players', { params });
  return response.data;
};

/**
 * Search players by name (quick search)
 * @param {string} query - Search query
 * @returns {Promise<Array>} Array of player objects (max 20)
 */
export const searchPlayers = async (query) => {
  const response = await api.get('/players/search', {
    params: { q: query },
  });
  return response.data;
};

/**
 * Get random player
 * @returns {Promise<Object>} Random player object
 */
export const getRandomPlayer = async () => {
  const response = await api.get('/players/random');
  return response.data;
};

/**
 * Get player by ID
 * @param {number} playerId - Player ID
 * @returns {Promise<Object>} Player object
 */
export const getPlayerById = async (playerId) => {
  const response = await api.get(`/players/${playerId}`);
  return response.data;
};

// ==================== GAMES API ====================

/**
 * Create a new game
 * @returns {Promise<Object>} Game object
 */
export const createGame = async () => {
  const response = await api.post('/games', {});
  return response.data;
};

/**
 * Submit a guess for a game
 * @param {number} gameId - Game ID
 * @param {number} playerId - Player ID being guessed
 * @returns {Promise<Object>} Updated game object
 */
export const submitGuess = async (gameId, playerId) => {
  const response = await api.post(`/games/${gameId}/guess`, {
    player_id: playerId,
  });
  return response.data;
};

/**
 * Get game state by ID
 * @param {number} gameId - Game ID
 * @returns {Promise<Object>} Game object with all guesses
 */
export const getGameById = async (gameId) => {
  const response = await api.get(`/games/${gameId}`);
  return response.data;
};

/**
 * List user's games
 * @param {string} status - Optional filter: 'in_progress', 'won', 'lost'
 * @returns {Promise<Array>} Array of game objects
 */
export const getGames = async (status = null) => {
  const params = status ? { status } : {};
  const response = await api.get('/games', { params });
  return response.data;
};

// ==================== STATS API ====================

/**
 * Get current user's statistics
 * @returns {Promise<Object>} User statistics object
 */
export const getUserStats = async () => {
  const response = await api.get('/stats/me');
  return response.data;
};

// ==================== GAMES API ====================

/**
 * Create a free play game (no login required)
 */
export const createFreePlayGame = async () => {
  const response = await api.post('/games/free-play', {});
  return response.data;
};

/**
 * Start or resume today's daily challenge (login required)
 */
export const startDailyChallenge = async () => {
  const response = await api.post('/games', {});
  return response.data;
};

// ==================== LEADERBOARD API ====================

/**
 * Get global leaderboard
 * @param {string} sortBy - 'win_rate', 'total_wins', 'win_streak', 'avg_guesses'
 * @param {number} limit - Number of entries to return
 */
export const getLeaderboard = async (sortBy = 'win_rate', limit = 100) => {
  const response = await api.get('/leaderboard/global', {
    params: { sort_by: sortBy, limit }
  });
  return response.data;
};

/**
 * Get current user's stats
 */
export const getMyStats = async () => {
  const response = await api.get('/leaderboard/me');
  return response.data;
};

/**
 * Get current user's rank
 */
export const getMyRank = async (sortBy = 'win_rate') => {
  const response = await api.get('/leaderboard/my-rank', {
    params: { sort_by: sortBy }
  });
  return response.data;
};


// Export the axios instance for custom requests if needed
export default api;
