import React from 'react';
import { Link } from 'react-router-dom';

interface Country {
  id: number;
  code: string;
  name: string;
  flag: string;
  priority: string;
  url: string;
  is_active: boolean;
}

interface CountryCardProps {
  country: Country;
}

const CountryCard: React.FC<CountryCardProps> = ({ country }) => {
  return (
    <Link
      to={`/country/${country.code}`}
      className="country-card block bg-white rounded-lg shadow-md border border-gray-200 p-6"
    >
      <div className="flex items-center space-x-3 mb-4">
        <span className="text-2xl">{country.flag}</span>
        <h3 className="text-lg font-semibold text-gray-900">{country.name}</h3>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Country Code:</span>
          <span className="text-sm font-medium text-gray-900">{country.code}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Priority:</span>
          <span className={`text-sm font-medium px-2 py-1 rounded-full ${
            country.priority === 'high' 
              ? 'bg-red-100 text-red-800' 
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {country.priority}
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Status:</span>
          <span className={`text-sm font-medium px-2 py-1 rounded-full ${
            country.is_active 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {country.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-sm text-blue-600 hover:text-blue-700 font-medium">
          View Details →
        </div>
      </div>
    </Link>
  );
};

export default CountryCard;
