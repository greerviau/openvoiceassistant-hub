import React, { useState, useEffect } from 'react';
import Skill from './Skill'
import {Routes, Route, useNavigate, BrowserRouter, Link} from 'react-router-dom';


const Skills = () => {
  const navigate = useNavigate();

  const navigateToSkill = (skill) => {
    // 👇️ navigate to /contacts
    navigate(`/skills/${skill}`);
  };

    const [skills, setSkills] = useState([]);
    useEffect(() => {
      fetch('/skills/active').then(
        res => res.json()
      ).then(
        data => {
          console.log(data)
          setSkills(data)
        }
      )
    }, []);

    return (
        <div>
            <h1>Skills</h1>
            <div className='item-list'>
            {skills.map((skill) => (
              <button
                onClick={navigateToSkill(skill)}
              >{skill}</button>
            ))}
            </div>
        </div>
    );
};

export default Skills;