import React, { useState } from 'react';
import { clearLocalStorage, logLocalStorage, getLocalStorageKeys } from '../utils/storage';

interface DevToolsProps {
  isVisible?: boolean;
}

export const DevTools: React.FC<DevToolsProps> = ({ isVisible = false }) => {
  const [isOpen, setIsOpen] = useState(isVisible);
  const [localStorageKeys, setLocalStorageKeys] = useState<string[]>([]);

  const handleClearLocalStorage = () => {
    clearLocalStorage();
    setLocalStorageKeys([]);
  };

  const handleLogLocalStorage = () => {
    logLocalStorage();
    setLocalStorageKeys(getLocalStorageKeys());
  };

  const handleRefreshKeys = () => {
    setLocalStorageKeys(getLocalStorageKeys());
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-gray-800 text-white px-3 py-2 rounded-lg text-sm hover:bg-gray-700"
          title="Open Dev Tools"
        >
          🛠️
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 bg-white border border-gray-300 rounded-lg shadow-lg p-4 max-w-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Dev Tools</h3>
        <button
          onClick={() => setIsOpen(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>
      
      <div className="space-y-3">
        <div>
          <h4 className="font-medium text-sm mb-2">localStorage</h4>
          <div className="space-y-2">
            <button
              onClick={handleClearLocalStorage}
              className="w-full bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
            >
              Clear All localStorage
            </button>
            <button
              onClick={handleLogLocalStorage}
              className="w-full bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
            >
              Log localStorage
            </button>
            <button
              onClick={handleRefreshKeys}
              className="w-full bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
            >
              Refresh Keys
            </button>
          </div>
        </div>

        {localStorageKeys.length > 0 && (
          <div>
            <h4 className="font-medium text-sm mb-2">localStorage Keys:</h4>
            <div className="bg-gray-100 p-2 rounded text-xs max-h-32 overflow-y-auto">
              {localStorageKeys.map(key => (
                <div key={key} className="text-gray-700">
                  {key}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="text-xs text-gray-500">
          <p>Note: This app uses session-based authentication (cookies).</p>
          <p>localStorage is only used for guild selection preferences.</p>
        </div>
      </div>
    </div>
  );
};

export default DevTools; 