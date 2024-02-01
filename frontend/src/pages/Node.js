// Node.js
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

function Node() {
  const location = useLocation();
  const jsonData = location.state?.jsonData;

  const [configData, setConfigData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if jsonData is available before making the API call
    if (jsonData) {
      const nodeId = jsonData.id;
      const apiEndpoint = `/node/${nodeId}/config`;

      // Fetch configuration data from the API endpoint
      fetch(apiEndpoint)
        .then((response) => response.json())
        .then((configJson) => {
          setConfigData(configJson);
          setLoading(false); // Set loading to false when data is fetched
        })
        .catch((error) => {
          console.error('Error fetching configuration data:', error);
          setLoading(false); // Set loading to false in case of an error
        });
    }
  }, [jsonData]); // Trigger the effect when jsonData changes

  if (!jsonData) {
    // Handle case where data for the selected node is not found
    return <div>No data found for this node.</div>;
  }

  return (
    <div className="list-container">
      <h1>{jsonData.name}</h1>
      {loading ? (
        <p>Loading configuration data...</p>
      ) : (
        <div>
          <h2>Configuration</h2>
          {/* Display configuration data or customize as needed */}
          <pre>{JSON.stringify(configData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default Node;
