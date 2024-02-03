// Nodes.js
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Nodes() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [restarting, setRestarting] = useState(false);
  const [identifying, setIdentifying] = useState(false);
  const navigate = useNavigate();

  const fetchData = () => {
    setRefreshing(true);
    // Fetch data from the API endpoint
    fetch('/node/status')
      .then((response) => response.json())
      .then((json) => {
        console.log(json);
        setData(json);
        setRefreshing(false); // Set loading to false when data is fetched
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
        setRefreshing(false); // Set loading to false in case of an error
      });
  };

  useEffect(() => {
    // Initial fetch
    setLoading(true);
    fetchData();
    setLoading(false);
  }, []);

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Fetch data every minute (60,000 milliseconds)
    const intervalId = setInterval(fetchData, 60000);

    // Cleanup the interval when the component unmounts
    return () => clearInterval(intervalId);
  }, []);

  const handleItemClick = (id) => {
    const selectedData = data.find((item) => item.id === id);

    // Navigate to the Node.js page with the specific item's data
    navigate(`/node/${id}`, { state: { jsonData: selectedData } });
  };

  const handleRestartClick = (id, event) => {
    // Stop the event from propagating to the list item's click event
    event.stopPropagation();
  
    // Set loading state to true for the corresponding item
    setRestarting(true);
  
    // API call to restart node
    fetch(`/node/${id}/restart`, {
      method: 'POST',
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log(`Node with ID ${id} restarted:`, json);
  
        // Refetch data from the /node/status API after a successful restart
        fetch('/node/status')
          .then((response) => response.json())
          .then((json) => {
            setData(json);
          })
          .catch((error) => {
            console.error('Error refetching data:', error);
          })
          .finally(() => {
            // Remove loading state for the corresponding item
            setRestarting(false);
          });
      })
      .catch((error) => {
        console.error(`Error restarting node with ID ${id}:`, error);
        // Remove loading state for the corresponding item on failure
        setRestarting(false);
      });
  };

  const handleRefreshClick = () => {
    // Manually trigger data refresh
    fetchData();
  };

  const handleItemIdentify = (id, event) => {
    // Stop the event from propagating to the list item's click event
    event.stopPropagation();
  
    // Set loading state to true for the corresponding item
    setIdentifying(true);
    // Call the identify API for the specific node
    fetch(`/node/${id}/announce/Hello%20World`, {
      method: 'POST',
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log('Node identified:', json);
        setIdentifying(false)
        // Add any additional logic you need after successful identification
      })
      .catch((error) => {
        console.error('Error identifying node:', error);
        // Handle the error, if needed
        setIdentifying(false);
      });
  };

  const handleDeleteClick = (id, name) => {
    const confirmation = window.confirm(`Are you sure you want to delete ${name}?`);
    if (confirmation) {
      // Call the API to remove the node
      fetch(`/node/${id}`, {
        method: 'DELETE',
      })
        .then((response) => {
          if (response.ok) {
            console.log(`${name} successfully deleted.`);
            // Add any additional logic or update UI as needed
            fetchData();
          } else {
            console.error(`Failed to delete ${name}.`);
            // Handle error or update UI accordingly
          }
        })
        .catch((error) => {
          console.error('Error deleting node:', error);
        });
    } else {
      // User canceled the deletion
      console.log(`Deletion of ${name} canceled.`);
    }
  };

  return (
    <div>
      <h1>Nodes</h1>
      <div className="list-container">
        <button
          onClick={handleRefreshClick}
          className={`info-button ${refreshing ? 'disabled' : ''}`}
          disabled={refreshing}
          style={{ marginBottom: '10px' }}
        >
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <ul className="item-list">
            {data.map((item) => (
              <li className="list-item" key={item.id} onClick={() => handleItemClick(item.id)}>
                <span>
                  <Link to="#" style={{ color: 'inherit' }}>
                    <strong>Name:</strong> {item.name} |{' '}
                    <strong>Status:</strong>{' '}
                    <span style={{ color: item.status === 'online' ? 'green' : 'red' }}>
                      {item.status}
                    </span>
                  </Link>
                  {item.status === 'online' && (
                    <button
                      className={`identify-button ${identifying ? 'disabled' : ''}`}
                      onClick={(event) => handleItemIdentify(item.id, event)}
                      disabled={identifying}
                    >
                      {identifying ? 'Identifying...' : 'Identify'}
                    </button>
                  )}
                  {item.restart_required && item.status === 'online' && (
                    <button
                      className={`info-button ${restarting ? 'disabled' : ''}`}
                      onClick={(event) => handleRestartClick(item.id, event)}
                      disabled={restarting}
                    >
                      {restarting ? 'Restarting...' : 'Restart'}
                    </button>
                  )}
                </span>
                <span className="delete-button-container">
                  <button
                    className="delete-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteClick(item.id, item.name);
                    }}
                  >
                    <i className="fas fa-trash-alt"></i>
                  </button>
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default Nodes;
