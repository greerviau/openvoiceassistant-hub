// Skill.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';

function capitalizeId(inputString) {
  inputString = inputString.replace(/_/g, ' ');
  return inputString.replace(/\b\w/g, match => match.toUpperCase());
}

function Skill() {
  const { skillId } = useParams(); // Access the skillId from URL params
  const location = useLocation();
  const [newChanges, setNewChanges] = useState(false);
  const [saveSuccessNotification, setSaveSuccessNotification] = useState(false);
  const [importSuccessNotification, setImportSuccessNotification] = useState(false);
  const [jsonData, setJsonData] = useState([]);
  const [importMode, setImportMode] = useState(false);

  useEffect(() => {
    // Fetch configuration data from the API endpoint
    fetch(`/skills/${skillId}/config`)
      .then((response) => response.json())
      .then((json) => {
        console.log(json);
        setJsonData(json);
      })
      .catch((error) => {
        console.error('Error fetching configuration data:', error);
      });
  }, []);

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
    fetch(`/skills/${skillId}/config`, {
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
    <div className="skill-container">
      <h1>Edit Skill {capitalizeId(skillId)}</h1>
      <form>
        {editableFields.map(([fieldName, fieldValue], index) => {
          const inputField = getFieldInput(fieldName, fieldValue, handleInputChange, jsonData, editableFields);

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
            <div className="notification info-notification">Skill Imported</div>
          )}
        </div>
      </form>
    </div>
  );
}

// Helper function to render input based on data type
const getFieldInput = (fieldName, fieldValue, handleInputChange, jsonData, editableFields) => {
  if (fieldName.endsWith('_options') && Array.isArray(fieldValue)) {
    // Skip rendering for fields ending with "_options"
    return null;
  }
  // Search for matching "_options" fields in the JSON
  const matchingOptionsField = editableFields.find(
    ([optionsFieldName, optionsFieldValue]) => (
      optionsFieldName.endsWith('_options') &&
      optionsFieldValue.length > 0 &&
      optionsFieldName.replace(/_options$/, '') === `${fieldName}`
    )
  );

  if (matchingOptionsField) {
    const baseFieldName = fieldName;
    return (
      <select
        className="dropdown"
        id={baseFieldName}
        name={baseFieldName}
        value={jsonData[baseFieldName]}
        onChange={(e) => handleInputChange(baseFieldName, e.target.value)}
      >
        {matchingOptionsField[1].map((option, index) => (
          <option key={index} value={option}>
            {option}
          </option>
        ))}
      </select>
    );
  }
  if (typeof fieldValue === 'boolean') {
    // Render a checkbox for boolean values
    return (
      <input
        type="checkbox"
        id={fieldName}
        name={fieldName}
        checked={fieldValue}
        onChange={(e) => handleInputChange(fieldName, e.target.checked)}
      />
    );
  } else if (typeof fieldValue === 'number') {
    // Render a number input for numeric values
    return (
      <input
        type="number"
        id={fieldName}
        name={fieldName}
        value={fieldValue}
        onChange={(e) => handleInputChange(fieldName, parseFloat(e.target.value))}
      />
    );
  } else {
    // Render a text input for other data types
    return (
      <input
        type="text"
        id={fieldName}
        name={fieldName}
        value={fieldValue || ''}
        onChange={(e) => handleInputChange(fieldName, e.target.value)}
      />
    );
  }
};

export default Skill;
