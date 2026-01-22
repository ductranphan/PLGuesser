// PlayerCard import removed - we only show photo and name now
import { formatPosition } from '../utils/positionMap';

/**
 * GuessRow - Displays a single guess with color-coded hints
 */
function GuessRow({ guess, targetPlayer = null, guessNumber = null }) {
  if (!guess || !guess.guessed_player || !guess.hints) return null;

  const { guessed_player, hints } = guess;
  const isCorrect = targetPlayer && guess.guessed_player.id === targetPlayer.id;

  // Helper function to get hint color classes
  const getHintColor = (result) => {
    switch (result) {
      case 'correct':
        return 'bg-[#00ff85] text-white';
      case 'close':
        return 'bg-yellow-500 text-white';
      case 'incorrect':
        return 'bg-red-500 text-white';
      default:
        return 'bg-gray-300 text-gray-700';
    }
  };

  // Helper function to get hint icon (no icon for incorrect, only for correct)
  const getHintIcon = (result) => {
    switch (result) {
      case 'correct':
        return '✓';
      case 'close':
        return ''; // No icon for close (arrows will show instead)
      case 'incorrect':
        return ''; // No icon for incorrect (arrows will show instead)
      default:
        return '';
    }
  };

  // Helper function to get comparison arrow (for numerical values)
  const getComparisonArrow = (hint) => {
    // Don't show arrows when correct
    if (!hint || hint.result === 'correct') {
      return null;
    }
    
    // Check if hint has comparison direction
    if (hint.direction === 'higher') return '↑'; // Target is higher
    if (hint.direction === 'lower') return '↓'; // Target is lower
    
    // Fallback: if we have both values, calculate direction
    if (hint.value !== undefined && hint.target !== undefined) {
      const guess = Number(hint.value);
      const target = Number(hint.target);
      
      if (!isNaN(guess) && !isNaN(target)) {
        if (guess < target) return '↑';
        if (guess > target) return '↓';
      }
    }
    return null;
  };

  return (
    <div className={`bg-[#28002a] rounded-lg shadow-md border-2 p-4 backdrop-blur-sm transition-all duration-200 hover:border-[#00ff85] hover:shadow-lg hover:shadow-[#00ff85]/20 ${
      isCorrect ? 'border-[#00ff85] ring-2 ring-[#00ff85]/30' : 'border-[#38003c]'
    }`}>
      {/* Guess Number Header */}
      {guessNumber !== null && (
        <div className="mb-3 pb-2 border-b border-[#38003c]">
          <span className="text-sm font-semibold text-[#00ff85]">Guess #{guessNumber}</span>
        </div>
      )}
      
      {/* Player Photo and Name Only */}
      <div className="mb-4 flex items-center gap-3">
        {guessed_player.photo_url ? (
          <img
            src={guessed_player.photo_url}
            alt={guessed_player.name}
            className="w-16 h-16 rounded-lg object-cover bg-gray-100"
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/64?text=No+Photo';
            }}
          />
        ) : (
          <div className="w-16 h-16 rounded-lg bg-gray-800 flex items-center justify-center text-gray-400 text-xs">
            No Photo
          </div>
        )}
        <h3 className="text-lg font-bold text-white">{guessed_player.name}</h3>
      </div>

      {isCorrect && (
        <div className="mb-4 p-3 bg-[#00ff85]/20 border border-[#00ff85] rounded-lg text-center">
          <span className="text-green-800 font-bold text-lg">🎉 Correct Guess! 🎉</span>
        </div>
      )}

      {/* Hints Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Name */}
        <HintCell
          label="Name"
          value={hints.name?.value || guessed_player.name}
          result={hints.name?.result}
          icon={getHintIcon(hints.name?.result)}
          colorClass={getHintColor(hints.name?.result)}
        />

        {/* Nationality */}
        <HintCell
          label="Nationality"
          value={hints.nationality?.value || guessed_player.nationality}
          result={hints.nationality?.result}
          icon={getHintIcon(hints.nationality?.result)}
          colorClass={getHintColor(hints.nationality?.result)}
        />

        {/* Club */}
        <HintCell
          label="Club"
          value={hints.club?.value || guessed_player.club}
          result={hints.club?.result}
          icon={getHintIcon(hints.club?.result)}
          colorClass={getHintColor(hints.club?.result)}
        />

        {/* Position */}
        <HintCell
          label="Position"
          value={formatPosition(hints.position?.value || guessed_player.position)}
          result={hints.position?.result}
          icon={getHintIcon(hints.position?.result)}
          colorClass={getHintColor(hints.position?.result)}
        />

        {/* Age */}
        <HintCell
          label="Age"
          value={hints.age?.value !== undefined ? hints.age.value : guessed_player.age}
          result={hints.age?.result}
          icon={getHintIcon(hints.age?.result)}
          colorClass={getHintColor(hints.age?.result)}
          arrow={getComparisonArrow(hints.age)}
        />

        {/* Height */}
        <HintCell
          label="Height (cm)"
          value={hints.height?.value !== undefined ? hints.height.value : guessed_player.height}
          result={hints.height?.result}
          icon={getHintIcon(hints.height?.result)}
          colorClass={getHintColor(hints.height?.result)}
          arrow={getComparisonArrow(hints.height)}
        />

        {/* Goal Contribution */}
        <HintCell
          label="Goal Contribution"
          value={hints.goal_contribution?.value !== undefined ? hints.goal_contribution.value : guessed_player.goal_contribution}
          result={hints.goal_contribution?.result}
          icon={getHintIcon(hints.goal_contribution?.result)}
          colorClass={getHintColor(hints.goal_contribution?.result)}
          arrow={getComparisonArrow(hints.goal_contribution)}
        />

        {/* Number */}
        <HintCell
          label="Number"
          value={hints.number?.value !== undefined ? hints.number.value : guessed_player.number}
          result={hints.number?.result}
          icon={getHintIcon(hints.number?.result)}
          colorClass={getHintColor(hints.number?.result)}
          arrow={getComparisonArrow(hints.number)}
        />
      </div>

      {/* Legend */}
      <div className="mt-4 pt-3 border-t border-[#38003c] flex flex-wrap gap-3 text-xs">
        <div className="flex items-center gap-1">
          <span className="w-4 h-4 rounded bg-[#00ff85]"></span>
          <span className="text-white">Correct</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-4 h-4 rounded bg-yellow-500"></span>
          <span className="text-white">Close</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-4 h-4 rounded bg-red-500"></span>
          <span className="text-white">Incorrect</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-white">↑ Higher</span>
          <span className="text-white">↓ Lower</span>
        </div>
      </div>
    </div>
  );
}

// Helper component for hint cells
function HintCell({ label, value, result, icon, colorClass, arrow }) {
  return (
    <div className="flex flex-col">
      <div className="text-xs font-medium text-white mb-1">{label}</div>
      <div className={`flex items-center justify-center gap-1 px-3 py-2 rounded-lg font-semibold ${colorClass}`}>
        {icon && <span>{icon}</span>}
        <span>{value}</span>
        {arrow && <span className="ml-1">{arrow}</span>}
      </div>
    </div>
  );
}

export default GuessRow;
