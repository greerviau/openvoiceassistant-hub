import React, { useState, useEffect } from 'react';
import './App.css';
import { BrowserRouter, Route, Routes, Link} from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import Nodes from './pages/Nodes.jsx';
import Skills from './pages/Skills.jsx';
import Settings from './pages/Settings.jsx';
import Logs from './pages/Logs.jsx';
import Skill from './pages/Skill'

const App = () => {

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
    <BrowserRouter>
      <Sidebar>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/overview" element={<Overview />} />
          <Route path="/nodes" element={<Nodes />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/logs" element={<Logs />} />
        </Routes>
      </Sidebar>

      {skills.map((skill) => (<Link to={'skills/' + skill} />))}
      <Routes>
        <Route path="skills/:skill" element={<Skill/>} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;