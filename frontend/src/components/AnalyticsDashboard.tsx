import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChartContainer from './ChartContainer';
import TimeframeSelector, { Timeframe } from './TimeframeSelector';
import { createLineChartData, getDefaultLayout, formatPercentage } from '../utils/chartUtils';
import ExportButtons from './ExportButtons';

interface GlobalAnalytics {
  total_active_positions: number;
  total_countries: number;
  total_companies: number;
  total_managers: number;
  latest_data_date: string;
  positions_trend: Array<{
    date: string;
    active_positions: number;
    total_value: number;
  }>;
  top_countries: Array<{
    country_name: string;
    country_flag: string;
    active_positions: number;
    total_value: number;
  }>;
  top_managers: Array<{
    manager_name: string;
    active_positions: number;
    total_value: number;
  }>;
}

const AnalyticsDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<GlobalAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe>('3m');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/analytics/global?timeframe=${selectedTimeframe}`);
        setAnalytics(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load global analytics');
        console.error('Error fetching global analytics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [selectedTimeframe]);

  const prepareTrendChartData = () => {
    if (!analytics?.positions_trend) return { data: [], layout: {} };

    const chartData = analytics.positions_trend.map(day => ({
      date: day.date,
      value: day.active_positions
    }));

    const data = createLineChartData(chartData);
    const layout = getDefaultLayout(
      'Active Positions Trend',
      'Number of Active Positions'
    );

    return { data, layout };
  };

  const prepareTopCountriesChartData = () => {
    if (!analytics?.top_countries) return { data: [], layout: {} };

    const chartData = analytics.top_countries.slice(0, 10).map(country => ({
      x: `${country.country_flag} ${country.country_name}`,
      y: country.active_positions,
      type: 'bar' as const,
      marker: {
        color: '#10B981'
      }
    }));

    const data = chartData;
    const layout = {
      ...getDefaultLayout('Top Countries by Active Positions', 'Number of Active Positions'),
      xaxis: {
        ...getDefaultLayout('', '').xaxis,
        title: 'Country',
        tickangle: -45
      }
    };

    return { data, layout };
  };

  const prepareTopManagersChartData = () => {
    if (!analytics?.top_managers) return { data: [], layout: {} };

    const chartData = analytics.top_managers.slice(0, 10).map(manager => ({
      x: manager.manager_name,
      y: manager.active_positions,
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
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-red-800 mb-2">Error</h2>
        <p className="text-red-600">{error || 'Failed to load analytics'}</p>
      </div>
    );
  }

  const trendData = prepareTrendChartData();
  const topCountriesData = prepareTopCountriesChartData();
  const topManagersData = prepareTopManagersChartData();

  return (
    <div className="space-y-6">
      {/* Timeframe Selector */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Timeframe</h2>
        <TimeframeSelector
          selectedTimeframe={selectedTimeframe}
          onTimeframeChange={setSelectedTimeframe}
        />
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {analytics.total_active_positions.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Active Positions</div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {analytics.total_countries}
            </div>
            <div className="text-sm text-gray-600">Countries</div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">
              {analytics.total_companies.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Companies</div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">
              {analytics.total_managers.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Managers</div>
          </div>
        </div>
      </div>

      {/* Trend Chart */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Active Positions Trend Over Time</h2>
          <ExportButtons
            data={analytics.positions_trend.map((point: any) => ({
              Date: new Date(point.date).toLocaleDateString(),
              'Active Positions': point.active_positions,
              'Total Value (%)': formatPercentage(point.total_value)
            }))}
            headers={['Date', 'Active Positions', 'Total Value (%)']}
            filename="global_trend_data"
          />
        </div>
        <ChartContainer
          data={trendData.data}
          layout={trendData.layout}
          title=""
          loading={loading}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Top Countries by Active Positions</h2>
            <ExportButtons
              data={analytics.top_countries.slice(0, 10).map((country: any) => ({
                Country: country.country_name,
                'Active Positions': country.active_positions,
                'Total Value (%)': formatPercentage(country.total_value)
              }))}
              headers={['Country', 'Active Positions', 'Total Value (%)']}
              filename="top_countries_chart"
            />
          </div>
          <ChartContainer
            data={topCountriesData.data}
            layout={topCountriesData.layout}
            title=""
            loading={loading}
          />
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Top Managers by Active Positions</h2>
            <ExportButtons
              data={analytics.top_managers.slice(0, 10).map((manager: any) => ({
                Manager: manager.manager_name,
                'Active Positions': manager.active_positions,
                'Total Value (%)': formatPercentage(manager.total_value)
              }))}
              headers={['Manager', 'Active Positions', 'Total Value (%)']}
              filename="top_managers_chart"
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
        {/* Top Countries Table */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Countries</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Country
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
                {analytics.top_countries.slice(0, 10).map((country, index) => (
                  <tr key={index} className="">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      <span className="mr-2">{country.country_flag}</span>
                      {country.country_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="font-medium text-green-600">
                        {country.active_positions}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatPercentage(country.total_value)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Managers Table */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Managers</h2>
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
                        {manager.active_positions}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatPercentage(manager.total_value)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Last Updated */}
      <div className="bg-gray-50 rounded-lg p-4 text-center">
        <p className="text-sm text-gray-600">
          Last updated: {new Date(analytics.latest_data_date).toLocaleDateString('en-GB', {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </p>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
