import React, { useState, useEffect } from 'react';

const Nodes = () => {
    const [data, setData] = useState([{}]);
    useEffect(() => {
      fetch('/node/status').then(
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
            <h1>Nodes</h1>
            <div className='item-list'>
                {Object.keys(data).map((node_id) => (
                    <div className='item-container'>
                        <div className='item-name'>{data[node_id].name}</div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Nodes;