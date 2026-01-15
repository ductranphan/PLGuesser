import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState('');
  
  const { login, loading, error, clearError } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');
    clearError();

    // Basic validation
    if (!username.trim()) {
      setLocalError('Username is required');
      return;
    }
    if (!password) {
      setLocalError('Password is required');
      return;
    }

    try {
      await login(username.trim(), password);
      // Redirect to game page on success
      navigate('/game');
    } catch (err) {
      // Error is handled by AuthContext, but we can show local error too
      setLocalError(err.message || 'Login failed. Please try again.');
    }
  };

  const displayError = localError || error;

  return (
    <div className="min-h-screen flex items-center justify-center p-5">
      <div className="bg-[#28002a] rounded-xl shadow-2xl border-2 border-[#2D1B69] p-10 w-full max-w-md backdrop-blur-sm">
        <h1 className="text-center text-[#00ff85] mb-2 text-3xl font-bold">PLGuesser</h1>
        <h2 className="text-center text-white mb-8 text-2xl font-medium">Login</h2>
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          {displayError && (
            <div className="bg-red-50 text-red-700 p-3 rounded-lg border border-red-200 text-sm" role="alert">
              {displayError}
            </div>
          )}

          <div className="flex flex-col gap-2">
            <label htmlFor="username" className="font-medium text-white text-sm">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                setLocalError('');
                clearError();
              }}
              placeholder="Enter your username"
              disabled={loading}
              autoComplete="username"
              className="px-4 py-3 border-2 border-gray-200 rounded-lg text-base transition-colors focus:outline-none focus:border-[#00ff85] disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="password" className="font-medium text-white text-sm">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setLocalError('');
                clearError();
              }}
              placeholder="Enter your password"
              disabled={loading}
              autoComplete="current-password"
              className="px-4 py-3 border-2 border-gray-200 rounded-lg text-base transition-colors focus:outline-none focus:border-[#00ff85] disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>

          <button 
            type="submit" 
            className="px-4 py-3.5 bg-[#00ff85] text-black rounded-lg text-base font-semibold cursor-pointer transition-all hover:bg-[#00e676] hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none mt-2"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="text-center mt-5 text-white text-sm">
          Don't have an account? <Link to="/register" className="text-[#00ff85] font-medium hover:underline">Register here</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
