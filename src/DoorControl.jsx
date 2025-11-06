import React, { useState } from 'react';

export default function DoorControl() {
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleButtonClick = async (direction) => {
    setLoading(true);
    setStatus('');
    
    try {
      const response = await fetch('https://data-dancer.com/api/door', {
        method: 'POST',
        headers: {
          'Content-Type': 'text/plain',
        },
        body: direction,
      });
      
      if (response.ok) {
        setStatus(`✓ Sent: ${direction}`);
      } else {
        setStatus(`✗ Error: ${response.status}`);
      }
    } catch (error) {
      setStatus(`✗ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold mb-6 text-center text-gray-800">
          Door Control
        </h1>
        
        <div className="flex gap-4 mb-4">
          <button
            onClick={() => handleButtonClick('Up')}
            disabled={loading}
            className="px-8 py-4 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors text-lg"
          >
            Up
          </button>
          
          <button
            onClick={() => handleButtonClick('Down')}
            disabled={loading}
            className="px-8 py-4 bg-green-500 text-white font-semibold rounded-lg hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors text-lg"
          >
            Down
          </button>
        </div>
        
        {status && (
          <div className="text-center text-sm mt-4 text-gray-700">
            {status}
          </div>
        )}
        
        {loading && (
          <div className="text-center text-sm mt-4 text-gray-500">
            Sending...
          </div>
        )}
      </div>
    </div>
  );
}