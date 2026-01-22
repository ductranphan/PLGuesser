import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getLeaderboard, getMyRank, getMyStats } from '../services/api';

function Leaderboard() {
  const { user, isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(true);
  const [leaderboard, setLeaderboard] = useState([]);
  const [error, setError] = useState('');
  const [myStats, setMyStats] = useState(null);
  const [myRank, setMyRank] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchLeaderboard = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await getLeaderboard('win_rate', 100);
        if (isMounted) {
          setLeaderboard(data);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to load leaderboard.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchLeaderboard();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;
    const fetchMyStats = async () => {
      if (!isAuthenticated) {
        setMyStats(null);
        setMyRank(null);
        return;
      }
      try {
        const [stats, rank] = await Promise.all([
          getMyStats(),
          getMyRank('win_rate')
        ]);
        if (isMounted) {
          setMyStats(stats);
          setMyRank(rank);
        }
      } catch (err) {
        if (isMounted) {
          setMyStats(null);
          setMyRank(null);
        }
      }
    };

    fetchMyStats();
    return () => {
      isMounted = false;
    };
  }, [isAuthenticated]);

  return (
    <div className="min-h-screen bg-[#28002a] rounded-lg shadow-md border-2 border-[#2D1B69] py-10 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white">Leaderboard</h1>
            <p className="text-gray-200 mt-2">See the top PLGuesser performers.</p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/game"
              className="px-4 py-2 bg-[#38003c] text-white rounded-lg hover:bg-[#200020] transition-colors font-semibold"
            >
              Back to Game
            </Link>
            {!isAuthenticated && (
              <Link
                to="/login"
                className="px-4 py-2 bg-[#00ff85] text-black rounded-lg hover:bg-[#00e676] transition-colors font-semibold"
              >
                Log in
              </Link>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <h2 className="text-xl font-bold text-gray-900">Global Rankings</h2>
            <span className="text-sm text-gray-500">Sorted by win rate</span>
          </div>

          {loading ? (
            <div className="py-8 text-center text-gray-500">Loading leaderboard...</div>
          ) : error ? (
            <div className="py-6 text-center text-red-600">{error}</div>
          ) : leaderboard.length === 0 ? (
            <div className="py-6 text-center text-gray-500">No players on the leaderboard yet.</div>
          ) : (
            <div className="overflow-x-auto mt-4">
              <table className="min-w-full text-sm text-left">
                <thead className="text-gray-700 border-b">
                  <tr>
                    <th className="py-3 pr-4">Rank</th>
                    <th className="py-3 pr-4">Player</th>
                    <th className="py-3 pr-4">Win %</th>
                    <th className="py-3 pr-4">Wins</th>
                    <th className="py-3 pr-4">Games</th>
                    <th className="py-3 pr-4">Best Streak</th>
                    <th className="py-3 pr-4">Avg Guesses</th>
                  </tr>
                </thead>
                <tbody>
                  {leaderboard.map((entry) => {
                    const isMe = user && entry.username === user.username;
                    return (
                      <tr
                        key={entry.user_id}
                        className={`border-b ${isMe ? 'bg-[#00ff85]/20' : 'bg-white'}`}
                      >
                        <td className="py-3 pr-4 font-semibold">{entry.rank}</td>
                        <td className="py-3 pr-4 font-medium">{entry.username}</td>
                        <td className="py-3 pr-4">{entry.win_percentage}%</td>
                        <td className="py-3 pr-4">{entry.total_wins}</td>
                        <td className="py-3 pr-4">{entry.total_games_played}</td>
                        <td className="py-3 pr-4">{entry.best_win_streak}</td>
                        <td className="py-3 pr-4">
                          {entry.average_guesses ? entry.average_guesses.toFixed(1) : '-'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {isAuthenticated ? (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Your Stats</h2>
            {myStats ? (
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="border-2 border-gray-200 rounded-lg p-4">
                  <div className="text-xs text-gray-500 mb-1">Games Played</div>
                  <div className="text-2xl font-bold text-gray-900">{myStats.total_games_played}</div>
                </div>
                <div className="border-2 border-gray-200 rounded-lg p-4">
                  <div className="text-xs text-gray-500 mb-1">Win Rate</div>
                  <div className="text-2xl font-bold text-gray-900">{myStats.win_percentage}%</div>
                </div>
                <div className="border-2 border-gray-200 rounded-lg p-4">
                  <div className="text-xs text-gray-500 mb-1">Best Streak</div>
                  <div className="text-2xl font-bold text-gray-900">{myStats.best_win_streak}</div>
                </div>
                <div className="border-2 border-gray-200 rounded-lg p-4">
                  <div className="text-xs text-gray-500 mb-1">Avg Guesses</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {myStats.average_guesses ? myStats.average_guesses.toFixed(1) : '-'}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-sm text-gray-500">Play a daily challenge to see stats.</div>
            )}

            {myRank && (
              <div className="mt-4 text-sm text-gray-600">
                {myRank.rank
                  ? `Your rank: #${myRank.rank} of ${myRank.total_players} players`
                  : 'Play at least one daily challenge to receive a rank.'}
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-lg p-6 text-gray-700">
            <p>Log in to see your personal rank and stats.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Leaderboard;
