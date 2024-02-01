// Nodes.js
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Nodes() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch data from the API endpoint
    fetch('/node/status')
      .then((response) => response.json())
      .then((json) => {
        console.log(json)
        setData(json);
        setLoading(false); // Set loading to false when data is fetched
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
        setLoading(false); // Set loading to false in case of an error
      });
  }, []);

  const handleItemClick = (id) => {
    const selectedData = data.find((item) => item.id === id);

    // Navigate to the Node.js page with the specific item's data
    navigate(`/node/${id}`, { state: { jsonData: selectedData } });
  };

  return (
    <div className="list-container">
      <h1>Nodes Page</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul className="item-list">
          {data.map((item) => (
            <li key={item.id} onClick={() => handleItemClick(item.id)}>
              <Link to="#" style={{ color: 'inherit' }}>
                <strong>Name:</strong> {item.name} |{' '}
                <strong>Status:</strong>{' '}
                <span style={{ color: item.status === 'online' ? 'green' : 'red' }}>
                  {item.status}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Nodes;
