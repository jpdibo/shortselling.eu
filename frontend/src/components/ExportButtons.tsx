import React, { useState } from 'react';
import { convertToCSV, copyToClipboard, ExportableData } from '../utils/exportUtils';
import { CheckIcon, ClipboardIcon } from '@heroicons/react/24/outline';

interface ExportButtonsProps {
  data: ExportableData[];
  headers: string[];
  filename: string;
  className?: string;
}

const ExportButtons: React.FC<ExportButtonsProps> = ({ data, headers, filename, className = '' }) => {
  const [isCopying, setIsCopying] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = async () => {
    if (data.length === 0) return;
    
    setIsCopying(true);
    setCopySuccess(false);
    
    const csvContent = convertToCSV(data, headers);
    const success = await copyToClipboard(csvContent);
    
    setIsCopying(false);
    setCopySuccess(success);
    
    // Reset success message after 2 seconds
    if (success) {
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  if (data.length === 0) {
    return null;
  }

  return (
    <div className={`flex items-center ${className}`}>
      <button
        onClick={handleCopy}
        disabled={isCopying}
        className={`inline-flex items-center space-x-1.5 px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors ${
          isCopying ? 'opacity-75 cursor-not-allowed' : ''
        }`}
        title="Copy data to clipboard"
      >
        {copySuccess ? (
          <>
            <CheckIcon className="h-3 w-3 text-gray-700" />
            <span>Copied!</span>
          </>
        ) : (
          <>
            <ClipboardIcon className="h-3 w-3 text-gray-700" />
            <span>{isCopying ? 'Copying...' : 'Copy Data'}</span>
          </>
        )}
      </button>
    </div>
  );
};

export default ExportButtons;
