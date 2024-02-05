// Integrations.jsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { capitalizeId } from '../Utils';

function Integrations() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [successNotification, setSuccessNotification] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);
  const navigate = useNavigate();

  const fetchData = () => {
    // Fetch data from the API endpoint
    setLoading(true);
    fetch('/integrations/imported')
      .then((response) => response.json())
      .then((json) => {
        setData(json); // Convert object to an array of key-value pairs
      })
      .catch((error) => {
        console.error('Error fetching integrations data:', error);
        setErrorNotification(`${error.message}`);
        // Clear the notification after a few seconds
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    // Fetch data from the /integrations/imported API endpoint
    fetchData();
  }, []);

  const handleItemClick = (item) => {
    // Use item[0] as the key (name) and item[1] as the value (object)
    navigate(`/integration/${encodeURIComponent(item.toLowerCase())}`, { state: { jsonData: item[1] } });
  };

  const handleDeleteClick = (item) => {
    const confirmation = window.confirm(`Are you sure you want to delete ${capitalizeId(item)}?`);
    if (confirmation) {
      // Call the API to remove the integration
      fetch(`/integrations/${encodeURIComponent(item.toLowerCase())}`, {
        method: 'DELETE',
      })
      .then(() => {
        console.log(`Integration ${capitalizeId(item)} successfully deleted.`);
        setSuccessNotification(`${capitalizeId(item)} Deleted`);
        // Clear the notification after a few seconds
        setTimeout(() => {
          setSuccessNotification(null);
        }, 3000);
        // Add any additional logic or update UI as needed
        fetchData();
      })
      .catch((error) => {
        console.error('Error deleting integration:', error);
        setErrorNotification(`${error.message}`);
        // Clear the notification after a few seconds
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      });
    } else {
      // User canceled the deletion
      console.log(`Deletion of ${capitalizeId(item)} canceled.`);
    }
  };

  return (
    <div>
      <h1>Integrations</h1>
      <div className="list-container">
      <Link to="/import-integration" className="import-button">
          + Import Integration
      </Link>
      <div style={{ marginTop: '20px' }}>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <div>
            <h2 style={{ marginBottom: '10px' }}>Imported</h2>
            <ul className="item-list" style={{ paddingTop: '10px' }}>
              {data.map((item, index) => (
                <li key={index} className="list-item" onClick={() => handleItemClick(item)}>
                  <span><strong>{capitalizeId(item)}</strong></span>
                  {item !== 'default' && (
                  <button
                    className="delete-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteClick(item);
                    }}
                  >
                    <i className="fas fa-trash-alt"></i>
                  </button>
                  )}
                </li>
              ))}
            </ul>
          </div>
          )}
        </div>
      </div>
      <div className="notification-container">
        {errorNotification && (
          <div className="notification error-notification">{errorNotification}</div>
        )}
        {successNotification && (
          <div className="notification success-notification">{successNotification}</div>
        )}
      </div>
    </div>
  );
}

export default Integrations;
