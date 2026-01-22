import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { createFreePlayGame, startDailyChallenge, submitGuess, getGameById, getPlayerById, getUserStats } from '../services/api';
import PlayerSelector from './PlayerSelector';
import GuessRow from './GuessRow';
import PlayerCard from './PlayerCard';

const MAX_GUESSES = 6;

/**
 * GameBoard - Main game interface
 */
function GameBoard() {
  const { user, logout, isAuthenticated } = useAuth();
  const [game, setGame] = useState(null);
  const [targetPlayer, setTargetPlayer] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [selectorKey, setSelectorKey] = useState(0);
  const [showInstructions, setShowInstructions] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(false);

  // Create or load game on mount
  useEffect(() => {
    initializeGame();
  }, []);

  // If user logs out, start a fresh guest game
  useEffect(() => {
    if (!isAuthenticated && game?.user_id) {
      setGame(null);
      setTargetPlayer(null);
      setSelectedPlayer(null);
      setError('');
      initializeGame();
    }
  }, [isAuthenticated, game?.user_id]);

  // If user logs in, start/resume daily challenge
  useEffect(() => {
    if (isAuthenticated && game && game.user_id === null) {
      setGame(null);
      setTargetPlayer(null);
      setSelectedPlayer(null);
      setError('');
      initializeGame();
    }
  }, [isAuthenticated, game]);

  // Debug logging - must be before any conditional returns
  useEffect(() => {
    if (game) {
      const currentGuesses = game.guesses || game.game_data?.guesses || [];
      console.log('=== GAME STATE UPDATE (useEffect) ===');
      console.log('Game ID:', game.id);
      console.log('Game status:', game.game_status);
      console.log('game.guesses:', game.guesses);
      console.log('game.guesses type:', typeof game.guesses);
      console.log('game.guesses length:', game.guesses?.length);
      console.log('game.game_data?.guesses:', game.game_data?.guesses);
      console.log('game.game_data?.guesses type:', typeof game.game_data?.guesses);
      console.log('game.game_data?.guesses length:', game.game_data?.guesses?.length);
      console.log('currentGuesses (computed):', currentGuesses);
      console.log('guessesCount:', currentGuesses.length);
      console.log('Full game object keys:', Object.keys(game));
      console.log('selectedPlayer:', selectedPlayer?.name);
      console.log('=====================================');
    }
  }, [game, selectedPlayer]);

  const initializeGame = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Log to help debug
      console.log('Creating new game...');
      const newGame = isAuthenticated ? await startDailyChallenge() : await createFreePlayGame();
      console.log('Game created:', newGame);
      
      if (!newGame) {
        throw new Error('Game creation returned null');
      }
      
      setGame(newGame);
      
      // Fetch target player if game is won/lost (reveal the answer)
      if (newGame.game_status === 'won' || newGame.game_status === 'lost') {
        const secretPlayerId = newGame.game_data?.secret_player_id;
        if (secretPlayerId) {
          try {
            const target = await getPlayerById(secretPlayerId);
            setTargetPlayer(target);
          } catch (err) {
            console.error('Error fetching target player:', err);
          }
        }
      }
    } catch (err) {
      console.error('Error creating game:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response,
        data: err.response?.data,
        status: err.response?.status
      });
      
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Failed to start game. Please check your connection and try again.';
      
      setError(errorMessage);
      setGame(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlayer = useCallback((player) => {
    console.log('GameBoard: handleSelectPlayer called with:', player);
    if (player) {
      console.log('GameBoard: Setting selectedPlayer to:', player.name);
      setSelectedPlayer(player);
      setError('');
    } else {
      console.log('GameBoard: Clearing selectedPlayer');
      setSelectedPlayer(null);
    }
  }, []);

  const handleSubmitGuess = async (player = null) => {
    // Use provided player or selectedPlayer
    const playerToGuess = player || selectedPlayer;
    
    if (!playerToGuess) {
      setError('Please select a player');
      return;
    }

    if (!game) {
      setError('No active game');
      return;
    }

    if (game.game_status !== 'in_progress') {
      setError('Game is already finished');
      return;
    }

    try {
      setSubmitting(true);
      setError('');
      console.log('Submitting guess:', { gameId: game.id, playerId: playerToGuess.id });
      
      const updatedGame = await submitGuess(game.id, playerToGuess.id);
      console.log('=== API RESPONSE ===');
      console.log('Full response:', JSON.stringify(updatedGame, null, 2));
      console.log('Updated game guesses:', updatedGame.guesses);
      console.log('Updated game guesses type:', typeof updatedGame.guesses);
      console.log('Updated game guesses length:', updatedGame.guesses?.length);
      console.log('Updated game status:', updatedGame.game_status);
      console.log('Updated game game_data:', updatedGame.game_data);
      console.log('Game data guesses:', updatedGame.game_data?.guesses);
      console.log('Current game guesses (before update):', game.guesses);
      console.log('Current game guesses length:', game.guesses?.length);
      
      if (!updatedGame) {
        throw new Error('No game data returned from server');
      }
      
      // Ensure guesses are properly formatted - check multiple sources
      const responseGuesses = updatedGame.guesses || updatedGame.game_data?.guesses || [];
      console.log('Extracted guesses from response:', responseGuesses);
      console.log('Extracted guesses length:', responseGuesses.length);
      
      const formattedGame = {
        ...updatedGame,
        guesses: responseGuesses
      };
      
      console.log('=== BEFORE STATE UPDATE ===');
      console.log('Old game:', game);
      console.log('Old guesses count:', game.guesses?.length || 0);
      console.log('New formatted game:', formattedGame);
      console.log('New guesses count:', formattedGame.guesses?.length || 0);
      
      // Force re-render by creating a new game object
      setGame(formattedGame);
      
      console.log('=== AFTER STATE UPDATE ===');
      console.log('State should now have guesses:', formattedGame.guesses?.length || 0);
      
      setSelectedPlayer(null);
      
      // Reset PlayerSelector by changing key
      setSelectorKey(prev => prev + 1);
      
      // Clear any errors
      setError('');

      // If game ended, fetch target player to reveal the answer and refresh stats
      if (updatedGame.game_status === 'won' || updatedGame.game_status === 'lost') {
        const secretPlayerId = updatedGame.game_data?.secret_player_id;
        if (secretPlayerId) {
          try {
            const target = await getPlayerById(secretPlayerId);
            setTargetPlayer(target);
          } catch (err) {
            console.error('Error fetching target player:', err);
          }
        }
        
        // Refresh stats when game ends (only if logged in)
        if (isAuthenticated) {
          try {
            const statsData = await getUserStats();
            setStats(statsData);
          } catch (err) {
            console.error('Error refreshing stats:', err);
          }
        }
      }
    } catch (err) {
      console.error('Error submitting guess:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response,
        data: err.response?.data,
        status: err.response?.status,
        stack: err.stack
      });
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to submit guess';
      console.error('Setting error message:', errorMessage);
      setError(errorMessage);
      // Also show a visible alert for debugging
      alert(`Error: ${errorMessage}\n\nCheck console (F12) for details.`);
    } finally {
      setSubmitting(false);
      console.log('Submit finished, submitting state set to false');
    }
  };

  const handleNewGame = async () => {
    setGame(null);
    setTargetPlayer(null);
    setSelectedPlayer(null);
    setError('');
    await initializeGame();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#28002a] flex items-center justify-center">
        <div className="text-white text-xl">Loading game...</div>
      </div>
    );
  }

  if (!game && !loading && error) {
    return (
      <div className="min-h-screen bg-[#28002a] flex items-center justify-center p-4">
        <div className="bg-[#28002a] rounded-lg shadow-md border-2 border-[#2D1B69] p-8 max-w-md w-full">
          <h2 className="text-2xl font-bold text-[#00ff85] mb-4">Failed to Load Game</h2>
          <div className="bg-red-100 border-2 border-red-400 text-red-700 px-4 py-3 rounded-lg mb-4">
            <p className="font-semibold mb-2">Error:</p>
            <p>{error}</p>
          </div>
          
          {error.includes('No players found') || error.includes('seed') ? (
            <div className="bg-yellow-100 border-2 border-yellow-400 text-yellow-800 px-4 py-3 rounded-lg mb-4">
              <p className="font-semibold mb-2">Solution:</p>
              <p className="text-sm mb-2">You need to seed players in your database first.</p>
              <p className="text-sm">Run: <code className="bg-gray-200 px-2 py-1 rounded">python backend/scripts/seed_players.py</code></p>
            </div>
          ) : error.includes('Network') || error.includes('connection') || error.includes('Failed to fetch') ? (
            <div className="bg-yellow-100 border-2 border-yellow-400 text-yellow-800 px-4 py-3 rounded-lg mb-4">
              <p className="font-semibold mb-2">Solution:</p>
              <p className="text-sm mb-2">Make sure your backend server is running.</p>
              <p className="text-sm">Run: <code className="bg-gray-200 px-2 py-1 rounded">cd backend && python main.py</code></p>
            </div>
          ) : null}
          
          <button
            onClick={initializeGame}
            className="w-full py-3 bg-[#38003c] text-white rounded-lg hover:bg-[#200020] transition-colors font-semibold mt-4"
          >
            Try Again
          </button>
          
          {isAuthenticated && (
            <button
              onClick={logout}
              className="w-full py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-semibold mt-2"
            >
              Logout
            </button>
          )}
        </div>
      </div>
    );
  }

  if (!game) {
    return null;
  }

  const guesses = game.guesses || game.game_data?.guesses || [];
  const guessesRemaining = MAX_GUESSES - guesses.length;
  const isGameOver = game.game_status === 'won' || game.game_status === 'lost';

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-[#28002a] rounded-lg shadow-md border-2 border-[#2D1B69] p-6 mb-6 backdrop-blur-sm">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-[#00ff85]">PLGuesser</h1>
              <Link
                to="/"
                className="px-3 py-1.5 bg-[#38003c] text-white rounded-lg hover:bg-[#200020] transition-colors text-sm font-medium"
                title="Home"
              >
                Home
              </Link>
            </div>
            <div className="flex items-center gap-4">
              {isAuthenticated ? (
                <>
                  <span className="text-white">Welcome, <strong className="text-[#00ff85]">{user?.username}</strong></span>
                  <button
                    onClick={logout}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <span className="text-white">Playing as <strong className="text-[#00ff85]">Guest</strong></span>
              )}
            </div>
          </div>

          {/* Game Status */}
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-white mb-1">Guesses Remaining</div>
              <div className="text-2xl font-bold text-[#00ff85]">{guessesRemaining} / {MAX_GUESSES}</div>
            </div>
            <div className="text-right flex items-end gap-3">
              <div>
                <div className={`text-lg font-semibold ${
                  game.game_status === 'won' ? 'text-[#00ff85]' :
                  game.game_status === 'lost' ? 'text-red-400' :
                  'text-[#00ff85]'
                }`}>
                  {game.game_status === 'won' ? '🎉 Won!' :
                   game.game_status === 'lost' ? '💀 Lost' :
                   'In Progress'}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowInstructions(true)}
                  className="px-3 py-1.5 bg-[#38003c] text-white rounded-lg hover:bg-[#200020] transition-colors text-sm font-medium"
                  title="How to Play"
                >
                  ?
                </button>
                <Link
                  to="/leaderboard"
                  className="px-3 py-1.5 bg-[#38003c] text-white rounded-lg hover:bg-[#200020] transition-colors text-sm font-medium"
                  title="Leaderboard"
                >
                  🏆
                </Link>
                {!isAuthenticated && (
                  <Link
                    to="/login"
                    className="px-3 py-1.5 bg-[#00ff85] text-black rounded-lg hover:bg-[#00e676] transition-colors text-sm font-medium"
                    title="Log in"
                  >
                    Log in
                  </Link>
                )}
                {isAuthenticated && (
                  <button
                    onClick={async () => {
                      setShowStats(true);
                      setLoadingStats(true);
                      try {
                        // Always fetch fresh stats when opening the modal
                        const statsData = await getUserStats();
                        setStats(statsData);
                      } catch (err) {
                        console.error('Error fetching stats:', err);
                        setError('Failed to load stats');
                      } finally {
                        setLoadingStats(false);
                      }
                    }}
                    className="px-3 py-1.5 rounded-lg transition-colors text-sm font-medium bg-[#38003c] text-white hover:bg-[#200020]"
                    title="View Stats"
                  >
                    📊
                  </button>
                )}
              </div>
            </div>
            {isGameOver && (
              isAuthenticated ? (
                <div className="px-4 py-2 text-sm text-white bg-[#2D1B69]/40 border border-[#2D1B69] rounded-lg">
                  Come back tomorrow
                </div>
              ) : (
                <button
                  onClick={handleNewGame}
                  className="px-6 py-2 bg-[#38003c] text-white rounded-lg hover:bg-[#200020] transition-colors font-semibold"
                >
                  New Game
                </button>
              )
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border-2 border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Previous Guesses */}
        <div className="space-y-4 mb-6">
          {guesses && guesses.length > 0 && (
            <>
              {console.log('Rendering guesses:', guesses, 'Count:', guesses.length)}
              {guesses.map((guess, index) => {
                console.log(`Rendering guess ${index}:`, guess);
                return (
                  <GuessRow
                    key={`guess-${index}-${guess.guessed_player_id || index}`}
                    guess={guess}
                    targetPlayer={targetPlayer}
                    guessNumber={index + 1}
                  />
                );
              })}
            </>
          )}
        </div>

        {/* Player Selector (only show if game in progress) */}
        {!isGameOver && (
          <div className="bg-[#28002a] rounded-lg shadow-md border-2 border-[#2D1B69] p-6 mb-6">
            <div className="mb-4 pb-3 border-b border-[#38003c]">
              <span className="text-sm font-semibold text-[#00ff85]">Guess #{guesses.length + 1}</span>
            </div>
            <h2 className="text-xl font-bold text-[#00ff85] mb-4">Make Your Guess</h2>
            <PlayerSelector
              key={selectorKey}
              onSubmit={handleSubmitGuess}
              disabled={submitting || isGameOver}
            />
            
            {submitting && (
              <div className="mt-4 text-center">
                <div className="inline-flex items-center gap-2 text-[#00ff85]">
                  <span className="animate-spin rounded-full h-5 w-5 border-b-2 border-[#00ff85]"></span>
                  <span className="font-semibold">Submitting guess...</span>
                </div>
              </div>
            )}
            
            <div className="mt-4 text-sm text-white text-center">
              Click on a player from the dropdown to submit your guess
            </div>
          </div>
        )}

        {/* Target Player Reveal (when game is over) */}
        {isGameOver && targetPlayer && (
          <div className="bg-[#28002a] rounded-lg shadow-md border-2 border-[#2D1B69] p-6">
            <h2 className="text-2xl font-bold text-[#00ff85] mb-4 text-center">
              {game.game_status === 'won' ? '🎉 You Got It! 🎉' : 'The Answer Was:'}
            </h2>
            <PlayerCard player={targetPlayer} size="large" />
          </div>
        )}

        {/* Empty Guess Rows (visual guide) */}
        {!isGameOver && guesses.length < MAX_GUESSES && (
          <div className="space-y-4">
            {Array.from({ length: MAX_GUESSES - guesses.length }).map((_, index) => {
              // Skip the first empty box since "Make Your Guess" shows that number
              if (index === 0) {
                return null;
              }
              return (
                <div
                  key={`empty-${index}`}
                  className="bg-[#28002a] rounded-lg shadow-md border-2 border-dashed border-[#2D1B69] p-8 opacity-50"
                >
                  <div className="text-center text-white">Guess {guesses.length + index + 1}</div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Instructions Modal */}
      {showInstructions && (
        <div 
          className="fixed inset-0 bg-[#0A0517] bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setShowInstructions(false)}
        >
          <div 
            className="bg-[#28002a] rounded-lg shadow-md border-2 border-[#2D1B69] p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold text-[#00ff85]">How to Play</h2>
              <button
                onClick={() => setShowInstructions(false)}
                className="text-white hover:text-[#00ff85] text-2xl font-bold transition-colors"
              >
                ×
              </button>
            </div>

            <div className="space-y-6 text-white">
              <div>
                <h3 className="text-xl font-bold text-[#00ff85] mb-2">Objective</h3>
                <p className="text-gray-300">
                  Guess the secret Premier League player in 6 tries or less! Each guess reveals hints about how close you are to the correct player.
                </p>
              </div>

              <div>
                <h3 className="text-xl font-bold text-[#00ff85] mb-2">How to Play</h3>
                <ol className="list-decimal list-inside space-y-2 text-gray-300">
                  <li>Type a <strong>player's LAST NAME</strong> in the search box to find and select them</li>
                  <li>Click on a player from the dropdown to submit your guess</li>
                  <li>PLayers are updated to <strong>2024-2025 PREMIER LEAGUE SEASON</strong> (summer transfer window)</li>
                  <li>Review the hints for each attribute</li>
                  <li>Win by guessing the correct player within 6 attempts!</li>
                </ol>
              </div>

              <div>
                <h3 className="text-xl font-bold text-[#00ff85] mb-2">Understanding the Hints</h3>
                <div className="space-y-3 text-gray-300">
                  <div className="flex items-start gap-3">
                    <span className="px-3 py-1 bg-green-500 text-white rounded font-semibold min-w-[80px] text-center">Green</span>
                    <span className="flex-1">The attribute is <strong>correct</strong> - matches the secret player exactly</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="px-3 py-1 bg-yellow-500 text-white rounded font-semibold min-w-[80px] text-center">Yellow</span>
                    <span className="flex-1">The attribute is <strong>close</strong> - similar but not exact (e.g., same club but different position)</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="px-3 py-1 bg-red-500 text-white rounded font-semibold min-w-[80px] text-center">Red</span>
                    <span className="flex-1">The attribute is <strong>incorrect</strong> - doesn't match the secret player</span>
                  </div>
                  <div className="flex items-start gap-3 mt-4">
                    <span className="text-[#00ff85] font-bold">↑ ↓</span>
                    <span className="flex-1">For numerical values (age, height, goal contribution, number), arrows show if the secret player's value is <strong>higher (↑)</strong> or <strong>lower (↓)</strong> than your guess</span>
                  </div>
                  <div className="text-xl font-bold text-[#00ff85] mb-2">
                    <span className="flex-1">Remember, <strong>NO CHEATING!</strong></span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-[#2D1B69]">
                <button
                  onClick={() => setShowInstructions(false)}
                  className="w-full py-3 bg-[#38003c] text-white rounded-lg hover:bg-[#200020] transition-colors font-semibold"
                >
                  Got it!
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Modal */}
      {showStats && (
        <div 
          className="fixed inset-0 bg-[#0A0517] bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setShowStats(false)}
        >
          <div 
            className="bg-[#28002a] rounded-lg shadow-md border-2 border-[#2D1B69] p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold text-[#00ff85]">Your Statistics</h2>
              <button
                onClick={() => setShowStats(false)}
                className="text-white hover:text-[#00ff85] text-2xl font-bold transition-colors"
              >
                ×
              </button>
            </div>

            {loadingStats ? (
              <div className="flex items-center justify-center py-12">
                <div className="inline-flex items-center gap-2 text-[#00ff85]">
                  <span className="animate-spin rounded-full h-6 w-6 border-b-2 border-[#00ff85]"></span>
                  <span className="font-semibold">Loading stats...</span>
                </div>
              </div>
            ) : stats ? (
              <div className="space-y-6 text-white">
                {/* Overall Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-[#38003c]/30 rounded-lg p-4 border border-[#2D1B69]">
                    <div className="text-sm text-gray-400 mb-1">Games Played</div>
                    <div className="text-2xl font-bold text-[#00ff85]">{stats.games_played}</div>
                  </div>
                  <div className="bg-[#00ff85]/20 rounded-lg p-4 border border-[#00ff85]/50">
                    <div className="text-sm text-gray-400 mb-1">Games Won</div>
                    <div className="text-2xl font-bold text-[#00ff85]">{stats.games_won}</div>
                  </div>
                  <div className="bg-red-500/20 rounded-lg p-4 border border-red-500/50">
                    <div className="text-sm text-gray-400 mb-1">Games Lost</div>
                    <div className="text-2xl font-bold text-red-400">{stats.games_lost}</div>
                  </div>
                  <div className="bg-[#38003c]/30 rounded-lg p-4 border border-[#2D1B69]">
                    <div className="text-sm text-gray-400 mb-1">Win Rate</div>
                    <div className="text-2xl font-bold text-[#00ff85]">
                      {stats.games_played > 0 ? (stats.win_rate * 100).toFixed(1) : 0}%
                    </div>
                  </div>
                </div>

                {/* Streaks */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-[#38003c]/30 rounded-lg p-4 border border-[#2D1B69]">
                    <div className="text-sm text-gray-400 mb-1">Current Streak</div>
                    <div className="text-3xl font-bold text-[#00ff85]">{stats.current_streak}</div>
                  </div>
                  <div className="bg-[#38003c]/30 rounded-lg p-4 border border-[#2D1B69]">
                    <div className="text-sm text-gray-400 mb-1">Best Streak</div>
                    <div className="text-3xl font-bold text-[#00ff85]">{stats.best_streak}</div>
                  </div>
                </div>

                {/* Average Guesses */}
                {stats.games_won > 0 && (
                  <div className="bg-[#38003c]/30 rounded-lg p-4 border border-[#2D1B69]">
                    <div className="text-sm text-gray-400 mb-1">Average Guesses (Wins)</div>
                    <div className="text-3xl font-bold text-[#00ff85]">
                      {stats.average_guesses.toFixed(1)}
                    </div>
                  </div>
                )}

                {/* Guess Distribution */}
                {stats.games_won > 0 && (
                  <div>
                    <h3 className="text-xl font-bold text-[#00ff85] mb-3">Guess Distribution</h3>
                    <div className="space-y-2">
                      {[1, 2, 3, 4, 5, 6].map((guessNum) => {
                        const count = stats.guess_distribution[guessNum] || 0;
                        const percentage = stats.games_won > 0 ? (count / stats.games_won) * 100 : 0;
                        return (
                          <div key={guessNum} className="flex items-center gap-3">
                            <div className="w-8 text-sm font-medium text-gray-400">{guessNum}</div>
                            <div className="flex-1 bg-[#38003c]/30 rounded-full h-6 overflow-hidden">
                              <div 
                                className="bg-[#00ff85] h-full rounded-full transition-all duration-300 flex items-center justify-end pr-2"
                                style={{ width: `${percentage}%` }}
                              >
                                {count > 0 && (
                                  <span className="text-xs font-semibold text-black">{count}</span>
                                )}
                              </div>
                            </div>
                            <div className="w-12 text-right text-sm text-gray-400">
                              {count > 0 ? count : '-'}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {stats.games_played === 0 && (
                  <div className="text-center py-8 text-gray-400">
                    <p className="text-lg mb-2">No games played yet!</p>
                    <p className="text-sm">Start playing to see your statistics here.</p>
                  </div>
                )}

                <div className="pt-4 border-t border-[#2D1B69]">
                  <button
                    onClick={() => setShowStats(false)}
                    className="w-full py-3 bg-[#38003c] text-white rounded-lg hover:bg-[#200020] transition-colors font-semibold"
                  >
                    Close
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <p>Failed to load statistics</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default GameBoard;
