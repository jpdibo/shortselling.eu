// Utility functions for exporting table data to CSV

export interface ExportableData {
  [key: string]: any;
}

/**
 * Converts table data to CSV format
 */
export const convertToCSV = (data: ExportableData[], headers: string[]): string => {
  if (data.length === 0) return '';
  
  // Create header row
  const csvHeaders = headers.join(',');
  
  // Create data rows
  const csvRows = data.map(row => {
    return headers.map(header => {
      const value = row[header];
      // Handle values that contain commas, quotes, or newlines
      if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
        return `"${value.replace(/"/g, '""')}"`;
      }
      return value || '';
    }).join(',');
  });
  
  return [csvHeaders, ...csvRows].join('\n');
};

/**
 * Downloads CSV data as a file
 */
export const downloadCSV = (csvContent: string, filename: string): void => {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

/**
 * Copies CSV data to clipboard
 */
export const copyToClipboard = async (csvContent: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(csvContent);
    return true;
  } catch (err) {
    console.error('Failed to copy to clipboard:', err);
    return false;
  }
};

/**
 * Formats date for filename
 */
export const getFormattedDate = (): string => {
  const now = new Date();
  return now.toISOString().split('T')[0]; // YYYY-MM-DD format
};

/**
 * Creates a filename with date
 */
export const createFilename = (baseName: string): string => {
  const date = getFormattedDate();
  return `${baseName}_${date}.csv`;
};
