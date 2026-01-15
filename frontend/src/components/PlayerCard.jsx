import { formatPosition } from '../utils/positionMap';

/**
 * PlayerCard - Displays a player's information in a card format
 */
function PlayerCard({ player, size = 'normal' }) {
  if (!player) return null;

  const sizeClasses = {
    small: 'p-3 text-sm',
    normal: 'p-4',
    large: 'p-6 text-lg'
  };

  return (
    <div className={`bg-[#28002a] rounded-lg shadow-md border-2 border-[#2D1B69] backdrop-blur-sm ${sizeClasses[size]}`}>
      <div className="flex items-start gap-4">
        {/* Player Photo */}
        {player.photo_url ? (
          <img
            src={player.photo_url}
            alt={player.name}
            className={`rounded-lg object-cover bg-gray-100 ${
              size === 'small' ? 'w-16 h-16' : size === 'large' ? 'w-24 h-24' : 'w-20 h-20'
            }`}
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/100?text=No+Photo';
            }}
          />
        ) : (
          <div className={`rounded-lg bg-gray-800 flex items-center justify-center text-gray-400 ${
            size === 'small' ? 'w-16 h-16 text-xs' : size === 'large' ? 'w-24 h-24' : 'w-20 h-20'
          }`}>
            No Photo
          </div>
        )}

        {/* Player Info */}
        <div className="flex-1 min-w-0">
          <h3 className={`font-bold text-white truncate ${
            size === 'small' ? 'text-sm' : size === 'large' ? 'text-xl' : 'text-base'
          }`}>
            {player.name}
          </h3>
          <div className={`mt-2 space-y-1 text-white ${
            size === 'small' ? 'text-xs' : 'text-sm'
          }`}>
            <div className="flex items-center gap-2">
              <span className="font-medium">Club:</span>
              <span className="truncate">{player.club}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-medium">Nationality:</span>
              <span>{player.nationality}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-medium">Position:</span>
              <span className="px-2 py-0.5 bg-[#38003c]/30 text-[#00ff85] rounded text-xs font-medium">
                {formatPosition(player.position)}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <span>Age: <strong>{player.age}</strong></span>
              <span>Height: <strong>{player.height}cm</strong></span>
              {player.number && <span>#{player.number}</span>}
            </div>
            <div className="flex items-center gap-2">
              <span className="font-medium">Goal Contribution:</span>
              <span className="font-semibold text-[#00ff85]">{player.goal_contribution}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PlayerCard;
