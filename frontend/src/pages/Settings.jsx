import React, { useState, useEffect } from 'react';
import { capitalizeId, getFieldInput} from '../Utils';

function Settings() {
  const [transcriberConfig, setTranscriberConfig] = useState({});
  const [understanderConfig, setUnderstanderConfig] = useState({});
  const [synthesizerConfig, setSynthesizerConfig] = useState({});

  useEffect(() => {
    // Fetch configuration data for Transcriber
    fetch(`/transcriber/config`)
      .then((response) => response.json())
      .then((json) => {
        console.log(json);
        setTranscriberConfig(json);
      })
      .catch((error) => {
        console.error('Error fetching Transcriber configuration:', error);
      });

    // Fetch configuration data for Understander
    fetch(`/understander/config`)
      .then((response) => response.json())
      .then((json) => {
        console.log(json);
        setUnderstanderConfig(json);
      })
      .catch((error) => {
        console.error('Error fetching Understander configuration:', error);
      });

    // Fetch configuration data for Synthesizer
    fetch(`/synthesizer/config`)
      .then((response) => response.json())
      .then((json) => {
        console.log(json);
        setSynthesizerConfig(json);
      })
      .catch((error) => {
        console.error('Error fetching Synthesizer configuration:', error);
      });
  }, []);
  
  const CollapsibleSection = ({title, component, config}) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [newChanges, setNewChanges] = useState(false);
    const [saveSuccessNotification, setSaveSuccessNotification] = useState(false);
    
    const handleInputChange = (fieldName, value) => {
      // Update the state with the new input value
      setTranscriberConfig((prevData) => ({
        ...prevData,
        [fieldName]: value,
      }));
      // Mark changes as unsaved
      setNewChanges(true);
    };

    const handleSaveChanges = (config) => {
      fetch(`/${component}/config`, {
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
          setSaveSuccessNotification(true);
          setTimeout(() => {
            setSaveSuccessNotification(false);
          }, 3000);
        });
    };
  
    const toggleSection = () => {
      setIsExpanded(!isExpanded);
    };

    const component_config = config.config;

    console.log(component_config);
    const editableFields = Object.entries(component_config).filter(([fieldName]) => (
      fieldName !== 'id'));

    console.log(editableFields);

    return (
      <div className="collapsible-section">
        <div className="section-header" onClick={toggleSection}>
          <h2>{title}</h2>
          {config && config.algorithm_options && (
            <DropdownMenu options={config.algorithm_options} initialValue={config.algorithm} />
          )}
        </div>
        {isExpanded && (
          <div className="section-content">
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
              <button
                type="button"
                className={`save-button ${!newChanges ? 'disabled' : ''}`}
                disabled={!newChanges}
                onClick={handleSaveChanges}
              >
                Save Changes
              </button>
              <div className="notification-container">
                {saveSuccessNotification && (
                  <div className="notification success-notification">{title} Config Saved</div>
                )}
              </div>
            </form>
          </div>
        )}
      </div>
    );
  };

  const DropdownMenu = ({ options, initialValue }) => {
    const [selectedOption, setSelectedOption] = useState(initialValue || '');
  
    const handleOptionChange = (e) => {
      setSelectedOption(e.target.value);
    };
  
    return (
      <div className="dropdown-container">
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
          <option value="">Select an option</option>
          {options.map((option, index) => (
            <option key={index} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>
    );
  };

  return (
    <div className="settings-container">
      <h1>Settings</h1>
      <CollapsibleSection 
            title="Transcriber" 
            component="transcriber"
            config={transcriberConfig}/>
      <CollapsibleSection 
            title="Understander" 
            component="understander"
            config={understanderConfig}/>
      <CollapsibleSection 
            title="Synthesizer" 
            component="synthesizer"
            config={synthesizerConfig}/>
    </div>
  );
}

export default Settings;
