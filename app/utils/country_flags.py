"""
Country flag utilities for converting country codes/names to flag emojis
"""

# Country code to flag emoji mapping
COUNTRY_CODE_TO_FLAG = {
    'GB': '🇬🇧',  # United Kingdom
    'DE': '🇩🇪',  # Germany  
    'FR': '🇫🇷',  # France
    'ES': '🇪🇸',  # Spain
    'IT': '🇮🇹',  # Italy
    'NL': '🇳🇱',  # Netherlands
    'BE': '🇧🇪',  # Belgium
    'SE': '🇸🇪',  # Sweden
    'DK': '🇩🇰',  # Denmark
    'NO': '🇳🇴',  # Norway
    'FI': '🇫🇮',  # Finland
    'IE': '🇮🇪',  # Ireland
    'AT': '🇦🇹',  # Austria
    'CH': '🇨🇭',  # Switzerland
    'PL': '🇵🇱',  # Poland
    'PT': '🇵🇹',  # Portugal
    'CZ': '🇨🇿',  # Czech Republic
    'HU': '🇭🇺',  # Hungary
    'RO': '🇷🇴',  # Romania
    'BG': '🇧🇬',  # Bulgaria
    'HR': '🇭🇷',  # Croatia
    'SI': '🇸🇮',  # Slovenia
    'SK': '🇸🇰',  # Slovakia
    'LT': '🇱🇹',  # Lithuania
    'LV': '🇱🇻',  # Latvia
    'EE': '🇪🇪',  # Estonia
    'LU': '🇱🇺',  # Luxembourg
    'MT': '🇲🇹',  # Malta
    'CY': '🇨🇾',  # Cyprus
    'GR': '🇬🇷',  # Greece
    'IS': '🇮🇸',  # Iceland
}

# Country name to flag emoji mapping
COUNTRY_NAME_TO_FLAG = {
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
}


def get_flag_by_code(country_code: str) -> str:
    """Get flag emoji from country code (e.g., 'DE' -> '🇩🇪')"""
    return COUNTRY_CODE_TO_FLAG.get(country_code.upper(), country_code)


def get_flag_by_name(country_name: str) -> str:
    """Get flag emoji from country name (e.g., 'Germany' -> '🇩🇪')"""
    return COUNTRY_NAME_TO_FLAG.get(country_name, '🏳️')


def get_flag_emoji(country_code: str = None, country_name: str = None) -> str:
    """
    Get flag emoji from either country code or name
    Prefers code if both provided
    """
    if country_code:
        flag = get_flag_by_code(country_code)
        if flag != country_code:  # Found a flag emoji
            return flag
    
    if country_name:
        return get_flag_by_name(country_name)
    
    return '🏳️'  # Default flag