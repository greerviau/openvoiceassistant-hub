import React, { useState, useEffect } from 'react';
import './App.css';
import { BrowserRouter, Route, Routes, Link} from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import Nodes from './pages/Nodes.js';
import Node from './pages/Node.js';
import Skills from './pages/Skills.js';
import Settings from './pages/Settings.js';
import Logs from './pages/Logs.js';
import Skill from './pages/Skill'

const App = () => {

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
          <Route path="/node/:fieldName" element={<Node />} />
        </Routes>
      </Sidebar>
    </BrowserRouter>
  );
};

export default App;