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
