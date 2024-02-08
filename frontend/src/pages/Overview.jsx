import React, { useState } from 'react';

const Overview = () => {
  const [textInput, setTextInput] = useState('');
  const [textInputChange, setTextInputChange] = useState(false);
  const [responseText, setResponseText] = useState('');
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [errorNotification, setErrorNotification] = useState(null);

  const handleRecord = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      setMediaRecorder(mediaRecorder);
      const audioChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        audioChunks.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);
        sendAudioData(audioBlob);
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setErrorNotification(`${error.message}`);
      setTimeout(() => {
        setErrorNotification(null);
      }, 5000);
    }
  };

  const sendAudioData = async (audioBlob) => {
    const formData = new FormData();
    formData.append('audio_file', audioBlob);
    try {
        const response = await fetch('/api/respond/audio_file', {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            throw new Error('Failed to submit text');
        }
        const jsonHeaders = response.headers.get('X-JSON-Data');
        const jsonData = jsonHeaders ? JSON.parse(jsonHeaders) : {};

        console.log(jsonData);

        setTextInput(jsonData.command);
        setResponseText(jsonData.response);
        setTextInputChange(false);

        const audioBlob = await response.blob();
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
    } catch (error) {
        console.error('Error sending audio to API:', error);
        setErrorNotification(`${error.message}`);
        setTimeout(() => {
        setErrorNotification(null);
        }, 5000);
    }
  };

  const handleStop = async () => {
    if (mediaRecorder && recording) {
      mediaRecorder.stop();
      setRecording(false);
    }
  };

  const handleSubmit = async () => {
    const response = await fetch('/api/respond/text', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command_text: textInput })
    });
    if (!response.ok) {
        throw new Error('Failed to submit text');
    }
    try {
        const jsonHeaders = response.headers.get('X-JSON-Data');
        const jsonData = jsonHeaders ? JSON.parse(jsonHeaders) : {};

        console.log(jsonData);

        setTextInput(jsonData.command);
        setResponseText(jsonData.response);
        setTextInputChange(false);

        const audioBlob = await response.blob();
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
    } catch(error) {
        console.error('Error sending text to API:', error);
        setErrorNotification(`${error.message}`);
        setTimeout(() => {
        setErrorNotification(null);
        }, 5000);
    }
  }
  
  const handlePlayAudio = () => {
    if (audioUrl) {
        const audioElement = new Audio(audioUrl);
        audioElement.play();
    }
  };

  const handleTextInput = (e) => {
    setTextInput(e.target.value);
    setTextInputChange(true);
  };

  return (
    <div>
        <h1>Overview</h1>
        <div className="page-container">
            <h2>Testing</h2>
            <div style={{marginTop: "10px"}}>
                <input
                className="overview-field"
                type="text"
                value={textInput}
                onChange={(e) => handleTextInput(e)}
                placeholder="Enter your text"
                />
                <button 
                    className="record-button" 
                    style={{marginLeft: "30px"}} 
                    onClick={recording ? handleStop : handleRecord}>
                    {recording ? 'Stop' : 'Record'}
                </button>
                <button 
                    className={`big-submit-button ${!textInputChange | !textInput ? 'disabled' : ''}`}
                    style={{marginLeft: "10px"}} 
                    onClick={handleSubmit}
                    disabled={!textInputChange | !textInput}>Confirm</button>
            </div>
            <div>
                <input
                className="overview-field"
                type="text"
                value={responseText}
                readOnly
                />
                <button    
                    className={`big-info-button ${!audioUrl ? 'disabled' : ''}`}
                    style={{marginLeft: "30px"}} 
                    onClick={handlePlayAudio}
                    disabled={!audioUrl}>Play Audio</button>
            </div>
        </div>
        <div className="notification-container">
        {errorNotification && (
          <div className="notification error-notification">{errorNotification}</div>
        )}
      </div>
    </div>
  );
};

export default Overview;
