// Integration.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { capitalizeId, getFieldInput} from '../Utils';

function Integration() {
  const { integrationId } = useParams(); // Access the integrationId from URL params
  const location = useLocation();
  const [newChanges, setNewChanges] = useState(false);
  const [saveSuccessNotification, setSaveSuccessNotification] = useState(false);
  const [importSuccessNotification, setImportSuccessNotification] = useState(false);
  const [jsonData, setJsonData] = useState([]);
  const [importMode, setImportMode] = useState(false);

  useEffect(() => {
    // Fetch configuration data from the API endpoint
    fetch(`/integrations/${integrationId}/config`)
      .then((response) => response.json())
      .then((json) => {
        console.log(json);
        setJsonData(json);
      })
      .catch((error) => {
        console.error('Error fetching configuration data:', error);
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
    fetch(`/integrations/${integrationId}/config`, {
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
          setSaveSuccessNotification(true);
          setTimeout(() => {
            setSaveSuccessNotification(false);
          }, 3000);
        } else {
          setImportSuccessNotification(true);
          setTimeout(() => {
            setImportSuccessNotification(false);
          }, 3000);
        }
      });
  };

  const editableFields = Object.entries(jsonData).filter(([fieldName]) => (
    fieldName !== 'name' && fieldName !== 'required_integrations'
  ));

  return (
    <div className="integration-container">
      <h1>Edit Integration {capitalizeId(integrationId)}</h1>
      <form style={{ paddingTop: "20px"}}>
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
        {importMode ? (
          <button 
            type="button" 
            className="info-button" 
            onClick={handleSaveChanges}>
            Import
          </button>
        ) : (
          <button
            type="button"
            className={`save-button ${!newChanges ? 'disabled' : ''}`}
            disabled={!newChanges}
            onClick={handleSaveChanges}
          >
            Save Changes
          </button>
        )}
        <div className="notification-container">
          {saveSuccessNotification && (
            <div className="notification success-notification">Configuration Saved</div>
          )}
          {importSuccessNotification && (
            <div className="notification info-notification">Integration Imported</div>
          )}
        </div>
      </form>
    </div>
  );
}

export default Integration;
