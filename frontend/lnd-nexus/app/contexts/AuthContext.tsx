'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi, UserProfile, ApiError } from '../services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserProfile | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Check if user is already authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('auth_token');
      if (storedToken) {
        try {
          setIsLoading(true);
          const userProfile = await authApi.getProfile(storedToken);
          setUser(userProfile);
          setToken(storedToken);
          setIsAuthenticated(true);
          setError(null);
        } catch (err) {
          // Token might be expired or invalid
          console.error('Authentication error:', err);
          localStorage.removeItem('auth_token');
          setIsAuthenticated(false);
          setUser(null);
          setToken(null);
          
          if (err instanceof ApiError) {
            setError(err.message);
          } else {
            setError('Authentication failed. Please log in again.');
          }
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const tokenResponse = await authApi.login({ username: email, password });
      const userProfile = await authApi.getProfile(tokenResponse.access_token);
      
      // Save token to localStorage
      localStorage.setItem('auth_token', tokenResponse.access_token);
      
      setToken(tokenResponse.access_token);
      setUser(userProfile);
      setIsAuthenticated(true);
    } catch (err) {
      console.error('Login error:', err);
      
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Login failed. Please check your credentials and try again.');
      }
      
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('auth_token');
    setIsAuthenticated(false);
    setUser(null);
    setToken(null);
    setError(null);
  };

  const value = {
    isAuthenticated,
    isLoading,
    user,
    token,
    login,
    logout,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 