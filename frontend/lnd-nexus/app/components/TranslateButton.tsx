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
  const [progress, setProgress] = useState(0);
  
  // Check if translation service is available
  useEffect(() => {
    const checkTranslationService = async () => {
      const available = await isTranslationAvailable();
      setIsAvailable(available);
    };
    
    checkTranslationService();
  }, []);
  
  // Function to translate text nodes progressively
  const translateTextNodesProgressively = async (element: Element, source: string, target: string) => {
    // Get all text-containing elements
    const textElements = Array.from(element.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, a, button, li, label, div:not(:has(*))'))
      .filter(el => el.textContent && el.textContent.trim().length > 0);
    
    const totalElements = textElements.length;
    let processedElements = 0;
    
    // Process elements in small batches to keep the UI responsive
    const batchSize = 5;
    for (let i = 0; i < totalElements; i += batchSize) {
      const batch = textElements.slice(i, i + batchSize);
      
      // Process batch in parallel
      await Promise.all(batch.map(async (el) => {
        if (!el.hasAttribute('data-original-text') && el.textContent && el.textContent.trim()) {
          // Store original text
          el.setAttribute('data-original-text', el.textContent);
          
          try {
            // Translate the text content
            const translatedText = await translateHtml(el.innerHTML, source, target);
            
            // Update the element with translated text
            el.innerHTML = translatedText;
            
            // Mark as translated
            el.setAttribute('data-translated', 'true');
          } catch (error) {
            console.error('Error translating element:', error);
          }
        }
        
        processedElements++;
        setProgress(Math.round((processedElements / totalElements) * 100));
      }));
      
      // Small delay to keep UI responsive
      await new Promise(resolve => setTimeout(resolve, 10));
    }
  };
  
  // Function to revert translations
  const revertTranslations = (element: Element) => {
    // Find all translated elements
    const translatedElements = element.querySelectorAll('[data-translated="true"]');
    
    translatedElements.forEach(el => {
      const originalText = el.getAttribute('data-original-text');
      if (originalText) {
        el.innerHTML = originalText;
      }
      el.removeAttribute('data-translated');
    });
  };
  
  // Function to translate the entire page
  const translatePage = async () => {
    if (isTranslating) return;
    
    setIsTranslating(true);
    setProgress(0);
    
    try {
      // Get main content
      const mainContent = document.querySelector('main');
      
      if (!mainContent) {
        console.error('Main content not found');
        setIsTranslating(false);
        return;
      }
      
      if (!isTranslated) {
        // Apply RTL direction for Arabic
        mainContent.setAttribute('dir', 'rtl');
        
        // Translate text nodes progressively
        await translateTextNodesProgressively(mainContent, 'en', 'ar');
        
        // Handle image translations in the background
        translateAllImages().catch(error => {
          console.error('Error translating images:', error);
        });
        
        setIsTranslated(true);
      } else {
        // Revert to original content
        revertTranslations(mainContent);
        
        // Toggle image translations
        toggleImageTranslations(true);
        
        // Reset direction
        mainContent.setAttribute('dir', 'ltr');
        
        setIsTranslated(false);
      }
    } catch (error) {
      console.error('Error translating page:', error);
    } finally {
      setIsTranslating(false);
      setProgress(0);
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
          {progress > 0 ? `${progress}%` : 'Translating...'}
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