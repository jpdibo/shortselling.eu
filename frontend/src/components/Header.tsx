import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { MagnifyingGlassIcon, Bars3Icon } from '@heroicons/react/24/outline';
import SearchBar from './SearchBar';

const Header: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showCountryMenu, setShowCountryMenu] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState('all');

  const countries = [
    { code: 'all', name: '🌍 All European Countries' },
    { code: 'BE', name: '🇧🇪 Belgium' },
    { code: 'DK', name: '🇩🇰 Denmark' },
    { code: 'FI', name: '🇫🇮 Finland' },
    { code: 'FR', name: '🇫🇷 France' },
    { code: 'DE', name: '🇩🇪 Germany' },
    { code: 'IE', name: '🇮🇪 Ireland' },
    { code: 'IT', name: '🇮🇹 Italy' },
    { code: 'NL', name: '🇳🇱 Netherlands' },
    { code: 'NO', name: '🇳🇴 Norway' },
    { code: 'ES', name: '🇪🇸 Spain' },
    { code: 'SE', name: '🇸🇪 Sweden' },
    { code: 'UK', name: '🇬🇧 UK' },
  ];

  const handleCountrySelect = (countryCode: string) => {
    setSelectedCountry(countryCode);
    setShowCountryMenu(false);
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50" style={{boxShadow: '0 1px 0 0 rgba(0,0,0,0.06)'}}>
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <img 
              src="/logo-bear.png" 
              alt="ShortSelling.eu" 
              className="w-auto object-contain"
              style={{height: 'calc(80px * 1.2)'}}
            />
          </Link>

          {/* Right side - Search and Country Menu */}
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3">
                <MagnifyingGlassIcon className="h-4 w-4 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search companies or managers…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-80 h-10 pl-10 pr-4 text-sm border border-gray-200 rounded-lg bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-transparent"
              />
            </div>

            {/* Country Menu */}
            <div className="relative">
              <button
                onClick={() => setShowCountryMenu(!showCountryMenu)}
                className="flex items-center space-x-2 h-10 px-4 text-sm border border-gray-200 rounded-lg bg-white text-gray-900 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-transparent"
              >
                <Bars3Icon className="h-4 w-4" />
                <span>Countries</span>
              </button>

              {showCountryMenu && (
                <div className="absolute right-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                  <div className="py-2 max-h-80 overflow-y-auto">
                    {countries.map((country) => (
                      <button
                        key={country.code}
                        onClick={() => handleCountrySelect(country.code)}
                        className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-50 ${
                          selectedCountry === country.code ? 'bg-blue-50 text-blue-700' : 'text-gray-900'
                        }`}
                      >
                        {country.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;