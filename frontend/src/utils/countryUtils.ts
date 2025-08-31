// Country name to flag emoji mapping
const COUNTRY_FLAGS: { [key: string]: string } = {
  // European countries in the system
  'United Kingdom': '🇬🇧',
  'Germany': '🇩🇪',
  'France': '🇫🇷',
  'Spain': '🇪🇸',
  'Italy': '🇮🇹',
  'Netherlands': '🇳🇱',
  'Belgium': '🇧🇪',
  'Sweden': '🇸🇪',
  'Denmark': '🇩🇰',
  'Norway': '🇳🇴',
  'Finland': '🇫🇮',
  'Ireland': '🇮🇪',
  
  // Additional European countries that might appear
  'Austria': '🇦🇹',
  'Switzerland': '🇨🇭',
  'Poland': '🇵🇱',
  'Portugal': '🇵🇹',
  'Czech Republic': '🇨🇿',
  'Hungary': '🇭🇺',
  'Romania': '🇷🇴',
  'Bulgaria': '🇧🇬',
  'Croatia': '🇭🇷',
  'Slovenia': '🇸🇮',
  'Slovakia': '🇸🇰',
  'Lithuania': '🇱🇹',
  'Latvia': '🇱🇻',
  'Estonia': '🇪🇪',
  'Luxembourg': '🇱🇺',
  'Malta': '🇲🇹',
  'Cyprus': '🇨🇾',
  'Greece': '🇬🇷',
  'Iceland': '🇮🇸',
  'Liechtenstein': '🇱🇮',
  'Monaco': '🇲🇨',
  'San Marino': '🇸🇲',
  'Vatican City': '🇻🇦',
  'Andorra': '🇦🇩'
};

/**
 * Get the flag emoji for a country name
 * @param countryName The full country name (e.g., "United Kingdom", "Germany")
 * @returns Flag emoji or empty string if not found
 */
export const getCountryFlag = (countryName: string): string => {
  return COUNTRY_FLAGS[countryName] || '';
};

/**
 * Format country display with flag + name
 * @param countryName The country name
 * @returns Formatted string like "🇩🇪 Germany" or just "Germany" if no flag found
 */
export const formatCountryDisplay = (countryName: string): string => {
  const flag = getCountryFlag(countryName);
  return flag ? `${flag} ${countryName}` : countryName;
};

/**
 * Get just the flag emoji for display in tables
 * Falls back to country code if no flag emoji found
 * @param countryName The country name  
 * @param countryCode Optional country code as fallback
 * @returns Flag emoji or country code
 */
export const getCountryDisplayFlag = (countryName: string, countryCode?: string): string => {
  const flag = getCountryFlag(countryName);
  return flag || countryCode || '🏳️';
};