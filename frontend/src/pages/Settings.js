import React, { useState, useEffect } from 'react';
import { Accordion } from "../components/Accordion";

const Settings = () => {

    const [data, setData] = useState([{}]);
    const [components, setComponents] = useState([{}]);
    useEffect(() => {
      fetch('/config').then(
        res => res.json()
      ).then(
        d => {
          setData(d)
          setComponents(d.components)
          console.log(d)
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
                <Accordion label='transcriber' data={components?.transcriber} />
                <Accordion label='understander' data={components?.understander} />
                <Accordion label='synthesizer' data={components?.synthesizer} />
            </div>
        </div>
    );
};

export default Settings;