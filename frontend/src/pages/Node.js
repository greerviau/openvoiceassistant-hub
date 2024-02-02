// Node.js
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

function Node() {
  const location = useLocation();
  const initialData = location.state?.jsonData;

  const [configData, setConfigData] = useState({});
  const [editedData, setEditedData] = useState({});
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [restartNotification, setRestartNotification] = useState(null);
  const [restartSuccessNotification, setRestartSuccessNotification] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);
  const [isRestarting, setIsRestarting] = useState(false);
  const [microphones, setMicrophones] = useState([]);
  const [speakers, setSpeakers] = useState([]);
  const [isIdentifying, setIsIdentifying] = useState(false);

  useEffect(() => {
    if (initialData) {
      // Fetch configuration data from the API endpoint
      fetch(`/node/${initialData.id}/config`)
        .then((response) => response.json())
        .then((json) => {
          setConfigData(json);
          setEditedData(json);
          setLoading(false);
        })
        .catch((error) => {
          console.error('Error fetching configuration data:', error);
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
          console.error('Error fetching microphone data:', error);
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
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log('Announcement initiated:', json);
        // You can handle successful announcement here if needed
      })
      .catch((error) => {
        console.error('Error initiating announcement:', error);
        // You can handle the error if needed
      })
      .finally(() => {
        // Set the loading state to false after the API call is completed
        setIsIdentifying(false);
      });
  };

  const handleInputChange = (field, value) => {
    setEditedData((prevData) => ({
      ...prevData,
      [field]: value,
    }));
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
        setIsSaved(true);
  
        // Display notification for configuration saved
        setTimeout(() => {
          setIsSaved(false);
        }, 3000);
  
        // Display notification for node restart required
        setRestartNotification(true);
        setTimeout(() => {
          setRestartNotification(false);
        }, 3000);
  
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
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log('Node restarted:', json);
        setRestartSuccessNotification('Node Restarted');
      })
      .catch((error) => {
        console.error('Error restarting node:', error);
        setErrorNotification(`${error.message}`);
      })
      .finally(() => {
        // Set the loading state to false after the API call is completed
        setIsRestarting(false);
      });
  };

  if (!initialData) {
    return <div>No data found for this node.</div>;
  }

  // Filter out id and api_url from being displayed
  const filteredConfigData = Object.fromEntries(
    Object.entries(configData).filter(
      ([field]) => field !== 'id' && field !== 'api_url' && field !== 'restart_required'
    )
  );

  return (
    <div className="list-container">
      {!loading && (
        <div className="node-header">
        <h1>{initialData.name}</h1>
        <button
          type="button"
          className={`identify-button ${isIdentifying || initialData.status === 'offline' ? 'disabled' : ''}`}
          onClick={handleIdentify}
          disabled={isIdentifying || initialData.status === 'offline'}
        >
          {isIdentifying ? 'Identifying...' : 'Identify'}
        </button>
      </div>
      )}
      {loading ? (
        <p>Loading data...</p>
      ) : (
        <div className="edit-node-form">
          <h2>Edit Node Configuration</h2>
          
          <form>
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
              <label>Wake Word Engine</label>
              <input
                type="text"
                value={editedData.wake_word_engine}
                onChange={(e) => handleInputChange('wake_word_engine', e.target.value)}
              />
            </div>
            <div className="form-field">
              <label>Wake Word</label>
              <input
                type="text"
                value={editedData.wake_word}
                onChange={(e) => handleInputChange('wake_word', e.target.value)}
              />
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
                value={editedData.wakeup_sound}
                onChange={(e) => handleInputChange('wakeup_sound', e.target.value)}
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
                value={editedData.speex_noise_suppression}
                onChange={(e) => handleInputChange('speex_noise_suppression', e.target.value)}
              />
            </div>
            <div className="form-field">
              <label>Microphone</label>
              <select
                value={editedData.mic_index}
                onChange={(e) => handleInputChange('mic_index', e.target.value)}
              >
                {microphones.map((mic, index) => (
                  <option key={index} value={index}>
                    {mic}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Speaker</label>
              <select
                value={editedData.speaker_index}
                onChange={(e) => handleInputChange('speaker_index', e.target.value)}
              >
                {speakers.map((speaker, index) => (
                  <option key={index} value={index}>
                    {speaker}
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
            <button type="button" className="save-button" onClick={handleSaveChanges}>
              Save Changes
            </button>
            <button
              type="button"
              className={`restart-button ${isRestarting ? 'disabled' : ''}`}
              onClick={handleRestart}
              disabled={isRestarting}
            >
              {isRestarting ? 'Restarting...' : 'Restart'}
            </button>
            <div className="notification-container">
              {errorNotification && (
                <div className="notification error-notification">{errorNotification}</div>
              )}
              {restartNotification && (
                <div className="notification info-notification">Node Restart Required!</div>
              )}
              {restartSuccessNotification && (
                <div className="notification success-notification">Node Restarted</div>
              )}
              {isSaved && (
                <div className="notification success-notification">Configuration Saved!</div>
              )}
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default Node;
