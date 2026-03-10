export interface Service {
  id: string;
  name: string;
  icon: string;
  price: number;
  priceUsd: number;
  category: 'social' | 'messenger' | 'other';
}

export interface Country {
  code: string;
  name: string;
  dialCode: string;
  flag: string;
}

export interface ActiveNumber {
  id: string;
  phoneNumber: string;
  serviceName: string;
  countryName: string;
  status: 'waiting' | 'received' | 'timeout';
  message: string | null;
  timestamp: number;
  expiresAt: number;
}

export enum SimulationState {
  IDLE = 'IDLE',
  GENERATING = 'GENERATING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED'
}

export interface CountryPrice {
  kes: number;
  usd: number;
}

export interface PricingMap {
  [serviceId: string]: {
    [countryCode: string]: CountryPrice;
  };
}

export type PaymentStatus = 'idle' | 'initiating' | 'pending' | 'confirmed' | 'failed';

export interface PaymentResult {
  status: PaymentStatus;
  payment_id?: number;
  checkout_request_id?: string;
  order_id?: string;
  phone_number?: string;
  error?: string;
  message?: string;
}
