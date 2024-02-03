import React, { useState, useEffect } from 'react';
import './App.css';
import { BrowserRouter, Route, Routes, Link} from 'react-router-dom';
import Sidebar from './components/Sidebar.jsx';
import Overview from './pages/Overview.jsx';
import Nodes from './pages/Nodes.jsx';
import Node from './pages/Node.jsx';
import Skills from './pages/Skills.jsx';
import ImportSkill from './pages/ImportSkill.jsx'
import Skill from './pages/Skill.jsx'
import Settings from './pages/Settings.jsx';
import Logs from './pages/Logs.jsx';

const App = () => {

  return (
    <BrowserRouter>
      <Sidebar>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/overview" element={<Overview />} />
          <Route path="/nodes" element={<Nodes />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/import-skill" element={<ImportSkill />} />
          <Route path="/skill/:skillId" element={<Skill />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/node/:nodeId" element={<Node />} />
        </Routes>
      </Sidebar>
    </BrowserRouter>
  );
};

export default App;