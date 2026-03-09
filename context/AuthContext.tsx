import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  username: string;
}

interface Quota {
  allowed: number;
  used: number;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  quota: Quota | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  refreshQuota: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [quota, setQuota] = useState<Quota | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('smskenya_token');
    const savedUser = localStorage.getItem('smskenya_user');
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
      fetchMe(savedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchMe = async (authToken: string) => {
    try {
      const response = await fetch('/api/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setQuota(data.quota);
      } else if (response.status === 401) {
        logout();
      }
    } catch (error) {
      console.error('Failed to fetch user data', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem('smskenya_token', newToken);
    localStorage.setItem('smskenya_user', JSON.stringify(newUser));
    fetchMe(newToken);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setQuota(null);
    localStorage.removeItem('smskenya_token');
    localStorage.removeItem('smskenya_user');
  };

  const refreshQuota = async () => {
    if (token) {
      await fetchMe(token);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, quota, login, logout, refreshQuota, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
