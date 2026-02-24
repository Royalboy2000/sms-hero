import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Service } from '../types';

type Currency = 'KES' | 'USD';

interface CurrencyContextType {
  currency: Currency;
  toggleCurrency: () => void;
  formatPrice: (service: Service) => string;
  detectedCountry: string | null;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

export const CurrencyProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currency, setCurrency] = useState<Currency>('KES');
  const [detectedCountry, setDetectedCountry] = useState<string | null>(null);

  React.useEffect(() => {
    const detectLocation = async () => {
      try {
        const response = await fetch('https://ipapi.co/json/');
        const data = await response.json();
        if (data.country_code) {
          setDetectedCountry(data.country_code);
          if (data.country_code === 'KE') {
            setCurrency('KES');
          } else {
            setCurrency('USD');
          }
        }
      } catch (error) {
        console.error('Error detecting location:', error);
      }
    };
    detectLocation();
  }, []);

  const toggleCurrency = () => {
    setCurrency(prev => prev === 'KES' ? 'USD' : 'KES');
  };

  const formatPrice = (service: Service) => {
    if (currency === 'KES') {
      return `KSh ${service.price.toLocaleString()}`;
    } else {
      return `$${service.priceUsd.toLocaleString()}`;
    }
  };

  return (
    <CurrencyContext.Provider value={{ currency, toggleCurrency, formatPrice, detectedCountry }}>
      {children}
    </CurrencyContext.Provider>
  );
};

export const useCurrency = () => {
  const context = useContext(CurrencyContext);
  if (context === undefined) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return context;
};
