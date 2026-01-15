import { useState, useEffect, useRef } from 'react';
import { searchPlayers } from '../services/api';
import PlayerCard from './PlayerCard';
import { formatPosition } from '../utils/positionMap';

/**
 * PlayerSelector - Search and select a player for guessing
 */
function PlayerSelector({ onSelect, onSubmit, disabled = false }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const searchTimeoutRef = useRef(null);
  const dropdownRef = useRef(null);

  // Handle search with debounce
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    const query = searchQuery.trim();
    
    if (query.length < 2) {
      setPlayers([]);
      setShowDropdown(false);
      return;
    }
    
    setLoading(true);
    searchTimeoutRef.current = setTimeout(async () => {
      try {
        const results = await searchPlayers(query);
        setPlayers(results);
        setShowDropdown(true);
      } catch (error) {
        console.error('Error searching players:', error);
        setPlayers([]);
      } finally {
        setLoading(false);
      }
    }, 300); // 300ms debounce

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSelect = (player) => {
    console.log('PlayerSelector: handleSelect called with:', player);
    setSelectedPlayer(player);
    setSearchQuery(player.name);
    setShowDropdown(false);
    setPlayers([]);
    
    // If onSubmit is provided, immediately submit (don't show preview)
    if (onSubmit) {
      console.log('PlayerSelector: Calling onSubmit callback immediately');
      onSubmit(player);
    } else if (onSelect) {
      // Otherwise, just select (shows preview)
      console.log('PlayerSelector: Calling onSelect callback');
      onSelect(player);
    } else {
      console.warn('PlayerSelector: No callback provided!');
    }
  };

  const handleClear = () => {
    setSelectedPlayer(null);
    setSearchQuery('');
    setPlayers([]);
    setShowDropdown(false);
    if (onSelect) {
      onSelect(null);
    }
  };

  return (
    <div className="w-full relative" ref={dropdownRef}>
      <div className="relative">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setSelectedPlayer(null);
            if (onSelect) {
              onSelect(null); // Clear parent selection too
            }
          }}
          placeholder="Search for a player..."
          disabled={disabled}
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg text-base focus:outline-none focus:border-[#00ff85] disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        {loading && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-[#00ff85]"></div>
          </div>
        )}
        {selectedPlayer && !disabled && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        )}
      </div>

      {/* Dropdown Results */}
      {showDropdown && players.length > 0 && (
        <div className="absolute z-50 w-full mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl max-h-96 overflow-y-auto">
          {players.map((player) => (
            <div
              key={player.id}
              onClick={() => handleSelect(player)}
              className="p-3 hover:bg-[#38003c]/15 cursor-pointer border-b border-gray-100 last:border-b-0 transition-colors"
            >
              <div className="flex items-center gap-3">
                {player.photo_url ? (
                  <img
                    src={player.photo_url}
                    alt={player.name}
                    className="w-12 h-12 rounded object-cover"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/48?text=No+Photo';
                    }}
                  />
                ) : (
                  <div className="w-12 h-12 rounded bg-gray-200 flex items-center justify-center text-gray-400 text-xs">
                    No Photo
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-gray-800 truncate">{player.name}</div>
                  <div className="text-sm text-gray-600 truncate">
                    {player.club} • {formatPosition(player.position)} • {player.nationality}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showDropdown && searchQuery.trim().length >= 2 && !loading && players.length === 0 && (
        <div className="absolute z-50 w-full mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl p-4 text-center text-gray-500">
          No players found
        </div>
      )}

      {/* Selected Player Preview - Only show if onSubmit is NOT provided (preview mode) */}
      {selectedPlayer && !onSubmit && (
        <div className="mt-4">
          <div className="text-sm font-medium text-white mb-2">Selected Player:</div>
          <PlayerCard player={selectedPlayer} size="small" />
        </div>
      )}
    </div>
  );
}

export default PlayerSelector;
