import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';
import QuarterReport from './pages/QuarterReport';
import TestMap from './pages/TestMap';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/quarter-report" element={<QuarterReport />} />
        <Route path="/test-map" element={<TestMap />} />
      </Routes>
    </Router>
  );
}

export default App;
