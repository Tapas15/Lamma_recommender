"use client";
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Define supported languages
export type Language = 'en' | 'ar';

// Define the context type
type LanguageContextType = {
  language: Language;
  setLanguage: (language: Language) => void;
  t: (key: string) => string;
  isRTL: boolean;
};

// Create the context with default values
const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key: string) => key,
  isRTL: false,
});

// English translations
const enTranslations: Record<string, string> = {
  // Navigation
  'nav.home': 'Home',
  'nav.professionals': 'Professionals',
  'nav.jobs': 'Jobs',
  'nav.resources': 'Resources',
  'nav.community': 'Community',
  'nav.signin': 'Sign In',
  'nav.register': 'Register',
  'nav.dashboard': 'Dashboard',
  'nav.logout': 'Logout',
  
  // Common actions
  'action.search': 'Search',
  'action.apply': 'Apply',
  'action.save': 'Save',
  'action.submit': 'Submit',
  'action.cancel': 'Cancel',
  'action.edit': 'Edit',
  'action.delete': 'Delete',
  
  // Language switcher
  'language.english': 'English',
  'language.arabic': 'العربية',
};

// Arabic translations
const arTranslations: Record<string, string> = {
  // Navigation
  'nav.home': 'الرئيسية',
  'nav.professionals': 'المحترفين',
  'nav.jobs': 'الوظائف',
  'nav.resources': 'الموارد',
  'nav.community': 'المجتمع',
  'nav.signin': 'تسجيل الدخول',
  'nav.register': 'التسجيل',
  'nav.dashboard': 'لوحة التحكم',
  'nav.logout': 'تسجيل الخروج',
  
  // Common actions
  'action.search': 'بحث',
  'action.apply': 'تقديم',
  'action.save': 'حفظ',
  'action.submit': 'إرسال',
  'action.cancel': 'إلغاء',
  'action.edit': 'تعديل',
  'action.delete': 'حذف',
  
  // Language switcher
  'language.english': 'English',
  'language.arabic': 'العربية',
};

// All translations
const translations: Record<Language, Record<string, string>> = {
  en: enTranslations,
  ar: arTranslations,
};

// Provider component
export function LanguageProvider({ children }: { children: ReactNode }) {
  // Try to get saved language from localStorage, default to 'en'
  const [language, setLanguageState] = useState<Language>('en');
  const isRTL = language === 'ar';

  // Set up effect to load saved language preference
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language') as Language;
    if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'ar')) {
      setLanguageState(savedLanguage);
    }
  }, []);

  // Set up effect to apply RTL direction when language changes
  useEffect(() => {
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }, [language, isRTL]);

  // Function to set language and save to localStorage
  const setLanguage = (newLanguage: Language) => {
    setLanguageState(newLanguage);
    localStorage.setItem('language', newLanguage);
  };

  // Translation function
  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, isRTL }}>
      {children}
    </LanguageContext.Provider>
  );
}

// Custom hook to use the language context
export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
} 