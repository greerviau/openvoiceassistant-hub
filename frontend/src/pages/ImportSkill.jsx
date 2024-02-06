// ImportSkill.jsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { capitalizeId } from '../Utils';

function ImportSkill() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorNotification, setErrorNotification] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch data from the /skills/not_imported API endpoint
    fetch('/api/skills/not_imported')
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      setData(json); // Convert object to array
    })
    .catch((error) => {
      console.error('Error fetching not imported skills data:', error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    })
    .finally(() => {
      setLoading(false);
    });
  }, []);

  const handleItemClick = (item) => {
    // Use item[0] as the key (name) and item[1] as the value (object)
    navigate(`/skill/${encodeURIComponent(item.toLowerCase())}`, { state: { jsonData: item[1], import: true } });
  };

  return (
    <div>
      <h1>Import Skill</h1>
      <div className="list-container">
        <Link to="/skills" className="import-button">
          Back
        </Link>
        <h2 style={{ marginTop: '20px' }}>Available Skills</h2>
        <div style={{ marginTop: '20px' }}>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <div>
          {data.length === 0 ? (
            <p>No Available Skills</p>
          ) : (
          <ul className="item-list" style={{ paddingTop: '10px' }}>
            {data.map((item, index) => (
              <li className="list-item" key={index} onClick={() => handleItemClick(item)}>
                <strong>{capitalizeId(item)}</strong>
              </li>
            ))}
          </ul>
          )}
          </div>
        )}
        </div>
        <div className="notification-container">
          {errorNotification && (
            <div className="notification error-notification">{errorNotification}</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ImportSkill;
