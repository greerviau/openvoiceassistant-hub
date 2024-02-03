// ImportSkill.jsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function capitalizeId(inputString) {
    inputString = inputString.replace(/_/g, ' ');
    return inputString.replace(/\b\w/g, match => match.toUpperCase());
}

function ImportSkill() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch data from the /skills/not_imported API endpoint
    fetch('/skills/not_imported')
      .then((response) => response.json())
      .then((json) => {
        setData(json); // Convert object to array
        setLoading(false); // Set loading to false when data is fetched
      })
      .catch((error) => {
        console.error('Error fetching not imported skills data:', error);
        setLoading(false); // Set loading to false in case of an error
      });
  }, []);

  const handleItemClick = (item) => {
    // Use item[0] as the key (name) and item[1] as the value (object)
    navigate(`/skill/${encodeURIComponent(item.toLowerCase())}`, { state: { jsonData: item[1], import: true } });
  };

  return (
    <div className="list-container">
      <h1 style={{ marginBottom: '20px' }}>Import Skills</h1>
      <Link to="/skills" className="button-import">
        Back to Skills
      </Link>
      <h2 style={{ marginTop: '20px', marginBottom: '10px' }}>Imported Skills</h2>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div>
          <ul className="item-list" style={{ paddingTop: '10px' }}>
            {data.map((item, index) => (
              <li key={index} onClick={() => handleItemClick(item)}>
                {capitalizeId(item)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ImportSkill;
