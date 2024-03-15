// Skills.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { capitalizeId } from '../Utils';

function Skills() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [successNotification, setSuccessNotification] = useState(null);
  const [infoNotification, setInfoNotification] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);
  const navigate = useNavigate();

  const fetchData = () => {
    // Fetch data from the API endpoint
    setLoading(true);
    fetch('/api/skills/imported')
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      setData(json); // Convert object to an array of key-value pairs
    })
    .catch((error) => {
      console.error('Error fetching skills data:', error);
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
    // Fetch data from the /skills/imported API endpoint
    fetchData();
  }, []);

  const handleItemClick = (item) => {
    navigate(`/skill/${encodeURIComponent(item.id)}`, { state: { jsonData: item } });
  };

  const handleDeleteClick = (item) => {
    const confirmation = window.confirm(`Are you sure you want to delete ${item.name}?`);
    if (confirmation) {
      // Call the API to remove the skill
      fetch(`/api/skills/${item.id}`, {
        method: 'DELETE',
      })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log(`Skill ${capitalizeId(item.name)} successfully deleted.`);
        setSuccessNotification(`${capitalizeId(item.name)} Deleted`);
        // Clear the notification after a few seconds
        setTimeout(() => {
          setSuccessNotification(null);
        }, 3000);
        setInfoNotification(`Understander Restart Required`);
        // Clear the notification after a few seconds
        setTimeout(() => {
          setInfoNotification(null);
        }, 3000);
        fetchData();
      })
      .catch((error) => {
        console.error('Error deleting skill:', error);
        setErrorNotification(`${error.message}`);
        // Clear the notification after a few seconds
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      });
    } else {
      // User canceled the deletion
      console.log(`Deletion of ${item.name} canceled.`);
    }
  };

  return (
    <div>
      <h1>Skills</h1>
      <div className="page-container">
        <button 
          className="big-info-button"
          onClick={() => navigate('/import-skill')}
        >
            + Import Skill
        </button>
        <div style={{ paddingTop: '10px' }}>
          <h2 style={{ paddingBottom: '10px' }}>Imported</h2>
          {loading ? (
            <p>Loading...</p>
          ) : (
          <div>
            <ul className="item-list">
              {data.map((item, index) => (
                <li key={index} className="list-item" onClick={() => handleItemClick(item)}>
                  <span><strong>{item.name}</strong></span>
                  {item.id !== 'default' && (
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
        {infoNotification && (
          <div className="notification info-notification">{infoNotification}</div>
        )}
      </div>
    </div>
  );
}

export default Skills;
