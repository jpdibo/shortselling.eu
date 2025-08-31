import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import ReactCountryFlag from 'react-country-flag';
import { formatPercentage } from '../utils/chartUtils';
import ExportButtons from '../components/ExportButtons';

interface Position {
  company_name: string;
  country_name: string;
  country_flag: string;
  country_code: string;
  position_size: number;
  disclosure_date: string;
  exit_date?: string;
}

interface ManagerAnalytics {
  manager: {
    id: number;
    name: string;
    slug: string;
  };
  current_active_positions: Position[];
  historical_positions: Position[];
  countries: string[];
}

const ManagerPage: React.FC = () => {
  const { managerSlug } = useParams<{ managerSlug: string }>();
  const [analytics, setAnalytics] = useState<ManagerAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Country filters
  const [activeCountryFilter, setActiveCountryFilter] = useState<string>('');
  const [historicalCountryFilter, setHistoricalCountryFilter] = useState<string>('');

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!managerSlug) return;
      
      try {
        setLoading(true);
        const response = await axios.get(`/api/analytics/managers/${managerSlug}?timeframe=3m`);
        setAnalytics(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load manager analytics');
        console.error('Error fetching manager analytics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [managerSlug]);

  // Filter functions
  const getFilteredActivePositions = () => {
    if (!analytics) return [];
    if (!activeCountryFilter) return analytics.current_active_positions;
    return analytics.current_active_positions.filter(pos => pos.country_name === activeCountryFilter);
  };

  const getFilteredHistoricalPositions = () => {
    if (!analytics) return [];
    if (!historicalCountryFilter) return analytics.historical_positions;
    return analytics.historical_positions.filter(pos => pos.country_name === historicalCountryFilter);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-red-800 mb-2">Error</h2>
            <p className="text-red-600">{error || 'Manager not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  const filteredActivePositions = getFilteredActivePositions();
  const filteredHistoricalPositions = getFilteredHistoricalPositions();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900">{analytics.manager.name}</h1>
        </div>

        {/* Current Active Positions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Current Active Positions ({filteredActivePositions.length})
              </h2>
              <ExportButtons
                data={filteredActivePositions.map(position => ({
                  Company: position.company_name,
                  Country: position.country_name,
                  'Position Size (%)': formatPercentage(position.position_size),
                  'Disclosure Date': new Date(position.disclosure_date).toLocaleDateString()
                }))}
                headers={['Company', 'Country', 'Position Size (%)', 'Disclosure Date']}
                filename={`${analytics.manager.name}_active_positions`}
              />
            </div>
            
            {/* Country Filter for Active Positions - only show if there are positions */}
            {analytics.current_active_positions.length > 0 && (
              <div className="flex items-center space-x-2">
                <label htmlFor="active-country" className="text-sm text-gray-600">Filter by country:</label>
                <select
                  id="active-country"
                  value={activeCountryFilter}
                  onChange={(e) => setActiveCountryFilter(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">All Countries</option>
                  {analytics.countries.map(country => (
                    <option key={country} value={country}>{country}</option>
                  ))}
                </select>
              </div>
            )}
          </div>
          
          {analytics.current_active_positions.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">No Active Positions</p>
            </div>
          ) : filteredActivePositions.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">No active positions in {activeCountryFilter}</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Country
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Position Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Disclosure Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredActivePositions.map((position, index) => (
                    <tr key={index} className="">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        <div className="flex items-center gap-2">
                          {position.country_code && (
                            <ReactCountryFlag
                              countryCode={position.country_code}
                              svg
                              title={position.country_name}
                              style={{ width: '1.25em', height: '1.25em' }}
                            />
                          )}
                          {position.company_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex items-center gap-2">
                          {position.country_code && (
                            <ReactCountryFlag
                              countryCode={position.country_code}
                              svg
                              title={position.country_name}
                              style={{ width: '1.25em', height: '1.25em' }}
                            />
                          )}
                          {position.country_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className="font-medium text-red-600">
                          {formatPercentage(position.position_size)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(position.disclosure_date).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Historical Positions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Historical Positions ({filteredHistoricalPositions.length})
              </h2>
              <ExportButtons
                data={filteredHistoricalPositions.map(position => ({
                  Company: position.company_name,
                  Country: position.country_name,
                  'Position Size (%)': formatPercentage(position.position_size),
                  'Disclosure Date': new Date(position.disclosure_date).toLocaleDateString(),
                  'Exit Date': position.exit_date ? new Date(position.exit_date).toLocaleDateString() : 'N/A'
                }))}
                headers={['Company', 'Country', 'Position Size (%)', 'Disclosure Date', 'Exit Date']}
                filename={`${analytics.manager.name}_historical_positions`}
              />
            </div>
            
            {/* Country Filter for Historical Positions - only show if there are positions */}
            {analytics.historical_positions.length > 0 && (
              <div className="flex items-center space-x-2">
                <label htmlFor="historical-country" className="text-sm text-gray-600">Filter by country:</label>
                <select
                  id="historical-country"
                  value={historicalCountryFilter}
                  onChange={(e) => setHistoricalCountryFilter(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">All Countries</option>
                  {analytics.countries.map(country => (
                    <option key={country} value={country}>{country}</option>
                  ))}
                </select>
              </div>
            )}
          </div>
          
          {analytics.historical_positions.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">No Historical Positions</p>
            </div>
          ) : filteredHistoricalPositions.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">No historical positions in {historicalCountryFilter}</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Country
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Position Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Disclosure Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Exit Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredHistoricalPositions.map((position, index) => (
                    <tr key={index} className="">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        <div className="flex items-center gap-2">
                          {position.country_code && (
                            <ReactCountryFlag
                              countryCode={position.country_code}
                              svg
                              title={position.country_name}
                              style={{ width: '1.25em', height: '1.25em' }}
                            />
                          )}
                          {position.company_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex items-center gap-2">
                          {position.country_code && (
                            <ReactCountryFlag
                              countryCode={position.country_code}
                              svg
                              title={position.country_name}
                              style={{ width: '1.25em', height: '1.25em' }}
                            />
                          )}
                          {position.country_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className="font-medium text-gray-600">
                          {formatPercentage(position.position_size)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(position.disclosure_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(position.exit_date!).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ManagerPage;
