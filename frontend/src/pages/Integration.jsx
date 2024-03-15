// Integration.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { capitalizeId, getFieldInput} from '../Utils';

function Integration() {
  const { integrationId } = useParams(); // Access the integrationId from URL params
  const location = useLocation();
  const manifestData = location.state?.jsonData;

  const [newChanges, setNewChanges] = useState(false);
  const [saving, setSaving] = useState(false);
  const [successNotification, setSuccessNotification] = useState(null);
  const [infoNotification, setInfoNotification] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);
  const [jsonData, setJsonData] = useState([]);
  const [importMode, setImportMode] = useState(false);
  const navigate = useNavigate();

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
      setNewChanges(true);
    }
  }, [location.state]);

  const handleInputChange = (fieldName, value) => {
    // Update the state with the new input value
    setJsonData((prevData) => ({
      ...prevData,
      [fieldName]: value,
    }));
    console.log(jsonData);

    // Mark changes as unsaved
    setNewChanges(true);
  };

  const handleSaveChanges = () => {
    setSaving(true);
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
        setSuccessNotification(`${manifestData.name} Config Updated`);
        setTimeout(() => {
          setSuccessNotification(null);
        }, 3000);
      } else {
        setSuccessNotification(`${manifestData.name} Imported`);
        setTimeout(() => {
          setSuccessNotification(null);
        }, 3000);
        setInfoNotification('Understander Restart Required');
        setTimeout(() => {
          setInfoNotification(null);
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
    })
    .finally(() => {
      setSaving(false);
    });
  };

  const editableFields = Object.entries(jsonData).filter(([fieldName]) => (
    fieldName !== 'name' && fieldName !== 'required_integrations'
  ));

  return (
    <div>
      <h1>Configure {manifestData.name}</h1>
      <div className="page-container" >
        <button 
          className="big-info-button"
          onClick={() => importMode ? navigate('/import-integration') : navigate('/integrations')}
        >
            Back
        </button>
        <form style={{ marginTop: '10px' }}>
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
              className={`info-button ${(!newChanges || saving) ? 'disabled' : ''}`}
              onClick={handleSaveChanges}
              disabled={!newChanges || saving}>
              {saving ? 'Importing...' : 'Import'}
            </button>
          ) : (
            <button
              type="button"
              className={`submit-button ${(!newChanges || saving) ? 'disabled' : ''}`}
              disabled={!newChanges || saving}
              onClick={handleSaveChanges}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          )}
        </form>
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

export default Integration;
