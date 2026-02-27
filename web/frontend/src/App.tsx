import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import QuarterReport from './pages/QuarterReport';
import ComparisonView from './components/ComparisonView';
import { installDelegatedLinkTracking, trackPageView } from './lib/analytics';

const AnalyticsTracker = () => {
  const location = useLocation();

  useEffect(() => {
    const cleanup = installDelegatedLinkTracking();
    return cleanup;
  }, []);

  useEffect(() => {
    trackPageView(`${location.pathname}${location.search}`);
  }, [location.pathname, location.search]);

  return null;
};

function App() {
  return (
    <Router>
      <AnalyticsTracker />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/quarter-report" element={<QuarterReport />} />
        <Route path="/comparison" element={<ComparisonView />} />
      </Routes>
    </Router>
  );
}

export default App;
