import React, { useState } from 'react';
import CountrySelector from '../components/CountrySelector';
import LatestPositions from '../components/LatestPositions';
import AnimatedTagline from '../components/AnimatedTagline';

const HomePage: React.FC = () => {
  const [loading] = useState(false);
  
  // Subscription form state
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [frequency, setFrequency] = useState('daily');
  const [country, setCountry] = useState('all');

  // Define the 12 countries with data as specified
  const countriesWithData = [
    { id: 1, code: 'GB', name: 'United Kingdom', priority: 'high', url: '', is_active: true },
    { id: 2, code: 'DE', name: 'Germany', priority: 'high', url: '', is_active: true },
    { id: 3, code: 'FR', name: 'France', priority: 'high', url: '', is_active: true },
    { id: 4, code: 'SE', name: 'Sweden', priority: 'high', url: '', is_active: true },
    { id: 5, code: 'IT', name: 'Italy', priority: 'high', url: '', is_active: true },
    { id: 6, code: 'NO', name: 'Norway', priority: 'high', url: '', is_active: true },
    { id: 7, code: 'NL', name: 'Netherlands', priority: 'high', url: '', is_active: true },
    { id: 8, code: 'ES', name: 'Spain', priority: 'high', url: '', is_active: true },
    { id: 9, code: 'FI', name: 'Finland', priority: 'high', url: '', is_active: true },
    { id: 10, code: 'DK', name: 'Denmark', priority: 'high', url: '', is_active: true },
    { id: 11, code: 'BE', name: 'Belgium', priority: 'high', url: '', is_active: true },
    { id: 12, code: 'IE', name: 'Ireland', priority: 'high', url: '', is_active: true }
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="responsive-container max-w-7xl mx-auto py-4 sm:py-6 lg:py-8">
      {/* Animated Tagline */}
      <div className="mb-6 sm:mb-8 lg:mb-10">
        <div className="bg-white rounded-xl p-4 sm:p-6 lg:p-8 shadow-lg border border-gray-200">
          <AnimatedTagline 
            text="Track and analyze short-selling positions across Europe. Get real-time insights into the main market events."
            speed={30}
            className="font-mono"
          />
        </div>
      </div>

      {/* Country Selector with Top Companies and Managers */}
      <div className="mb-8 sm:mb-12">
        <CountrySelector countries={countriesWithData} />
      </div>

      {/* Latest Positions */}
      <div className="mb-8 sm:mb-12">
        <h2 className="tech-heading text-xl sm:text-2xl text-gray-900 mb-4 sm:mb-6">
          Latest Short Positions
        </h2>
        <LatestPositions />
      </div>

      {/* Subscription Form */}
      <div className="mb-8 sm:mb-12">
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Subscribe to Short Selling Updates
          </h3>
          <p className="text-gray-600 mb-6">
            Get the latest short selling positions delivered to your inbox.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="sub-frequency" className="block text-sm font-medium text-gray-700 mb-1">
                Frequency
              </label>
              <select
                id="sub-frequency"
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
                className="w-full h-10 px-3 text-sm border border-gray-300 rounded-md bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="sub-country" className="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <select
                id="sub-country"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="w-full h-10 px-3 text-sm border border-gray-300 rounded-md bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              >
                <option value="all">All European Countries</option>
                <option value="BE">Belgium</option>
                <option value="DK">Denmark</option>
                <option value="FI">Finland</option>
                <option value="FR">France</option>
                <option value="DE">Germany</option>
                <option value="IE">Ireland</option>
                <option value="IT">Italy</option>
                <option value="NL">Netherlands</option>
                <option value="NO">Norway</option>
                <option value="ES">Spain</option>
                <option value="SE">Sweden</option>
                <option value="UK">UK</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <input
              type="text"
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="h-10 px-3 text-sm border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              required
            />
            
            <input
              type="email"
              placeholder="Your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-10 px-3 text-sm border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              required
            />
          </div>
          
          <button
            onClick={() => {
              console.log('Subscribe:', { name, email, frequency, country });
              setName('');
              setEmail('');
            }}
            className="w-full md:w-auto bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2"
          >
            Subscribe to Updates
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
