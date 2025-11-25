import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import QuarterReport from './pages/QuarterReport';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/quarter-report" element={<QuarterReport />} />
      </Routes>
    </Router>
  );
}

export default App;
