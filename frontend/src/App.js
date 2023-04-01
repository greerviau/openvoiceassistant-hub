import React from 'react';
import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import Nodes from './pages/Nodes.jsx';
import Skills from './pages/Skills.jsx';
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
          <Route path="/settings" element={<Settings />} />
          <Route path="/logs" element={<Logs />} />
        </Routes>
      </Sidebar>
    </BrowserRouter>
  );
};

export default App;