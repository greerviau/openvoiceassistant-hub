// Node.js
import React, { useEffect, useState, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { capitalizeId } from '../Utils';

function Node() {
  const location = useLocation();
  const initialData = location.state?.jsonData;

  const [configData, setConfigData] = useState({});
  const [editedData, setEditedData] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newChanges, setNewChanges] = useState(false);
  const [infoNotification, setInfoNotification] = useState(null);
  const [successNotification, setSuccessNotification] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);
  const [isIdentifying, setIsIdentifying] = useState(false);
  const [isRestarting, setIsRestarting] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [microphones, setMicrophones] = useState([]);
  const [speakers, setSpeakers] = useState([]);
  const [wakeWords, setWakeWords] = useState([]);
  const [selectedWakeWord, setSelectedWakeWord] = useState(null);
  const [wakeWordFile, setWakeWordFile] = useState(null);
  const [logs, setLogs] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const terminalRef = useRef(null);

  useEffect(() => {
    handleLogRefresh();
    if (initialData) {
      fetch(`/api/node/${initialData.id}/config`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log(json)
        setConfigData(json);
        setEditedData(json);
        setSelectedWakeWord(json.wake_word);
      })
      .catch((error) => {
        console.error('Error fetching configuration data:', error);
        setErrorNotification(`${error.message}`);
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      })
      .finally(() => {
        setLoading(false);
      });

      fetch(`/api/node/${initialData.id}/hardware`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log(json)
        setMicrophones(json.microphones);
        setSpeakers(json.speakers);
      })
      .catch((error) => {
        console.error('Error fetching hardware data:', error);
        setErrorNotification(`${error.message}`);
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      });

      fetch(`/api/node/${initialData.id}/wake_words`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log(json)
        setWakeWords(json);
      })
      .catch((error) => {
        console.error('Error fetching wake word data:', error);
        setErrorNotification(`${error.message}`);
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      });
    }
  }, [initialData]);

  const handleIdentify = () => {
    setIsIdentifying(true);
  
    fetch(`/api/node/${initialData.id}/announce/Hello%20World`, {
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
    })
    .catch((error) => {
      console.error('Error initiating announcement:', error);
      setErrorNotification(`${error.message}`);
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    })
    .finally(() => {
      setIsIdentifying(false);
    });
  };

  const handleInputChange = (field, value) => {
    let typedValue = value;
    switch (typeof configData[field]) {
      case 'number':
        typedValue = parseFloat(value) || 0;
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
      [field]: !prevData[field],
    }));
    console.log(editedData);
  };

  const handleSaveChanges = () => {
    setSaving(true);
    const updateConfig = (data) => {
      fetch(`/api/node/${initialData.id}/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
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
        setSuccessNotification('Changes Saved');
        setTimeout(() => {
          setSuccessNotification(null);
        }, 3000);

        if (initialData.status !== 'offline') {
          setInfoNotification('Node Restart Required');
          setTimeout(() => {
            setInfoNotification(null);
          }, 3000);
        }

        setConfigData((prevData) => ({ ...prevData, restart_required: true }));
      })
      .catch((error) => {
        console.error('Error restarting node:', error);
        setErrorNotification(`${error.message}`);
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      })
      .finally(() => {
        setSaving(false);
      });
    };

    if (wakeWordFile) {
      const formData = new FormData();
      formData.append('wake_word_model', wakeWordFile);
      fetch(`/api/node/${initialData.id}/upload/wake_word_model`, {
        method: 'POST',
        body: formData,
      })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log('Wake Word Model uploaded:', json);
        console.log(selectedWakeWord);
        const data = { ...editedData, wake_word: selectedWakeWord, restart_required: true };
        updateConfig(data);
        setEditedData((prevData) => ({
          ...prevData,
          wake_word: selectedWakeWord,
        }));
      })
      .catch((error) => {
        console.error('Error uploading wake word:', error);
        setErrorNotification(`${error.message}`);
        // Clear the notification after a few seconds
        setTimeout(() => {
          setErrorNotification(null);
        }, 5000);
      });
    } else {
      const data = { ...editedData, restart_required: true };
      updateConfig(data);
    }
  };

  const handleRestart = () => {
    // Set the loading state to true
    setIsRestarting(true);

    // API call to restart node
    fetch(`/api/node/${initialData.id}/restart`, {
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

  const handleUpdate = () => {
    setIsUpdating(true);

    fetch(`/api/node/${initialData.id}/update`, {
      method: 'POST',
    })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      console.log('Node updated:', json);
      setSuccessNotification('Node Updated');
      setTimeout(() => {
        setSuccessNotification(null);
      }, 3000);
    })
    .catch((error) => {
      console.error('Error updating node:', error);
      setErrorNotification(`${error.message}`);
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    })
    .finally(() => {
      setIsUpdating(null);
    });
  };

  const handleWakeWordOptionChange = (e) => {
    const newSelectedWakeWord = e.target.value;

    if (newSelectedWakeWord === 'file-upload') {
      // If the selected option is 'file-upload', trigger file upload
      document.getElementById('file-upload-input').click();
      return;
    }

    setSelectedWakeWord(newSelectedWakeWord);
    setEditedData((prevData) => ({
      ...prevData,
      wake_word: newSelectedWakeWord,
    }));
    setNewChanges(true);
  };

  const handleWakeWordUploadSelection = (file) => {
    if (!file) {
      return;
    }
    setWakeWordFile(file);
    const fileName = file.name.replace(/.onnx/g, '');
    console.log(fileName);
    setWakeWords((prevData) => [...prevData, fileName]);
    setSelectedWakeWord(fileName);
    setNewChanges(true);
  };

  const handleLogRefresh = () => {
    setIsRefreshing(true);

    fetch(`/api/node/${initialData.id}/logs`, {
      method: 'GET',
    })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((json) => {
      console.log('Node logs:', json);
      setLogs(json);
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    })
    .catch((error) => {
      console.error('Error updating node:', error);
      setErrorNotification(`${error.message}`);
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    })
    .finally(() => {
      setIsRefreshing(false);
    });
  };

  if (!initialData) {
    return <div>No data found for this node.</div>;
  }

  return (
    <div>
      <div className="node-header">
        <h1>{initialData.name}</h1>
        {initialData.status === 'online' && (
          <button
            style={{marginLeft: "10px"}}
            className={`info-button ${isRestarting || initialData.status === 'offline' ? 'disabled' : ''}`}
            onClick={handleRestart}
            disabled={isRestarting}
          >
            {isRestarting ? 'Restarting...' : 'Restart'}
          </button>
        )}
        {initialData.status === 'online' && (
        <button
          style={{marginLeft: "10px"}}
          className={`submit-button ${isIdentifying || initialData.status !== 'online' ? 'disabled' : ''}`}
          onClick={handleIdentify}
          disabled={isIdentifying || initialData.status !== 'online'}
        >
          {isIdentifying ? 'Identifying...' : 'Identify'}
        </button>
        )}
        {initialData.update_available && initialData.status !== 'offline' && (
          <button
            style={{marginLeft: "10px"}}
            className={`update-button ${isUpdating ? 'disabled' : ''}`}
            onClick={(e) => {
              e.stopPropagation();
              handleUpdate(initialData.id, initialData.name);
            }}
            disabled={isUpdating}
          >
            {isUpdating ? 'Updating...' : 'Update'}
          </button>
        )}
      </div>
      <div className="page-container">
        <Link to="/nodes" className="big-info-button">
          Back
        </Link>
        {loading ? (
          <p style={{ paddingTop: "30px" }}>Loading data...</p>
        ) : (
          <div style={{ paddingTop: "30px", display: 'flex' }}>
            <div style={{ flex: 1, width: "300px"}}>
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
                  <label>Wake Word</label>
                  <select
                    className="dropdown"
                    value={selectedWakeWord}
                    onChange={handleWakeWordOptionChange}
                  >
                    {wakeWords.map((wakeWord, index) => (
                      <option key={index} value={wakeWord}>
                        {capitalizeId(wakeWord)}
                      </option>
                    ))}
                    <option value="file-upload">Upload Wake Word</option>
                  </select>
                </div>
                <input
                  id="file-upload-input"
                  type="file"
                  accept=".onnx"
                  onChange={(e) => handleWakeWordUploadSelection(e.target.files[0])}
                  style={{ display: 'none' }}
                />
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
                    disabled={!configData.speex_available}
                  />
                </div>
                <div className="form-field">
                  <label>Omni Directional Wake Word</label>
                  <input
                    type="checkbox"
                    checked={editedData.omni_directional_wake_word}
                    onChange={(e) => handleCheckboxChange('omni_directional_wake_word')}
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
                    className={`submit-button ${(!newChanges || saving) ? 'disabled' : ''}`} 
                    disabled={(!newChanges || saving)} 
                    onClick={handleSaveChanges}>
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
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
            <div style={{ flex: 2, width: "600px"}}>
              <div className="node-header">
                <h2 style={{paddingRight: "10px"}}>Logs</h2>
                <button 
                  className={`info-button ${isRefreshing ? 'disabled' : ''}`}
                  onClick={handleLogRefresh}
                  disabled={isRefreshing}
                >
                  Refresh
                </button>
              </div>
              <div className="terminal" ref={terminalRef}>
                {logs.map((log, index) => (
                    <p key={index} dangerouslySetInnerHTML={{ __html: log }} />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Node;
