import React, { useState, useEffect } from 'react';
import { capitalizeId, getFieldInput} from '../Utils';

const CollapsibleSection = ({ title, component, config, setConfig, setSuccessNotification, setInfoNotification, setErrorNotification}) => {
  const [newChanges, setNewChanges] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isReloading, setIsReloading] = useState(false);

  const DropdownMenu = ({ options, initialValue, component }) => {
    const [selectedOption, setSelectedOption] = useState(initialValue || '');

    const handleOptionChange = async (e) => {
      const newSelectedOption = e.target.value;

      setSelectedOption(newSelectedOption);
      fetch(`/api/${component.toLowerCase()}/${newSelectedOption.toLowerCase()}/config/default`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log(json);
        setConfig((prevData) => ({
          ...prevData,
          config: json,
          algorithm: newSelectedOption,
        }));
        setNewChanges(true);
      })
      .catch((error) => {
        console.error(`Error fetching ${component} configuration:`, error);
        setErrorNotification(`${error.message}`);
        // Clear the notification after a few seconds
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      });
    };

    return (
      <select
        className='dropdown'
        id="algorithmDropdown"
        name="algorithmDropdown"
        value={selectedOption}
        onChange={handleOptionChange}
        onClick={(e) => {
          e.stopPropagation();
        }}
      >
        {options.map((option, index) => (
          <option key={index} value={option}>
            {capitalizeId(option)}
          </option>
        ))}
      </select>
    );
  };

  const handleInputChange = (fieldName, value) => {
    // Update the state with the new input value
    setConfig((prevData) => ({
      ...prevData,
      config: {
        ...prevData.config,
        [fieldName]: value,
      },
    }));
    // Mark changes as unsaved
    setNewChanges(true);
  };

  const handleComponentConfigInputChange = (fieldName, value) => {
    // Update the state with the new input value
    setConfig((prevData) => ({
      ...prevData,
      [fieldName]: value
    }));
    // Mark changes as unsaved
    setNewChanges(true);
  };

  const handleSaveChanges = () => {
    fetch(`/api/${component}/config`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      setNewChanges(false);
      console.log('Update successful:', json);
      // Display notification for configuration saved
      setSuccessNotification(`Saved ${capitalizeId(component)} Config`);
      setTimeout(() => {
        setSuccessNotification(null);
      }, 3000);

      setInfoNotification(`${capitalizeId(component)} Reload Required`);
      setTimeout(() => {
        setInfoNotification(null);
      }, 3000);
    })
    .catch((error) => {
      console.error(`Error updating ${component} configuration:`, error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });
  };

  const handleReload = () => {
    setIsReloading(true);
    setInfoNotification(`${capitalizeId(component)} Reloading...`);
    // Call the reload API
    fetch(`/api/${component}/reload`, {
      method: 'POST',
    })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      console.log('Reload successful');
      setInfoNotification(null);
      setSuccessNotification(`${capitalizeId(component)} Reloaded`);
      setTimeout(() => {
        setSuccessNotification(null);
      }, 3000);
      setIsReloading(false);
    })
    .catch((error) => {
      console.error(`Error reloading ${component} configuration:`, error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });
  };

  const toggleSection = () => {
    setIsExpanded(!isExpanded);
  };

  if (config && config.config) {
    const componentConfig = config;
    const editableComponentConfig = Object.entries(componentConfig).filter(([fieldName]) => fieldName !== 'config' && fieldName !== 'algorithm' && fieldName !== 'algorithm_options');

    const algorithmConfig = config.config;
    const editableAlgorithmConfig = Object.entries(algorithmConfig).filter(([fieldName]) => fieldName !== 'id');

    return (
      <div className="collapsible-section">
        <div className="section-header" onClick={toggleSection}>
          <h2>
            {title}
            <button className="reload-button" 
              style={{ marginLeft: '10px' }} 
              disabled={isReloading}
              onClick={(e) => {
                e.stopPropagation();
                handleReload();
              }}>
              <i className={`fas fa-sync${isReloading ? ' fa-spin' : ''}`}></i>
            </button>
          </h2>
        </div>
        {isExpanded && (
          <div className="section-content">
            <span>
            <label>Algorithm</label>
            {config && config.algorithm_options && (
              <DropdownMenu options={config.algorithm_options} initialValue={config.algorithm} component={component} />
            )}
            </span>
            <form style={{ marginLeft: '30px', paddingTop: '20px' }}>
              {editableAlgorithmConfig.map(([fieldName, fieldValue], index) => {
                const inputField = getFieldInput(fieldName, fieldValue, handleInputChange, editableAlgorithmConfig);

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
            </form>
            {editableComponentConfig.map(([fieldName, fieldValue], index) => {
                const inputField = getFieldInput(fieldName, fieldValue, handleComponentConfigInputChange, editableComponentConfig);

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
            <button
                type="button"
                className={`submit-button ${!newChanges ? 'disabled' : ''}`}
                disabled={!newChanges}
                onClick={handleSaveChanges}
              >
                Save Changes
              </button>
          </div>
        )}
      </div>
    );
  } else {
    console.error('Config is undefined or missing required properties.');
    return null; // or some fallback UI if needed
  }
};

function Settings() {
  const [newSettingsChanges, setNewSettingsChanges] = useState(false);
  const [generalSettings, setGeneralSettings] = useState({});
  const [isSettingsExpanded, setIsSettingsExpanded] = useState(false);
  const [transcriberConfig, setTranscriberConfig] = useState({});
  const [understanderConfig, setUnderstanderConfig] = useState({});
  const [synthesizerConfig, setSynthesizerConfig] = useState({});
  const [successNotification, setSuccessNotification] = useState(null);
  const [infoNotification, setInfoNotification] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);
  const [updateStatus, setUpdateStatus] = useState({});
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    // Initial fetch
    console.log('Pulling config data')
    // Fetch configuration data for Transcriber
    fetch('/api/config')
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      console.log(json);
      setTranscriberConfig(json.transcriber);
      setUnderstanderConfig(json.understander);
      setSynthesizerConfig(json.synthesizer);
      setGeneralSettings(json.settings);
    })
    .catch((error) => {
      console.error('Error fetching config:', error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });

    fetch('/api/update/available')
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      console.log(json);
      setUpdateStatus(json);
      setUpdating(json.updating);
    })
    .catch((error) => {
      console.error('Error fetching update status:', error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });
  }, []);

  const handleSaveSettingsChanges = () => {
    fetch(`/api/config/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(generalSettings),
    })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      setNewSettingsChanges(false);
      console.log('Update successful:', json);
      // Display notification for configuration saved
      setSuccessNotification(`Saved Settings`);
      setTimeout(() => {
        setSuccessNotification(null);
      }, 3000);

      setInfoNotification(`Restart Required`);
      setTimeout(() => {
        setInfoNotification(null);
      }, 3000);
    })
    .catch((error) => {
      console.error(`Error updating settings:`, error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });
  };

  const handleInputSettingsChange = (fieldName, value) => {
    // Update the state with the new input value
    setGeneralSettings((prevData) => ({
      ...prevData,
      [fieldName]: value
    }));
    // Mark changes as unsaved
    setNewSettingsChanges(true);
  };

  const handleUpdateClick = () => {
    // Set loading state to true for the corresponding item
    setUpdating(true);
  
    // API call to restart node
    fetch(`/api/update`, {
      method: 'POST',
    })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      console.log(`OVA updating:`, json);
      setInfoNotification(`Updating...`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setInfoNotification(null);
      }, 3000);
      refreshStatus();
    })
    .catch((error) => {
      console.error(`Error updating:`, error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });
  };

  const toggleSection = () => {
    setIsSettingsExpanded(!isSettingsExpanded);
  };

  const editableSettings = Object.entries(generalSettings);

  return (
    <div>
      <h1>Settings</h1>
      <div className="page-container">
        {(updateStatus.update_available || updateStatus.updating) && (
          <div className="collapsible-section">
            <div className="section-header">
              <h2>{`Update: ${updateStatus.update_version}`}
                <button
                  style={{marginLeft: "10px"}}
                  className={`update-button ${updating ? 'disabled' : ''}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleUpdateClick();
                  }}
                  disabled={updating}
                >
                  {updating ? 'Updating...' : 'Update'}
                </button>
              </h2>
            </div>
          </div>
        )};
        <CollapsibleSection 
              title="Transcriber" 
              component="transcriber"
              config={transcriberConfig}
              setConfig={setTranscriberConfig}
              setSuccessNotification={setSuccessNotification}
              setInfoNotification={setInfoNotification}
              setErrorNotification={setErrorNotification}/>
        <CollapsibleSection 
              title="Understander" 
              component="understander"
              config={understanderConfig}
              setConfig={setUnderstanderConfig}
              setSuccessNotification={setSuccessNotification}
              setInfoNotification={setInfoNotification}
              setErrorNotification={setErrorNotification}/>
        <CollapsibleSection 
              title="Synthesizer" 
              component="synthesizer"
              config={synthesizerConfig}
              setConfig={setSynthesizerConfig}
              setSuccessNotification={setSuccessNotification}
              setInfoNotification={setInfoNotification}
              setErrorNotification={setErrorNotification}/>
        <div className="collapsible-section">
          <div className="section-header" onClick={toggleSection}>
            <h2>General</h2>
          </div>
          {isSettingsExpanded && (
            <div className="section-content">
              <form style={{ paddingTop: '20px' }}>
                {editableSettings.map(([fieldName, fieldValue], index) => {
                  const inputField = getFieldInput(fieldName, fieldValue, handleInputSettingsChange, editableSettings);

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
              </form>
              <button
                  type="button"
                  className={`submit-button ${!newSettingsChanges ? 'disabled' : ''}`}
                  disabled={!newSettingsChanges}
                  onClick={handleSaveSettingsChanges}
                >
                  Save Changes
                </button>
            </div>
          )}
        </div>
        <div className="notification-container">
          {successNotification && (
            <div className="notification success-notification">{successNotification}</div>
          )}
          {infoNotification && (
            <div className="notification info-notification">{infoNotification}</div>
          )}
          {errorNotification && (
            <div className="notification error-notification">{errorNotification}</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Settings;
