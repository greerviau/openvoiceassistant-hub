import React, { useEffect, useState, useRef } from 'react';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const terminalRef = useRef(null);
  const [isScrolledToBottom, setIsScrolledToBottom] = useState(true);

  useEffect(() => {
    const ws = new WebSocket(`ws:127.0.0.1:7123/ws/log`);

    ws.onmessage = (event) => {
      setLogs([event.data]); // Append new log to existing logs
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, []);

  useEffect(() => {
    if (isScrolledToBottom) {
      scrollToBottom();
    }
  }, [logs, isScrolledToBottom]);

  const scrollToBottom = () => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  };

  const handleScroll = () => {
    if (
      terminalRef.current &&
      terminalRef.current.scrollHeight - terminalRef.current.scrollTop ===
        terminalRef.current.clientHeight
    ) {
      setIsScrolledToBottom(true);
    } else {
      setIsScrolledToBottom(false);
    }
  };

  return (
    <div>
        <h1>Logs</h1>
        <div className="page-container">
            <div className="terminal" ref={terminalRef} onScroll={handleScroll}>
            {logs.map((log, index) => (
                <p key={index} dangerouslySetInnerHTML={{ __html: log }} />
            ))}
            </div>
        </div>
    </div>
  );
};

export default Logs;
