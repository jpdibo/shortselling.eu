import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import ReactCountryFlag from 'react-country-flag';
import ChartContainer from '../components/ChartContainer';
import TimeframeSelector, { Timeframe } from '../components/TimeframeSelector';
import { createStackedBarChartData, getStackedBarLayout, formatPercentage } from '../utils/chartUtils';
import ExportButtons from '../components/ExportButtons';

interface CompanyAnalytics {
  company: {
    id: number;
    name: string;
    isin_code?: string;
    country: {
      code: string;
      name: string;
      flag: string;
    };
  };
  positions_over_time: Array<{
    date: string;
    total_position: number;
    manager_positions: Array<{
      manager_name: string;
      position_size: number;
    }>;
  }>;
}

const CompanyPage: React.FC = () => {
  const { companyId, companyName } = useParams<{ companyId?: string; companyName?: string }>();
  const [analytics, setAnalytics] = useState<CompanyAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe>('3m');

  useEffect(() => {
    const fetchAnalytics = async () => {
      const identifier = companyId || companyName;
      if (!identifier) return;
      
      try {
        setLoading(true);
        let url: string;
        
        if (companyId && !isNaN(parseInt(companyId))) {
          // Route: /company/:companyId (numeric ID)
          url = `/api/analytics/companies/${companyId}?timeframe=${selectedTimeframe}`;
        } else {
          // Route: /:companyName (company name)
          const nameParam = companyName || companyId;
          url = `/api/analytics/companies/by-name/${encodeURIComponent(nameParam!)}?timeframe=${selectedTimeframe}`;
        }
        
        const response = await axios.get(url);
        setAnalytics(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load company analytics');
        console.error('Error fetching company analytics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [companyId, companyName, selectedTimeframe]);

  const prepareChartData = () => {
    if (!analytics?.positions_over_time) return { data: [], layout: {} };

    const data = createStackedBarChartData(analytics.positions_over_time);
    const layout = getStackedBarLayout(
      '',  // No chart title
      'Short Positions as % of Total Shares'
    );

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
            <p className="text-red-600">{error || 'Company not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  const { data, layout } = prepareChartData();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header and Chart Combined */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <ReactCountryFlag
              countryCode={analytics.company.country.code}
              svg
              title={analytics.company.country.name}
              style={{ width: '2rem', height: '2rem' }}
            />
            <h1 className="text-3xl font-bold text-gray-900">{analytics.company.name}</h1>
          </div>
          
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Short Positions in {analytics.company.name} over time</h2>
            <div className="flex items-center gap-4">
              <TimeframeSelector
                selectedTimeframe={selectedTimeframe}
                onTimeframeChange={setSelectedTimeframe}
              />
              <ExportButtons
              data={analytics.positions_over_time.map(position => {
                const exportData: any = {
                  Date: new Date(position.date).toLocaleDateString(),
                  'Total Position (%)': formatPercentage(position.total_position)
                };
                
                // Add individual manager positions
                position.manager_positions.forEach(managerPos => {
                  exportData[`${managerPos.manager_name} (%)`] = formatPercentage(managerPos.position_size);
                });
                
                return exportData;
              })}
              headers={[
                'Date', 
                'Total Position (%)',
                ...Array.from(new Set(analytics.positions_over_time.flatMap(pos => 
                  pos.manager_positions.map(mp => mp.manager_name)
                ))).map(name => `${name} (%)`)
              ]}
              filename={`${analytics.company.name}_short_positions_${selectedTimeframe}`}
            />
            </div>
          </div>
          <ChartContainer
            data={data}
            layout={layout}
            title=""
            loading={loading}
            className=""
          />
        </div>

      </div>
    </div>
  );
};

export default CompanyPage;
