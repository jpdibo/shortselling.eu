import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import ReactCountryFlag from 'react-country-flag';
import ExportButtons from './ExportButtons';

interface Country {
  id: number;
  code: string;
  name: string;
  priority: string;
  url: string;
  is_active: boolean;
}

interface TopCompany {
  company_name: string;
  company_id: number;
  total_short_positions: number;
  average_position_size: number;
  position_count: number;
  week_delta: number;
  most_recent_position_date: string;
}

interface TopManager {
  name: string;
  slug: string;
  active_positions: number;
  total_exposure: number;
}

interface CountrySelectorProps {
  countries: Country[];
}

const CountrySelector: React.FC<CountrySelectorProps> = ({ countries }) => {
  const [selectedCountry, setSelectedCountry] = useState<string>('all');
  const [topCompanies, setTopCompanies] = useState<TopCompany[]>([]);
  const [topManagers, setTopManagers] = useState<TopManager[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchGlobalData = useCallback(async () => {
    try {
      // Fetch global top companies
      const companiesResponse = await fetch('/api/analytics/global/top-companies');
      const companiesData = await companiesResponse.json();
      setTopCompanies(companiesData.slice(0, 10)); // Top 10

      // Fetch global top managers
      const managersResponse = await fetch('/api/analytics/global/top-managers');
      const managersData = await managersResponse.json();
      setTopManagers(managersData.slice(0, 10)); // Top 10
    } catch (error) {
      console.error('Error fetching global data:', error);
    }
  }, []);

  const fetchCountryData = useCallback(async (countryCode: string) => {
    try {
      // Fetch top companies
      const companiesResponse = await fetch(`/api/countries/${countryCode}/most-shorted`);
      const companiesData = await companiesResponse.json();
      setTopCompanies(companiesData.slice(0, 10)); // Top 10

      // Fetch top managers
      const managersResponse = await fetch(`/api/countries/${countryCode}/top-managers`);
      const managersData = await managersResponse.json();
      setTopManagers(managersData.slice(0, 10)); // Top 10
    } catch (error) {
      console.error('Error fetching country data:', error);
    }
  }, []);

  const fetchTopData = useCallback(async (countryCode: string) => {
    setLoading(true);
    try {
      if (countryCode === 'all') {
        // Use global endpoints for all European countries
        await fetchGlobalData();
      } else {
        await fetchCountryData(countryCode);
      }
    } catch (error) {
      console.error('Error fetching top data:', error);
    } finally {
      setLoading(false);
    }
  }, [fetchGlobalData, fetchCountryData]);

  useEffect(() => {
    if (selectedCountry) {
      fetchTopData(selectedCountry);
    }
  }, [selectedCountry, fetchTopData]);

  const getCountryDisplayName = (countryCode: string) => {
    if (countryCode === 'all') return 'All European Countries';
    const country = countries.find(c => c.code === countryCode);
    return country ? country.name : countryCode;
  };

  const formatWeekDelta = (delta: number) => {
    if (delta > 0) {
      return `+${delta.toFixed(2)}%`;
    } else if (delta < 0) {
      return `${delta.toFixed(2)}%`;
    }
    return '0.00%';
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const getDeltaColor = (delta: number) => {
    if (delta > 0) return 'text-green-600';
    if (delta < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="tech-container rounded-lg p-4 sm:p-6">
      <div className="mb-4 sm:mb-6">
        <h2 className="tech-heading text-xl sm:text-2xl text-gray-900 mb-3 sm:mb-4">Select Country</h2>
        
        {/* Country Buttons */}
        <div className="flex flex-wrap gap-2 sm:gap-3 mb-4 sm:mb-6">
          <button
            onClick={() => setSelectedCountry('all')}
            className={`px-3 sm:px-4 py-2 rounded-lg font-medium transition-colors duration-200 text-sm sm:text-base ${
              selectedCountry === 'all'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            🌍 All European Countries
          </button>
          
          {countries.map((country) => (
            <button
              key={country.code}
              onClick={() => setSelectedCountry(country.code)}
              className={`px-3 sm:px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-1 sm:gap-2 text-sm sm:text-base ${
                selectedCountry === country.code
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <ReactCountryFlag
                countryCode={country.code}
                svg
                title={country.name}
                style={{ width: '1.25em', height: '1.25em' }}
              />
              {country.name}
            </button>
          ))}
        </div>

        {/* Selected Country Display */}
        <div className="mb-4 sm:mb-6">
          <h3 className="tech-heading text-lg sm:text-xl text-gray-900">
            {getCountryDisplayName(selectedCountry)}
          </h3>
        </div>
      </div>

      {/* Data Tables */}
      {loading ? (
        <div className="flex justify-center items-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
          {/* Top Companies Table */}
          <div className="tech-container rounded-lg p-4 sm:p-6">
            <div className="flex justify-between items-center mb-3 sm:mb-4">
              <h3 className="tech-heading text-base sm:text-lg text-gray-900">
                Most Shorted Companies
              </h3>
              <ExportButtons
                data={topCompanies.map(company => ({
                  Company: company.company_name,
                  'Total Disclosed Positions (%)': company.total_short_positions.toFixed(2),
                  'Positions': company.position_count || 0,
                  'Week Delta': formatWeekDelta(company.week_delta),
                  'Position Date': formatDate(company.most_recent_position_date)
                }))}
                headers={['Company', 'Total Disclosed Positions (%)', 'Positions', 'Week Delta', 'Position Date']}
                filename={`most_shorted_companies_${selectedCountry}`}
              />
            </div>
            <div className="responsive-table">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-1 sm:px-2 font-medium text-gray-700 text-sm sm:text-base">Company</th>
                    <th className="text-right py-2 px-1 sm:px-2 font-medium text-gray-700 text-sm sm:text-base">Total Disclosed Positions</th>
                    <th className="text-right py-2 px-1 sm:px-2 font-medium text-gray-700 text-sm sm:text-base">Positions</th>
                    <th className="text-right py-2 px-1 sm:px-2 font-medium text-gray-700 text-sm sm:text-base">Week Δ</th>
                    <th className="text-right py-2 px-1 sm:px-2 font-medium text-gray-700 text-sm sm:text-base">Position Date</th>
                  </tr>
                </thead>
                <tbody>
                  {topCompanies.map((company, index) => (
                    <tr key={company.company_id} className="border-b border-gray-100">
                      <td className="py-2 px-1 sm:px-2 text-sm sm:text-base">
                        <Link 
                          to={`/company/${company.company_id}`}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          {company.company_name}
                        </Link>
                      </td>
                      <td className="py-2 px-1 sm:px-2 text-right text-gray-700 font-semibold text-sm sm:text-base">
                        {company.total_short_positions.toFixed(2)}%
                      </td>
                      <td className="py-2 px-1 sm:px-2 text-right text-gray-700 text-sm sm:text-base">
                        {company.position_count || 0}
                      </td>
                      <td className={`py-2 px-1 sm:px-2 text-right font-semibold text-sm sm:text-base ${getDeltaColor(company.week_delta)}`}>
                        {formatWeekDelta(company.week_delta)}
                      </td>
                      <td className="py-2 px-1 sm:px-2 text-right text-gray-700 text-sm sm:text-base">
                        {formatDate(company.most_recent_position_date)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Top Managers Table */}
          <div className="tech-container rounded-lg p-4 sm:p-6">
            <div className="flex justify-between items-center mb-3 sm:mb-4">
              <h3 className="tech-heading text-base sm:text-lg text-gray-900">
                Managers with Most Active Positions
              </h3>
              <ExportButtons
                data={topManagers.map((manager, index) => ({
                  Rank: `#${index + 1}`,
                  Manager: manager.name,
                  'Active Positions Disclosed': manager.active_positions
                }))}
                headers={['Rank', 'Manager', 'Active Positions Disclosed']}
                filename={`top_managers_${selectedCountry}`}
              />
            </div>
            <div className="responsive-table">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-1 sm:px-2 font-medium text-gray-700 text-sm sm:text-base">Rank</th>
                    <th className="text-left py-2 px-1 sm:px-2 font-medium text-gray-700 text-sm sm:text-base">Manager</th>
                    <th className="text-right py-2 px-1 sm:px-2 font-medium text-gray-700 text-sm sm:text-base">Active Positions Disclosed</th>
                  </tr>
                </thead>
                <tbody>
                  {topManagers.map((manager, index) => (
                    <tr key={manager.slug} className="border-b border-gray-100">
                      <td className="py-2 px-1 sm:px-2 text-center text-gray-700 font-semibold text-sm sm:text-base">
                        #{index + 1}
                      </td>
                      <td className="py-2 px-1 sm:px-2 text-sm sm:text-base">
                        <Link 
                          to={`/manager/${manager.slug}`}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          {manager.name}
                        </Link>
                      </td>
                      <td className="py-2 px-1 sm:px-2 text-right text-gray-700 font-semibold text-sm sm:text-base">
                        {manager.active_positions}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CountrySelector;
