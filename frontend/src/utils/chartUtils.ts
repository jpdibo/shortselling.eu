// Color palette for charts - ensures managers are easily distinguishable
export const CHART_COLORS = [
  '#3B82F6', // Blue
  '#EF4444', // Red
  '#10B981', // Green
  '#F59E0B', // Yellow
  '#8B5CF6', // Purple
  '#F97316', // Orange
  '#06B6D4', // Cyan
  '#84CC16', // Lime
  '#EC4899', // Pink
  '#6366F1', // Indigo
  '#14B8A6', // Teal
  '#F43F5E', // Rose
  '#A855F7', // Violet
  '#22C55E', // Emerald
  '#EAB308', // Amber
  '#0EA5E9', // Sky
  '#06B6D4', // Cyan
];

export const getChartColor = (index: number): string => {
  return CHART_COLORS[index % CHART_COLORS.length];
};

export const formatPercentage = (value: number): string => {
  return `${value.toFixed(2)}%`;
};

export const formatDate = (dateString: string, compact: boolean = false): string => {
  const date = new Date(dateString);
  
  if (compact) {
    // More compact format for charts with many data points
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: '2-digit'
    });
  }
  
  return date.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  });
};

export const formatDateForChart = (dateString: string, totalDates: number): string => {
  // Use compact format if we have many dates to prevent overlap
  const useCompact = totalDates > 15;
  return formatDate(dateString, useCompact);
};

export const createBarChartData = (
  data: Array<{ date: string; value: number; manager?: string }>,
  managers?: string[]
) => {
  if (managers && managers.length > 0) {
    // Multiple managers - create grouped bar chart
    const traces = managers.map((manager, index) => {
      const managerData = data.filter(d => d.manager === manager);
      return {
        x: managerData.map(d => formatDateForChart(d.date, data.length)),
        y: managerData.map(d => d.value),
        name: manager,
        type: 'bar' as const,
        marker: {
          color: getChartColor(index)
        }
      };
    });

    return traces;
  } else {
    // Single series
    return [{
      x: data.map(d => formatDateForChart(d.date, data.length)),
      y: data.map(d => d.value),
      type: 'bar' as const,
      marker: {
        color: getChartColor(0)
      }
    }];
  }
};

export const createLineChartData = (
  data: Array<{ date: string; value: number; manager?: string }>,
  managers?: string[]
) => {
  if (managers && managers.length > 0) {
    // Multiple managers - create multiple line traces
    const traces = managers.map((manager, index) => {
      const managerData = data.filter(d => d.manager === manager);
      return {
        x: managerData.map(d => formatDateForChart(d.date, data.length)),
        y: managerData.map(d => d.value),
        name: manager,
        type: 'scatter' as const,
        mode: 'lines+markers' as const,
        line: {
          color: getChartColor(index),
          width: 2
        },
        marker: {
          color: getChartColor(index),
          size: 6
        }
      };
    });

    return traces;
  } else {
    // Single series
    return [{
      x: data.map(d => formatDateForChart(d.date, data.length)),
      y: data.map(d => d.value),
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      line: {
        color: getChartColor(0),
        width: 2
      },
      marker: {
        color: getChartColor(0),
        size: 6
      }
    }];
  }
};

export const createStackedBarChartData = (
  positionsOverTime: Array<{
    date: string;
    total_position: number;
    manager_positions: Array<{
      manager_name: string;
      position_size: number;
    }>;
  }>
) => {
  if (!positionsOverTime || positionsOverTime.length === 0) {
    return [];
  }

  // Get all unique managers
  const allManagers = new Set<string>();
  positionsOverTime.forEach(day => {
    day.manager_positions.forEach(pos => {
      allManagers.add(pos.manager_name);
    });
  });

  const managerList = Array.from(allManagers);
  const dates = positionsOverTime.map(day => formatDateForChart(day.date, positionsOverTime.length));

  // Create one trace per manager for stacked bar chart
  const traces = managerList.map((manager, index) => {
    const values = positionsOverTime.map(day => {
      const managerPos = day.manager_positions.find(pos => pos.manager_name === manager);
      return managerPos?.position_size || 0;
    });

    return {
      x: dates,
      y: values,
      name: manager,
      type: 'bar' as const,
      marker: {
        color: getChartColor(index)
      },
      hovertemplate: `<b>%{fullData.name}</b><br>` +
                     `Date: %{x}<br>` +
                     `Position Size: %{y:.2f}%<br>` +
                     `<extra></extra>`,
      hoverlabel: {
        bgcolor: getChartColor(index),
        bordercolor: 'white',
        font: { color: 'white' }
      }
    };
  });

  return traces;
};

export const getDefaultLayout = (title: string, yAxisTitle: string = 'Value') => ({
  title: {
    text: title,
    font: { size: 18, color: '#1F2937' }
  },
  xaxis: {
    showgrid: true,
    gridcolor: '#E5E7EB',
    tickfont: { size: 11 },
    tickangle: -45  // Angle the dates to prevent overlap
  },
  yaxis: {
    title: yAxisTitle,
    showgrid: true,
    gridcolor: '#E5E7EB',
    tickfont: { size: 12 }
  },
  legend: {
    orientation: 'h' as const,
    y: -0.15,  // Moved legend closer to chart
    x: 0.5,
    xanchor: 'center' as const,
    font: { size: 11 }  // Slightly smaller legend text
  },
  margin: { l: 60, r: 40, t: 60, b: 100 },  // Increased bottom margin for angled dates
  hovermode: 'closest' as const,
  showlegend: true
});

export const getStackedBarLayout = (title: string, yAxisTitle: string = 'Position Size (%)') => ({
  ...getDefaultLayout(title, yAxisTitle),
  barmode: 'stack' as const,
  hovermode: 'closest' as const  // Changed from 'x unified' to show only hovered segment
});
