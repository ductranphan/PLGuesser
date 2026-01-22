import { useState } from 'react';
import { Analytics } from '@vercel/analytics/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  createFreePlayGame,
  startDailyChallenge,
  isAuthenticated 
} from '../services/api';

function Home() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const isLoggedIn = isAuthenticated();

  const handleFreePlay = async () => {
    setLoading(true);
    try {
      // If user is logged in, log them out first (free play is for guests only)
      if (isLoggedIn) {
        console.log('Logging out to play free play...');
        await logout();
        // Wait a moment for logout to complete
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      await createFreePlayGame();
      navigate('/game');
    } catch (error) {
      console.error('Error creating free play game:', error);
      alert('Failed to create game. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDailyChallenge = async () => {
    setLoading(true);
    try {
      // Start or resume today's challenge
      await startDailyChallenge();
      navigate('/game');
    } catch (error) {
      console.error('Error starting daily challenge:', error);
      alert(error.response?.data?.detail || 'Failed to start daily challenge.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Analytics />
      <div className="min-h-screen bg-[#28002a] rounded-lg shadow-md border-2 border-[#2D1B69] py-12 px-4">
        <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            ⚽ PLGuesser
          </h1>
          <p className="text-xl text-gray-100">
            Guess the Premier League player in 6 tries or less!
          </p>
        </div>

        {/* Game Modes */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Free Play Card */}
          <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-4">🎮</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Free Play</h2>
            <p className="text-gray-600 mb-6">
              Play unlimited games with random players. Perfect for practice!
            </p>
            <ul className="text-sm text-black mb-6 space-y-2">
              <li>✓ No login required</li>
              <li>✓ Unlimited games</li>
              <li>✓ Random players</li>
              <li>✗ Stats not tracked</li>
            </ul>
            <button
              onClick={handleFreePlay}
              disabled={loading}
              className="w-full bg-[#00ff85] text-black py-3 rounded-lg font-semibold hover:bg-[#00e676] transition-colors"
            >
              {loading ? 'Starting...' : isLoggedIn ? 'Logout & Play Free' : 'Start Free Play'}
            </button>
            {isLoggedIn && (
              <p className="text-xs text-gray-500 mt-2 text-center">
                Note: This will log you out
              </p>
            )}
          </div>

          {/* Daily Challenge Card */}
          {isLoggedIn ? (
            <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-gray-300 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">🏆</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">Daily Challenge</h2>
              <p className="text-gray-600 mb-6">
                Compete with everyone on the same mystery player!
              </p>
              <ul className="text-sm text-black mb-6 space-y-2">
                <li>✓ One game per day</li>
                <li>✓ Same player for everyone</li>
                <li>✓ Stats tracked</li>
                <li>✓ Leaderboard ranking</li>
              </ul>
              <button
                onClick={handleDailyChallenge}
                disabled={loading}
                className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white py-3 rounded-lg font-semibold hover:from-yellow-600 hover:to-orange-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all"
              >
                {loading ? 'Starting...' : "Play Today's Challenge"}
              </button>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-gray-300">
              <div className="text-4xl mb-4">🔒</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">Daily Challenge</h2>
              <p className="text-gray-600 mb-6">
                Login to compete on the daily leaderboard and track your stats!
              </p>
              <ul className="text-sm text-black mb-6 space-y-2">
                <li>✓ One game per day</li>
                <li>✓ Same player for everyone</li>
                <li>✓ Stats tracked</li>
                <li>✓ Leaderboard ranking</li>
              </ul>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/login')}
                  className="w-full bg-[#00ff85] text-black py-3 rounded-lg font-semibold hover:bg-[#00e676] transition-colors"
                >
                  Login
                </button>
                <button
                  onClick={() => navigate('/register')}
                  className="w-full bg-[#00ff85] text-black py-3 rounded-lg font-semibold border-2 border-[#00ff85] hover:bg-[#00e676] transition-colors"
                >
                  Sign Up
                </button>
              </div>
            </div>
          )}
        </div>

        {/* How to Play */}
        <div className="mt-12 bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">How to Play</h2>
          <div className="space-y-3 text-gray-700">
            <p>🎯 Guess the mystery <strong>2024-2025 SEASON PREMIER LEAGUE </strong> player using hints in 6 tries</p>
            <p>💡 Guess with <strong>player's last name</strong> first</p>
            <ul className="ml-8 space-y-2">
              <li><strong className="text-green-500">Green</strong> = Exact match</li>
              <li><strong className="text-yellow-500">Yellow</strong> = Close (age within 3 years, etc.)</li>
              <li><strong className="text-red-500">Red</strong> = Wrong</li>
            </ul>
            <p>🏆 In Daily Challenge, compete for the best score!</p>
          </div>
        </div>
        </div>
      </div>
    </>
  );
}

export default Home;