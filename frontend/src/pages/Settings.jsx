import React, { useState, useEffect } from 'react';
import { Accordion } from "../components/Accordion";

const Settings = () => {

    const [data, setData] = useState([{}]);
    const [components, setComponents] = useState([{}]);
    useEffect(() => {
      fetch('/config').then(
        res => res.json()
      ).then(
        data => {
          setData(data)
          setComponents(data.components)
          console.log(data)
        }
      )
    }, []);

    return (
        <div>
            <h1>Settings</h1>
            <label>Wake word: </label>
            <input placeholder={data.wake_word}/>
            
            <button>Save</button>
            <div>
                <Accordion label='Transcriber' data={components?.transcriber} />
                <Accordion label='Understander' data={components?.understander} />
                <Accordion label='Synthesizer' data={components?.synthesizer} />
            </div>
        </div>
    );
};

export default Settings;