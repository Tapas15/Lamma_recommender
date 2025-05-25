"use client";
import React, { useState, useEffect, ReactNode } from 'react';
import { useI18n } from '../providers/i18n-provider';

interface TranslatableContentProps {
  content: {
    en: ReactNode;
    ar: ReactNode;
  };
  fallback?: ReactNode;
}

export default function TranslatableContent({ content, fallback }: TranslatableContentProps) {
  const { language } = useI18n();
  const [currentContent, setCurrentContent] = useState<ReactNode>(null);
  
  useEffect(() => {
    // Set content based on current language
    setCurrentContent(content[language] || fallback || content.en);
  }, [content, language, fallback]);
  
  // Listen for translate-all event
  useEffect(() => {
    const handleTranslateAll = (event: Event) => {
      const customEvent = event as CustomEvent<{ language: string }>;
      if (customEvent.detail && customEvent.detail.language === language) {
        // Force refresh the content
        setCurrentContent(null);
        setTimeout(() => {
          setCurrentContent(content[language] || fallback || content.en);
        }, 0);
      }
    };
    
    document.addEventListener('translate-all', handleTranslateAll);
    return () => {
      document.removeEventListener('translate-all', handleTranslateAll);
    };
  }, [content, language, fallback]);
  
  return <>{currentContent}</>;
} 