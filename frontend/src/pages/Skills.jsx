import React, { useState, useEffect } from 'react';

const Skills = () => {
    const [data, setData] = useState([{}]);
    useEffect(() => {
      fetch('/skills/active').then(
        res => res.json()
      ).then(
        d => {
          console.log(d)
          setData(d)
        }
      )
    }, []);

    return (
        <div>
            <h1>Skills</h1>
            <div className='item-list'>
                {Object.keys(data).map((id) => (
                    <div className='item-container'>
                        <div className='item-name'>{data[id]}</div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Skills;