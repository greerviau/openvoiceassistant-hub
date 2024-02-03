// Skills.jsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function capitalizeId(inputString) {
  inputString = inputString.replace(/_/g, ' ');
  return inputString.replace(/\b\w/g, match => match.toUpperCase());
}

function Skills() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchData = () => {
    // Fetch data from the API endpoint
    setLoading(true);
    fetch('/skills/imported')
      .then((response) => response.json())
      .then((json) => {
        setData(json); // Convert object to an array of key-value pairs
        setLoading(false); // Set loading to false when data is fetched
      })
      .catch((error) => {
        console.error('Error fetching skills data:', error);
        setLoading(false); // Set loading to false in case of an error
      });
  };

  useEffect(() => {
    // Fetch data from the /skills/imported API endpoint
    fetchData();
  }, []);

  const handleItemClick = (item) => {
    // Use item[0] as the key (name) and item[1] as the value (object)
    navigate(`/skill/${encodeURIComponent(item.toLowerCase())}`, { state: { jsonData: item[1] } });
  };

  const handleImportNewSkill = () => {
    // Navigate to the ImportSkill page
    navigate('/import-skill');
  };

  const handleDeleteClick = (item) => {
    const confirmation = window.confirm(`Are you sure you want to delete ${capitalizeId(item)}?`);
    if (confirmation) {
      // Call the API to remove the skill
      fetch(`/skills/${encodeURIComponent(item.toLowerCase())}`, {
        method: 'DELETE',
      })
        .then((response) => {
          if (response.ok) {
            console.log(`Skill ${capitalizeId(item)} successfully deleted.`);
            // Add any additional logic or update UI as needed
            fetchData();
          } else {
            console.error(`Failed to delete skill ${capitalizeId(item)}.`);
            // Handle error or update UI accordingly
          }
        })
        .catch((error) => {
          console.error('Error deleting skill:', error);
        });
    } else {
      // User canceled the deletion
      console.log(`Deletion of ${capitalizeId(item)} canceled.`);
    }
  };

  return (
    <div className="list-container">
      <h1>Skills</h1>
      <button
        className="button-import"
        onClick={handleImportNewSkill}
      >
        + Import Skill
      </button>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div>
          <h2 style={{ marginBottom: '10px' }}>Imported Skills</h2>
          <ul className="item-list" style={{ paddingTop: '10px' }}>
            {data.map((item, index) => (
              <li key={index} className="list-item" onClick={() => handleItemClick(item)}>
                <span>{capitalizeId(item)}</span>
                {item != 'default' && (
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
  );
}

export default Skills;
