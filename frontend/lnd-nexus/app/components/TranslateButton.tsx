"use client";

import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { translateHtml, isTranslationAvailable } from '@/lib/translate';
import { translateAllImages, toggleImageTranslations } from '@/lib/imageTranslate';
import { Globe, Loader2 } from 'lucide-react';

interface TranslateButtonProps {
  className?: string;
}

export default function TranslateButton({ className }: TranslateButtonProps) {
  const [isTranslating, setIsTranslating] = useState(false);
  const [isTranslated, setIsTranslated] = useState(false);
  const [isAvailable, setIsAvailable] = useState(false);
  
  // Check if translation service is available
  useEffect(() => {
    const checkTranslationService = async () => {
      const available = await isTranslationAvailable();
      setIsAvailable(available);
    };
    
    checkTranslationService();
  }, []);
  
  // Function to translate the entire page
  const translatePage = async () => {
    if (isTranslating) return;
    
    setIsTranslating(true);
    
    try {
      // Get all text nodes in the body
      const mainContent = document.querySelector('main');
      
      if (!mainContent) {
        console.error('Main content not found');
        setIsTranslating(false);
        return;
      }
      
      // Save the original HTML if not already translated
      if (!isTranslated) {
        mainContent.setAttribute('data-original-html', mainContent.innerHTML);
      } else {
        // If already translated, revert to original
        const originalHtml = mainContent.getAttribute('data-original-html');
        if (originalHtml) {
          mainContent.innerHTML = originalHtml;
          setIsTranslated(false);
          setIsTranslating(false);
          return;
        }
      }
      
      // Get HTML content
      const htmlContent = mainContent.innerHTML;
      
      // Translate HTML content
      const translatedHtml = await translateHtml(htmlContent, 'en', 'ar');
      
      // Update the content with translated text
      mainContent.innerHTML = translatedHtml;
      
      // Add RTL direction for Arabic
      mainContent.setAttribute('dir', isTranslated ? 'ltr' : 'rtl');
      
      // Handle image translations
      if (!isTranslated) {
        // Translate images when switching to Arabic
        await translateAllImages();
      } else {
        // Toggle image translations when switching back to English
        toggleImageTranslations(true);
      }
      
      // Toggle translation state
      setIsTranslated(!isTranslated);
    } catch (error) {
      console.error('Error translating page:', error);
    } finally {
      setIsTranslating(false);
    }
  };
  
  if (!isAvailable) return null;
  
  return (
    <Button
      onClick={translatePage}
      variant="outline"
      size="sm"
      className={className}
      disabled={isTranslating}
    >
      {isTranslating ? (
        <>
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          Translating...
        </>
      ) : (
        <>
          <Globe className="h-4 w-4 mr-2" />
          {isTranslated ? 'View in English' : 'عرض بالعربية'}
        </>
      )}
    </Button>
  );
} 