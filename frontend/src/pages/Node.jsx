// Node.js
import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { capitalizeId } from '../Utils';

function Node() {
  const location = useLocation();
  const initialData = location.state?.jsonData;

  const [configData, setConfigData] = useState({});
  const [editedData, setEditedData] = useState({});
  const [loading, setLoading] = useState(true);
  const [newChanges, setNewChanges] = useState(false);
  const [infoNotification, setInfoNotification] = useState(null);
  const [successNotification, setSuccessNotification] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);
  const [isIdentifying, setIsIdentifying] = useState(false);
  const [isRestarting, setIsRestarting] = useState(false);
  const [microphones, setMicrophones] = useState([]);
  const [speakers, setSpeakers] = useState([]);
  const [wakeWords, setWakeWords] = useState([]);

  useEffect(() => {
    if (initialData) {
      // Fetch configuration data from the API endpoint
      fetch(`/node/${initialData.id}/config`)
        .then((response) => response.json())
        .then((json) => {
          console.log(json)
          setConfigData(json);
          setEditedData(json);
        })
        .catch((error) => {
          console.error('Error fetching configuration data:', error);
          setErrorNotification(`${error.message}`);
          // Clear the notification after a few seconds
          setTimeout(() => {
            setErrorNotification(null);
          }, 5000);
        })
        .finally(() => {
          setLoading(false);
        });

      // Fetch microphone data from the microphones endpoint using api_url
      fetch(`/node/${initialData.id}/hardware`)
        .then((response) => response.json())
        .then((json) => {
          console.log(json)
          setMicrophones(json.microphones);
          setSpeakers(json.speakers);
        })
        .catch((error) => {
          console.error('Error fetching hardware data:', error);
          setErrorNotification(`${error.message}`);
          // Clear the notification after a few seconds
          setTimeout(() => {
            setErrorNotification(null);
          }, 5000);
        });

      fetch(`/node/${initialData.id}/wake_words`)
        .then((response) => response.json())
        .then((json) => {
          console.log(json)
          setWakeWords(json);
        })
        .catch((error) => {
          console.error('Error fetching wake word data:', error);
          setErrorNotification(`${error.message}`);
          // Clear the notification after a few seconds
          setTimeout(() => {
            setErrorNotification(null);
          }, 5000);
        });
    }
  }, [initialData]);

  const handleIdentify = () => {
    // Set the loading state to true
    setIsIdentifying(true);
  
    // API call to announce "Hello World"
    fetch(`/node/${initialData.id}/announce/Hello%20World`, {
      method: 'POST',
    })
    .then((json) => {
      console.log('Announcement initiated:', json);
      // You can handle successful announcement here if needed
    })
    .catch((error) => {
      console.error('Error initiating announcement:', error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    })
    .finally(() => {
      // Set the loading state to false after the API call is completed
      setIsIdentifying(false);
    });
  };

  const handleInputChange = (field, value) => {
    let typedValue = value;
    // Convert the value to the appropriate type based on the field type
    switch (typeof configData[field]) {
      case 'number':
        typedValue = parseFloat(value) || 0; // Use 0 if parseFloat returns NaN
        break;
      default:
        typedValue = value;
    }

    setNewChanges(true);
  
    setEditedData((prevData) => ({
      ...prevData,
      [field]: typedValue,
    }));
  };

  const handleCheckboxChange = (field) => {
    setNewChanges(true);
    setEditedData((prevData) => ({
      ...prevData,
      [field]: !prevData[field], // Toggle the boolean value
    }));
    console.log(editedData);
  };

  const handleSaveChanges = () => {
    // Set restart_required to true before making the API call
    const dataWithRestart = { ...editedData, restart_required: true };
  
    // API call to update node configuration
    fetch(`/node/${initialData.id}/config`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dataWithRestart),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log('Update successful:', json);
        setNewChanges(false);
        // Display notification for configuration saved
        setSuccessNotification('Changes Saved');
        setTimeout(() => {
          setSuccessNotification(null);
        }, 3000);
  
        if (initialData.status === 'online') {
          // Display notification for node restart required
          setInfoNotification('Node Restart Required');
          setTimeout(() => {
            setInfoNotification(null);
          }, 3000);
        }
  
        // Enable the restart button
        setConfigData((prevData) => ({ ...prevData, restart_required: true }));
      })
      .catch((error) => {
        console.error('Error restarting node:', error);
        setErrorNotification(`${error.message}`);
        // Clear the notification after a few seconds
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      });
  };

  const handleRestart = () => {
    // Set the loading state to true
    setIsRestarting(true);

    // API call to restart node
    fetch(`/node/${initialData.id}/restart`, {
      method: 'POST',
    })
    .then((json) => {
      console.log('Node restarted:', json);
      setSuccessNotification('Node Restarted');
      setTimeout(() => {
        setSuccessNotification(null);
      }, 3000);
    })
    .catch((error) => {
      console.error('Error restarting node:', error);
      setErrorNotification(`${error.message}`);
      // Clear the notification after a few seconds
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    })
    .finally(() => {
      // Set the loading state to false after the API call is completed
      setIsRestarting(null);
    });
  };

  if (!initialData) {
    return <div>No data found for this node.</div>;
  }

  return (
    <div>
      <div className="node-header">
        <h1>{initialData.name}</h1>
        <button
          type="button"
          className={`info-button ${isRestarting || initialData.status === 'offline' ? 'disabled' : ''}`}
          onClick={handleRestart}
          disabled={isRestarting}
        >
          {isRestarting ? 'Restarting...' : 'Restart'}
        </button>
        <button
          type="button"
          className={`identify-button ${isIdentifying || initialData.status === 'offline' ? 'disabled' : ''}`}
          onClick={handleIdentify}
          disabled={isIdentifying || initialData.status === 'offline'}
        >
          {isIdentifying ? 'Identifying...' : 'Identify'}
        </button>
      </div>
      <div style={{ paddingLeft: "20px"}}>
        <Link to="/nodes" className="import-button">
          Back
        </Link>
        {loading ? (
          <p>Loading data...</p>
        ) : (
          <div style={{ paddingTop: "20px" }}>
            <h2>Configuration</h2>
            
            <form style={{ paddingTop: "20px"}}>
              <div className="form-field">
                <label>Name</label>
                <input
                  type="text"
                  value={editedData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                />
              </div>
              <div className="form-field">
                <label>Area</label>
                <input
                  type="text"
                  value={editedData.area}
                  onChange={(e) => handleInputChange('area', e.target.value)}
                />
              </div>
              <div className="form-field">
                <label>WakeWord</label>
                <select
                  className="dropdown"
                  value={editedData.wake_word}
                  onChange={(e) => handleInputChange('wake_word', e.target.value)}
                >
                  {wakeWords.map((wake_word, index) => (
                    <option key={index} value={wake_word}>
                      {capitalizeId(wake_word)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <label>Wake Word Confidence</label>
                <input
                  type="number"
                  value={editedData.wake_word_conf_threshold}
                  onChange={(e) => handleInputChange('wake_word_conf_threshold', e.target.value)}
                />
              </div>
              <div className="form-field">
                <label>Wakeup Sound</label>
                <input
                  type="checkbox"
                  checked={editedData.wakeup_sound}
                  onChange={(e) => handleCheckboxChange('wakeup_sound')}
                />
              </div>
              <div className="form-field">
                <label>VAD Sensitivity</label>
                <input
                  type="number"
                  value={editedData.vad_sensitivity}
                  onChange={(e) => handleInputChange('vad_sensitivity', e.target.value)}
                />
              </div>
              <div className="form-field">
                <label>VAD Threshold</label>
                <input
                  type="number"
                  value={editedData.vad_threshold}
                  onChange={(e) => handleInputChange('vad_threshold', e.target.value)}
                />
              </div>
              <div className="form-field">
                <label>Speex Noise Suppression</label>
                <input
                  type="checkbox"
                  checked={editedData.speex_noise_suppression}
                  onChange={(e) => handleCheckboxChange('speex_noise_suppression')}
                />
              </div>
              <div className="form-field">
                <label>Microphone</label>
                <select
                  className="dropdown"
                  value={editedData.mic_index}
                  onChange={(e) => handleInputChange('mic_index', e.target.value)}
                >
                  {microphones.map((mic, index) => (
                    <option key={index} value={mic.idx}>
                      {mic.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <label>Speaker</label>
                <select
                  className="dropdown"
                  value={editedData.speaker_index}
                  onChange={(e) => handleInputChange('speaker_index', e.target.value)}
                >
                  {speakers.map((speaker, index) => (
                    <option key={index} value={speaker.idx}>
                      {speaker.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <label>Volume</label>
                <input
                  type="number"
                  value={editedData.volume}
                  onChange={(e) => handleInputChange('volume', e.target.value)}
                />
              </div>
              <button type="button" 
                  className={`save-button ${!newChanges ? 'disabled' : ''}`} 
                  disabled={!newChanges} 
                  onClick={handleSaveChanges}>Save Changes</button>
              <div className="notification-container">
                {errorNotification && (
                  <div className="notification error-notification">{errorNotification}</div>
                )}
                {infoNotification && (
                  <div className="notification info-notification">{infoNotification}</div>
                )}
                {successNotification && (
                  <div className="notification success-notification">{successNotification}</div>
                )}
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

export default Node;
