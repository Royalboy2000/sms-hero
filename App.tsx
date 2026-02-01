import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import { CurrencyProvider } from './context/CurrencyContext';

const App = () => {
  return (
    <CurrencyProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/app" element={<Dashboard />} />
            <Route path="/services/:serviceId" element={<Dashboard />} />
            <Route path="/countries/:countryId" element={<Dashboard />} />
            <Route path="/buy/:serviceId/:countryId" element={<Dashboard />} />
          </Routes>
        </Layout>
      </Router>
    </CurrencyProvider>
  );
};

export default App;