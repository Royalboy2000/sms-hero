import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import Layout from './components/Layout';
import LandingPage from './components/LandingPage';
import CatalogModal from './components/CatalogModal';
import { CurrencyProvider } from './context/CurrencyContext';

const AppContent = () => {
  const [isCatalogOpen, setIsCatalogOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Extract params from path
  const pathParts = location.pathname.split('/');
  let initialServiceId: string | undefined = undefined;
  let initialCountryId: string | undefined = undefined;

  if (pathParts[1] === 'services') initialServiceId = pathParts[2];
  if (pathParts[1] === 'countries') initialCountryId = pathParts[2];
  if (pathParts[1] === 'buy') {
    initialServiceId = pathParts[2];
    initialCountryId = pathParts[3];
  }

  useEffect(() => {
    if (['/app', '/services', '/countries', '/buy'].some(p => location.pathname.startsWith(p))) {
      setIsCatalogOpen(true);
    } else {
      setIsCatalogOpen(false);
    }
  }, [location.pathname]);

  const handleCloseCatalog = () => {
    setIsCatalogOpen(false);
    navigate('/');
  };

  return (
    <Layout>
      <Routes>
        <Route path="*" element={<LandingPage />} />
      </Routes>
      <CatalogModal
        isOpen={isCatalogOpen}
        onClose={handleCloseCatalog}
        initialServiceId={initialServiceId}
        initialCountryId={initialCountryId}
      />
    </Layout>
  );
};

const App = () => {
  return (
    <CurrencyProvider>
      <Router>
        <AppContent />
      </Router>
    </CurrencyProvider>
  );
};

export default App;
