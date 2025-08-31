import React from 'react';
import Plot from 'react-plotly.js';

interface ChartContainerProps {
  data: any[];
  layout: any;
  config?: any;
  title?: string;
  loading?: boolean;
  className?: string;
}

const ChartContainer: React.FC<ChartContainerProps> = ({
  data,
  layout,
  config = { displayModeBar: false },
  title,
  loading = false,
  className = ''
}) => {
  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      )}
      <div className="chart-container">
        <Plot
          data={data}
          layout={{
            ...layout,
            autosize: true,
            margin: { l: 50, r: 50, t: 50, b: 50 },
            font: { family: 'Inter, sans-serif' },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
          }}
          config={config}
          useResizeHandler={true}
          style={{ width: '100%', height: '400px' }}
        />
      </div>
    </div>
  );
};

export default ChartContainer;
