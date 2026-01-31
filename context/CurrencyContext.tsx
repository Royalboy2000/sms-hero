import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Service } from '../types';

type Currency = 'KES' | 'USD';

interface CurrencyContextType {
  currency: Currency;
  toggleCurrency: () => void;
  formatPrice: (service: Service) => string;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

export const CurrencyProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currency, setCurrency] = useState<Currency>('KES');

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
    <CurrencyContext.Provider value={{ currency, toggleCurrency, formatPrice }}>
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
