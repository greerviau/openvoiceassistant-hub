import React, { useState, useEffect } from 'react';
import { capitalizeId, getFieldInput} from '../Utils';

const CollapsibleSection = ({ title, component, config, setConfig, setSuccessNotification, setInfoNotification, setErrorNotification}) => {
  const [newChanges, setNewChanges] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const DropdownMenu = ({ options, initialValue, component }) => {
    const [selectedOption, setSelectedOption] = useState(initialValue || '');

    const handleOptionChange = async (e) => {
      const newSelectedOption = e.target.value;

      setSelectedOption(newSelectedOption);

      try {
        const response = await fetch(`/${component.toLowerCase()}/${newSelectedOption.toLowerCase()}/config/default`);
        const json = await response.json();
        console.log(json);
        setConfig((prevData) => ({
          ...prevData,
          config: json,
          algorithm: newSelectedOption,
        }));
      } catch (error) {
        console.error(`Error fetching ${component} configuration:`, error);
      }
      setNewChanges(true);
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

  const handleSaveChanges = () => {
    fetch(`/api/${component}/config`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    })
    .then((response) => response.json())
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
    // Call the reload API
    fetch(`/api/${component}/reload`, {
      method: 'POST',
    })
    .then((response) => response.json())
    .then((json) => {
      console.log('Reload successful');
      setSuccessNotification(`${capitalizeId(component)} Reloaded`);
      setTimeout(() => {
        setSuccessNotification(null);
      }, 3000);
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
    const componentConfig = config.config;
    const editableFields = Object.entries(componentConfig).filter(([fieldName]) => fieldName !== 'id');

    return (
      <div className="collapsible-section">
        <div className="section-header" onClick={toggleSection}>
          <h2>
            {title}
            <button className="reload-button" 
              style={{ marginLeft: '10px' }} 
              onClick={(e) => {
                e.stopPropagation();
                handleReload();
              }}>
              <i className="fas fa-sync"></i>
            </button>
            <span style={{ marginLeft: '10px' }}>
          {config && config.algorithm_options && (
            <DropdownMenu options={config.algorithm_options} initialValue={config.algorithm} component={component} />
          )}
          </span>
          </h2>
        </div>
        {isExpanded && (
          <div className="section-content">
            <form style={{ paddingTop: '20px' }}>
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
              <button
                type="button"
                className={`save-button ${!newChanges ? 'disabled' : ''}`}
                disabled={!newChanges}
                onClick={handleSaveChanges}
              >
                Save Changes
              </button>
            </form>
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
  const [transcriberConfig, setTranscriberConfig] = useState({});
  const [understanderConfig, setUnderstanderConfig] = useState({});
  const [synthesizerConfig, setSynthesizerConfig] = useState({});
  const [successNotification, setSuccessNotification] = useState(null);
  const [infoNotification, setInfoNotification] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);

  useEffect(() => {
    // Initial fetch
    console.log('Pulling config data')
    // Fetch configuration data for Transcriber
    fetch('/api/transcriber/config')
    .then((response) => response.json())
    .then((json) => {
      console.log(json);
      setTranscriberConfig(json);
    })
    .catch((error) => {
      console.error('Error fetching transcriber config:', error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });

    // Fetch configuration data for Understander
    fetch('/api/understander/config')
    .then((response) => response.json())
    .then((json) => {
      console.log(json);
      setUnderstanderConfig(json);
    })
    .catch((error) => {
      console.error('Error fetching understander config:', error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });

    // Fetch configuration data for Synthesizer
    fetch('/api/synthesizer/config')
    .then((response) => response.json())
    .then((json) => {
      console.log(json);
      setSynthesizerConfig(json);
    })
    .catch((error) => {
      console.error('Error fetching synthesizer config:', error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    });
  }, []);  

  return (
    <div>
      <h1>Settings</h1>
      <div className="settings-container">
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
