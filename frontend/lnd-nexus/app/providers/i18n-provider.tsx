"use client";
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import i18next from 'i18next';
import { initReactI18next, useTranslation } from 'react-i18next';

// Import language files
import enTranslations from '../locales/en.json';
import arTranslations from '../locales/ar.json';

// Initialize i18next
i18next
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: enTranslations },
      ar: { translation: arTranslations }
    },
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

// Define supported languages
export type Language = 'en' | 'ar';

// Define the context type
type I18nContextType = {
  language: Language;
  setLanguage: (language: Language) => void;
  t: (key: string, options?: any) => string;
  tImage: (key: string) => string;
  isRTL: boolean;
  translateAll: () => void;
};

// Create the context with default values
const I18nContext = createContext<I18nContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key: string) => key,
  tImage: (key: string) => '',
  isRTL: false,
  translateAll: () => {},
});

// Image translations
const imageTranslations: Record<Language, Record<string, string>> = {
  en: {
    'logo': '/images/en/logo.png',
    'hero.banner': '/images/en/hero-banner.jpg',
    'cta.banner': '/images/en/cta-banner.jpg',
  },
  ar: {
    'logo': '/images/ar/logo.png',
    'hero.banner': '/images/ar/hero-banner.jpg',
    'cta.banner': '/images/ar/cta-banner.jpg',
  },
};

// Provider component
export function I18nProvider({ children }: { children: ReactNode }) {
  // Get i18next translation function
  const { t: translate, i18n } = useTranslation();
  
  // Try to get saved language from localStorage, default to 'en'
  const [language, setLanguageState] = useState<Language>('en');
  const isRTL = language === 'ar';

  // Set up effect to load saved language preference
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language') as Language;
    if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'ar')) {
      setLanguageState(savedLanguage);
      i18n.changeLanguage(savedLanguage);
    }
  }, [i18n]);

  // Set up effect to apply RTL direction when language changes
  useEffect(() => {
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }, [language, isRTL]);

  // Function to set language and save to localStorage
  const setLanguage = (newLanguage: Language) => {
    setLanguageState(newLanguage);
    i18n.changeLanguage(newLanguage);
    localStorage.setItem('language', newLanguage);
    // Force reload all translatable images
    translateAll();
  };

  // Translation function for text
  const t = (key: string, options?: any): string => {
    const result = translate(key, options);
    return typeof result === 'string' ? result : key;
  };

  // Translation function for images
  const tImage = (key: string): string => {
    return imageTranslations[language][key] || '';
  };

  // Function to trigger translation of all content (including images)
  const translateAll = () => {
    // This function will be called when language changes
    // It dispatches a custom event that components can listen for
    const event = new CustomEvent('translate-all', { detail: { language } });
    document.dispatchEvent(event);
  };

  return (
    <I18nContext.Provider value={{ language, setLanguage, t, tImage, isRTL, translateAll }}>
      {children}
    </I18nContext.Provider>
  );
}

// Custom hook to use the language context
export function useI18n() {
  const context = useContext(I18nContext);
  if (context === undefined) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
} 