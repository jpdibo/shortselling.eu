import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import ReactCountryFlag from 'react-country-flag';
import ExportButtons from './ExportButtons';

interface Position {
  id: number;
  date: string;
  company: string;
  company_id: number;
  manager: string;
  manager_slug: string;
  country: string;
  country_code: string;
  position_size: number;
  is_active: boolean;
}

const LatestPositions: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLatestPositions = async () => {
      try {
        const response = await fetch('/api/positions/latest?limit=10');
        const data = await response.json();
        setPositions(data);
      } catch (error) {
        console.error('Error fetching latest positions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLatestPositions();
  }, []);

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (positions.length === 0) {
    return (
      <div className="tech-container rounded-lg p-6">
        <p className="tech-body text-gray-600 text-center">No recent positions available</p>
      </div>
    );
  }

  return (
    <div className="tech-container rounded-lg overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h3 className="tech-heading text-lg text-gray-900">Latest Short Positions</h3>
          <ExportButtons
            data={positions.map(position => ({
              Date: formatDate(position.date),
              Company: position.company,
              Manager: position.manager,
              Country: position.country,
              'Position Size (%)': position.position_size.toFixed(2)
            }))}
            headers={['Date', 'Company', 'Manager', 'Country', 'Position Size (%)']}
            filename="latest_short_positions"
          />
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="position-table min-w-full">
          <thead>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Manager
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Country
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Position Size
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {positions.map((position) => (
              <tr key={position.id} className="">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(position.date)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  <Link
                    to={`/company/${position.company_id}`}
                    className="text-blue-600 hover:text-blue-700 flex items-center gap-2"
                  >
                    {position.country_code && (
                      <ReactCountryFlag
                        countryCode={position.country_code}
                        svg
                        title={position.country}
                        style={{ width: '1.25em', height: '1.25em' }}
                      />
                    )}
                    {position.company}
                  </Link>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <Link
                    to={`/manager/${position.manager_slug}`}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    {position.manager}
                  </Link>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div className="flex items-center gap-2">
                    {position.country_code && (
                      <ReactCountryFlag
                        countryCode={position.country_code}
                        svg
                        title={position.country}
                        style={{ width: '1.25em', height: '1.25em' }}
                      />
                    )}
                    {position.country}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {position.position_size.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="px-6 py-4 border-t border-gray-200">
        <Link
          to="/positions"
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          View all positions →
        </Link>
      </div>
    </div>
  );
};

export default LatestPositions;
