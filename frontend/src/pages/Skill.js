import React, { useState, useEffect } from 'react';

const Skill = () => {
    const skill = this.props.match.params.skill

    const [config, setConfig] = useState([{}]);
    useEffect(() => {
      fetch(`/skills/${skill}/config`).then(
        res => res.json()
      ).then(
        data => {
          console.log(data)
          setConfig(data)
        }
      )
    }, []);

    return (
        <div>
            <h1>{skill}</h1>
        </div>
    );
};

export default Skill;