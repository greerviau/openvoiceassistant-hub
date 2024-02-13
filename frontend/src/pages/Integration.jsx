// Integration.jsx
import React, { useState, useEffect } from 'react';
import { Link, useParams, useLocation } from 'react-router-dom';
import { capitalizeId, getFieldInput} from '../Utils';

function Integration() {
  const { integrationId } = useParams(); // Access the integrationId from URL params
  const location = useLocation();
  const [newChanges, setNewChanges] = useState(false);
  const [successNotification, setSuccessNotification] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);
  const [jsonData, setJsonData] = useState([]);
  const [importMode, setImportMode] = useState(false);

  useEffect(() => {
    // Fetch configuration data from the API endpoint
    fetch(`/api/integrations/${integrationId}/config`)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      console.log(json);
      setJsonData(json);
    })
    .catch((error) => {
      console.error('Error fetching configuration data:', error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });
  }, [integrationId]);

  useEffect(() => {
    // Check if import mode is true
    if (location.state && location.state.import) {
      setImportMode(true);
    }
  }, [location.state]);

  const handleInputChange = (fieldName, value) => {
    // Update the state with the new input value
    setJsonData((prevData) => ({
      ...prevData,
      [fieldName]: value,
    }));

    // Mark changes as unsaved
    setNewChanges(true);
  };

  const handleSaveChanges = () => {
    fetch(`/api/integrations/${integrationId}/config`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonData),
    })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      setNewChanges(false);
      if (!importMode) {
        console.log('Update successful:', json);
        // Display notification for configuration saved
        setSuccessNotification(`${capitalizeId(integrationId)} Config Updated`);
        setTimeout(() => {
          setSuccessNotification(null);
        }, 3000);
      } else {
        setSuccessNotification(`${capitalizeId(integrationId)} Imported`);
        setTimeout(() => {
          setSuccessNotification(null);
        }, 3000);
      }
    })
    .catch((error) => {
      console.error('Error fetching integrations data:', error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });
  };

  const editableFields = Object.entries(jsonData).filter(([fieldName]) => (
    fieldName !== 'name' && fieldName !== 'required_integrations'
  ));

  return (
    <div>
      <h1>Configure {capitalizeId(integrationId)}</h1>
      <div className='page-container'>
        <Link to="/integrations" className="big-info-button">
            Back
        </Link>
        <form style={{ paddingTop: "40px"}}>
        {editableFields.length === 0 ? (
            <p style={{ paddingBottom: "30px"}}>No Configuration Needed</p>
          ) : (
          <div>
            {editableFields.map(([fieldName, fieldValue], index) => {
              const inputField = getFieldInput(fieldName, fieldValue, handleInputChange, editableFields);

              // Skip rendering for fields ending with "_options"
              if (inputField === null) {
                return null;
              }

              return (
                <div key={index} className="form-field">
                  <label htmlFor={fieldName}>{capitalizeId(fieldName)}</label>
                  {inputField}
                </div>
              );
            })}
          </div>
          )}
          {importMode ? (
            <button 
              type="button" 
              className={`info-button ${!newChanges ? 'disabled' : ''}`}
              onClick={handleSaveChanges}
              disabled={!newChanges}>
              Import
            </button>
          ) : (
            <button
              type="button"
              className={`submit-button ${!newChanges ? 'disabled' : ''}`}
              disabled={!newChanges}
              onClick={handleSaveChanges}
            >
              Save Changes
            </button>
          )}
          <div className="notification-container">
            {errorNotification && (
              <div className="notification error-notification">{errorNotification}</div>
            )}
            {successNotification && (
              <div className="notification success-notification">{successNotification}</div>
            )}
          </div>
        </form>  
      </div>
    </div>
  );
}

export default Integration;
