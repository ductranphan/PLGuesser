/**
 * Maps position codes to full position names for display
 * @param {string} positionCode - The position code (e.g., "CM", "ST", "CB", "GK")
 * @returns {string} - The full position name (e.g., "Midfielder", "Attacker", "Defender", "Goalkeeper")
 */
export function formatPosition(positionCode) {
  if (!positionCode) return positionCode;

  const positionMap = {
    'CM': 'Midfielder',
    'ST': 'Attacker',
    'CB': 'Defender',
    'GK': 'Goalkeeper',
    // Handle case if full names are already stored
    'Midfielder': 'Midfielder',
    'Attacker': 'Attacker',
    'Defender': 'Defender',
    'Goalkeeper': 'Goalkeeper',
  };

  return positionMap[positionCode] || positionCode;
}
