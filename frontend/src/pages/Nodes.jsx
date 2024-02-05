// Nodes.js
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Nodes() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [successNotification, setSuccessNotification] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);
  const navigate = useNavigate();

  const fetchData = () => {
    setRefreshing(true);
    // Fetch data from the API endpoint
    fetch('/node/status')
      .then((response) => response.json())
      .then((json) => {
        console.log(json);
        setData(json);
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
        setErrorNotification(`${error.message}`);
        // Clear the notification after a few seconds
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      })
      .finally(() => {
        setRefreshing(false);
      });
  };

  useEffect(() => {
    // Initial fetch
    setLoading(true);
    fetchData();
    setLoading(false);

    // Fetch data every minute (60,000 milliseconds)
    const intervalId = setInterval(fetchData, 60000);

    // Cleanup the interval when the component unmounts
    return () => clearInterval(intervalId);
  }, []);

  const NodeItem = ({nodeItem}) => {
    const [restarting, setRestarting] = useState(false);
    const [identifying, setIdentifying] = useState(false);

    const handleItemClick = (id) => {
      const selectedData = data.find((item) => item.id === id);
  
      // Navigate to the Node.js page with the specific item's data
      navigate(`/node/${id}`, { state: { jsonData: selectedData } });
    };
  
    const handleRestartClick = (id, name) => {
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
          setSuccessNotification(`${name} Restarted`);
          // Clear the notification after a few seconds
          setTimeout(() => {
            setSuccessNotification(null);
          }, 3000);
          fetchData();
        })
        .catch((error) => {
          console.error(`Error restarting node with ID ${id}:`, error);
          setErrorNotification(`${error.message}`);
          // Clear the notification after a few seconds
          setTimeout(() => {
            setErrorNotification(null);
          }, 5000);
        })
        .finally(() => {
          setRestarting(false);
        });
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
          // Add any additional logic you need after successful identification
        })
        .catch((error) => {
          console.error('Error identifying node:', error);
          setErrorNotification(`${error.message}`);
          // Clear the notification after a few seconds
          setTimeout(() => {
            setErrorNotification(null);
          }, 5000);
          // Handle the error, if needed
          
        }).finally(() => {
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
              setSuccessNotification(`${name} Deleted`);
              // Clear the notification after a few seconds
              setTimeout(() => {
                setSuccessNotification(null);
              }, 3000);
              fetchData();
            } else {
              console.error(`Failed to delete ${name}.`);
              // Handle error or update UI accordingly
            }
          })
          .catch((error) => {
            console.error('Error deleting node:', error);
            setErrorNotification(`${error.message}`);
            // Clear the notification after a few seconds
            setTimeout(() => {
              setErrorNotification(null);
            }, 5000);
          });
      } else {
        // User canceled the deletion
        console.log(`Deletion of ${name} canceled.`);
      }
    };

    return (
      <li className="list-item" key={nodeItem.id} onClick={() => handleItemClick(nodeItem.id)}>
        <span>
          <Link to="#" style={{ color: 'inherit' }}>
            <strong>Name:</strong> {nodeItem.name} |{' '}
            <strong>Status:</strong>{' '}
            <span style={{ color: nodeItem.status === 'online' ? 'green' : 'red' }}>
              {nodeItem.status}
            </span>
          </Link>
          {nodeItem.status === 'online' && (
            <button
              className={`identify-button ${identifying ? 'disabled' : ''}`}
              onClick={(event) => handleItemIdentify(nodeItem.id, event)}
              disabled={identifying}
            >
              {identifying ? 'Identifying...' : 'Identify'}
            </button>
          )}
          {nodeItem.restart_required && nodeItem.status === 'online' && (
            <button
              className={`info-button ${restarting ? 'disabled' : ''}`}
              onClick={(e) => {
                e.stopPropagation();
                handleRestartClick(nodeItem.id, nodeItem.name);
              }}
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
              handleDeleteClick(nodeItem.id, nodeItem.name);
            }}
          >
            <i className="fas fa-trash-alt"></i>
          </button>
        </span>
      </li>
    )
  };

  return (
    <div>
      <h1>Nodes</h1>
      <div className="list-container">
        <button
          onClick={fetchData}
          className={`import-button ${refreshing ? 'disabled' : ''}`}
          disabled={refreshing}
        >
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <ul className="item-list">
            {data.map((item) => (
              <NodeItem nodeItem={item}/>
            ))}
          </ul>
        )}
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

export default Nodes;
