import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import ReactCountryFlag from 'react-country-flag';
import ChartContainer from '../components/ChartContainer';
import TimeframeSelector, { Timeframe } from '../components/TimeframeSelector';
import { getDefaultLayout, formatPercentage } from '../utils/chartUtils';
import ExportButtons from '../components/ExportButtons';

interface CountryAnalytics {
  country: {
    code: string;
    name: string;
    flag: string;
    priority: string;
    is_active: boolean;
  };
  most_shorted_companies: Array<{
    company_name: string;
    total_position: number;
    active_managers: number;
  }>;
  top_managers: Array<{
    manager_name: string;
    active_positions_count: number;
    total_position_value: number;
  }>;
  total_active_positions: number;
}

const CountryPage: React.FC = () => {
  const { countryCode } = useParams<{ countryCode: string }>();
  const [analytics, setAnalytics] = useState<CountryAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe>('3m');

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!countryCode) return;
      
      try {
        setLoading(true);
        const response = await axios.get(`/api/countries/${countryCode}/analytics?timeframe=${selectedTimeframe}`);
        setAnalytics(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load country analytics');
        console.error('Error fetching country analytics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [countryCode, selectedTimeframe]);

  const prepareMostShortedChartData = () => {
    if (!analytics?.most_shorted_companies) return { data: [], layout: {} };

    const chartData = analytics.most_shorted_companies.slice(0, 10).map(company => ({
      x: company.company_name,
      y: company.total_position,
      type: 'bar' as const,
      marker: {
        color: '#EF4444'
      }
    }));

    const data = chartData;
    const layout = {
      ...getDefaultLayout('Most Shorted Companies', 'Total Position (%)'),
      xaxis: {
        ...getDefaultLayout('', '').xaxis,
        title: 'Company',
        tickangle: -45
      }
    };

    return { data, layout };
  };

  const prepareTopManagersChartData = () => {
    if (!analytics?.top_managers) return { data: [], layout: {} };

    const chartData = analytics.top_managers.slice(0, 10).map(manager => ({
      x: manager.manager_name,
      y: manager.active_positions_count,
      type: 'bar' as const,
      marker: {
        color: '#3B82F6'
      }
    }));

    const data = chartData;
    const layout = {
      ...getDefaultLayout('Top Managers by Active Positions', 'Number of Active Positions'),
      xaxis: {
        ...getDefaultLayout('', '').xaxis,
        title: 'Manager',
        tickangle: -45
      }
    };

    return { data, layout };
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
            <p className="text-red-600">{error || 'Country not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  const mostShortedData = prepareMostShortedChartData();
  const topManagersData = prepareTopManagersChartData();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">{analytics.country.flag}</span>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{analytics.country.name}</h1>
              <p className="text-gray-600">Country Code: {analytics.country.code}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div>
              <span className="font-medium">Priority:</span> 
              <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                analytics.country.priority === 'High' 
                  ? 'bg-red-100 text-red-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {analytics.country.priority}
              </span>
            </div>
            <div>
              <span className="font-medium">Status:</span> 
              <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                analytics.country.is_active 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {analytics.country.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div>
              <span className="font-medium">Total Active Positions:</span> {analytics.total_active_positions}
            </div>
          </div>
        </div>

        {/* Timeframe Selector */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Timeframe</h2>
          <TimeframeSelector
            selectedTimeframe={selectedTimeframe}
            onTimeframeChange={setSelectedTimeframe}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Most Shorted Companies Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Most Shorted Companies</h2>
              <ExportButtons
                data={analytics.most_shorted_companies.slice(0, 10).map(company => ({
                  Company: company.company_name,
                  'Total Position (%)': formatPercentage(company.total_position),
                  'Active Managers': company.active_managers
                }))}
                headers={['Company', 'Total Position (%)', 'Active Managers']}
                filename={`${analytics.country.code}_most_shorted_chart`}
              />
            </div>
            <ChartContainer
              data={mostShortedData.data}
              layout={mostShortedData.layout}
              title=""
              loading={loading}
            />
          </div>

          {/* Top Managers Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Top Managers by Active Positions</h2>
              <ExportButtons
                data={analytics.top_managers.slice(0, 10).map(manager => ({
                  Manager: manager.manager_name,
                  'Active Positions': manager.active_positions_count,
                  'Total Value (%)': formatPercentage(manager.total_position_value)
                }))}
                headers={['Manager', 'Active Positions', 'Total Value (%)']}
                filename={`${analytics.country.code}_top_managers_chart`}
              />
            </div>
            <ChartContainer
              data={topManagersData.data}
              layout={topManagersData.layout}
              title=""
              loading={loading}
            />
          </div>
        </div>

        {/* Detailed Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Most Shorted Companies Table */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Most Shorted Companies</h2>
              <ExportButtons
                data={analytics.most_shorted_companies.slice(0, 10).map(company => ({
                  Company: company.company_name,
                  'Total Position (%)': formatPercentage(company.total_position),
                  'Active Managers': company.active_managers
                }))}
                headers={['Company', 'Total Position (%)', 'Active Managers']}
                filename={`${analytics.country.code}_most_shorted_companies`}
              />
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Position
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Active Managers
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {analytics.most_shorted_companies.slice(0, 10).map((company, index) => (
                    <tr key={index} className="">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        <div className="flex items-center gap-2">
                          <ReactCountryFlag
                            countryCode={analytics.country.code}
                            svg
                            title={analytics.country.name}
                            style={{ width: '1.25em', height: '1.25em' }}
                          />
                          {company.company_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className="font-medium text-red-600">
                          {formatPercentage(company.total_position)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {company.active_managers}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Top Managers Table */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Top Managers</h2>
              <ExportButtons
                data={analytics.top_managers.slice(0, 10).map(manager => ({
                  Manager: manager.manager_name,
                  'Active Positions': manager.active_positions_count,
                  'Total Value (%)': formatPercentage(manager.total_position_value)
                }))}
                headers={['Manager', 'Active Positions', 'Total Value (%)']}
                filename={`${analytics.country.code}_top_managers`}
              />
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Manager
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Active Positions
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Value
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {analytics.top_managers.slice(0, 10).map((manager, index) => (
                    <tr key={index} className="">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {manager.manager_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className="font-medium text-blue-600">
                          {manager.active_positions_count}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatPercentage(manager.total_position_value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CountryPage;
