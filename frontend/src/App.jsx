import React from 'react';
import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Sidebar from './components/Sidebar.jsx';
import Overview from './pages/Overview.jsx';
import Nodes from './pages/Nodes.jsx';
import Node from './pages/Node.jsx';
import Skills from './pages/Skills.jsx';
import Skill from './pages/Skill.jsx'
import ImportSkill from './pages/ImportSkill.jsx'
import Integrations from './pages/Integrations.jsx';
import Integration from './pages/Integration.jsx'
import ImportIntegration from './pages/ImportIntegration.jsx'
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
          <Route path="/node/:nodeId" element={<Node />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/skill/:skillId" element={<Skill />} />
          <Route path="/import-skill" element={<ImportSkill />} />
          <Route path="/integrations" element={<Integrations />} />
          <Route path="/integration/:integrationId" element={<Integration />} />
          <Route path="/import-integration" element={<ImportIntegration />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/logs" element={<Logs />} />
        </Routes>
      </Sidebar>
    </BrowserRouter>
  );
};

export default App;