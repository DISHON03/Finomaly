import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from '../types';
import { api } from '../api/client';
import { useNotification } from './NotificationContext';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name: string) => Promise<void>;
  demoLogin: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const { notify } = useNotification();

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('finomaly_token') || localStorage.getItem('spendsense_token');
      if (token) {
        try {
          const me = await api.getMe();
          setUser(me);
        } catch {
          api.logout();
          setUser(null);
        }
      } else {
        setUser(null);
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await api.login(email, password);
      setUser(res.user);
      notify('success', 'Welcome Back!', `Logged in as ${res.user.full_name}`);
    } catch (err: any) {
      notify('error', 'Login Failed', err.message || 'Invalid credentials');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, full_name: string) => {
    setIsLoading(true);
    try {
      const res = await api.register(email, password, full_name);
      setUser(res.user);
      notify('success', 'Account Created', `Welcome to Finomaly, ${res.user.full_name}!`);
    } catch (err: any) {
      notify('error', 'Registration Failed', err.message || 'Could not create account');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const demoLogin = async () => {
    setIsLoading(true);
    try {
      const res = await api.demoLogin();
      setUser(res.user);
      notify('info', 'Demo Profile Active', 'Loaded realistic multi-year personal banking & credit card portfolio data.');
    } catch (err: any) {
      notify('error', 'Demo Initialization Failed', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
    notify('info', 'Logged Out', 'You have been signed out.');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        demoLogin,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
