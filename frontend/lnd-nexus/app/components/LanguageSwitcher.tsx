"use client";
import { useState, useEffect } from 'react';
import { useI18n, Language } from '../providers/i18n-provider';
import { Button } from './ui/button';
import { Globe, RefreshCw, Loader2 } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from './ui/dropdown-menu';
import { translateHtml, isTranslationAvailable } from '@/lib/translate';
import { translateAllImages, toggleImageTranslations } from '@/lib/imageTranslate';

export default function LanguageSwitcher() {
  const { language, setLanguage, t, translateAll } = useI18n();
  const [isOpen, setIsOpen] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [isTranslated, setIsTranslated] = useState(false);
  const [translationAvailable, setTranslationAvailable] = useState(false);
  const [progress, setProgress] = useState(0);

  // Check if translation service is available
  useEffect(() => {
    const checkTranslationService = async () => {
      try {
        const available = await isTranslationAvailable();
        setTranslationAvailable(available);
      } catch (error) {
        console.error('Error checking translation service:', error);
        setTranslationAvailable(false);
      }
    };
    
    checkTranslationService();
  }, []);

  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    setIsOpen(false);
  };

  const handleTranslateAll = () => {
    translateAll();
    setIsOpen(false);
  };

  // Find the main content container
  const findContentContainer = (): Element | null => {
    // Try different content containers in order of preference
    const selectors = [
      'main', // Standard main tag
      '[role="main"]', // Elements with role="main"
      '#__next > div', // Next.js app structure
      '.page-content', // Common content class
      '#root > div', // React app structure
      'body > div > div' // Fallback for simple layouts
    ];
    
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        return element;
      }
    }
    
    // Fallback to body if no suitable container found
    return document.body;
  };

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

  // Function to translate the page
  const translatePage = async () => {
    if (isTranslating) return;
    
    setIsTranslating(true);
    setProgress(0);
    setIsOpen(false);
    
    try {
      // Get main content using the flexible finder
      const contentContainer = findContentContainer();
      
      if (!contentContainer) {
        console.error('Content container not found');
        setIsTranslating(false);
        return;
      }
      
      if (!isTranslated) {
        // Apply RTL direction for Arabic
        contentContainer.setAttribute('dir', 'rtl');
        
        // Translate text nodes progressively
        await translateTextNodesProgressively(contentContainer, 'en', 'ar');
        
        // Handle image translations in the background
        translateAllImages().catch(error => {
          console.error('Error translating images:', error);
        });
        
        setIsTranslated(true);
      } else {
        // Revert to original content
        revertTranslations(contentContainer);
        
        // Toggle image translations
        toggleImageTranslations(true);
        
        // Reset direction
        contentContainer.setAttribute('dir', 'ltr');
        
        setIsTranslated(false);
      }
    } catch (error) {
      console.error('Error translating page:', error);
    } finally {
      setIsTranslating(false);
      setProgress(0);
    }
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="flex items-center gap-1 text-slate-700 hover:text-blue-700 hover:bg-blue-50 rounded-md border-blue-200"
          disabled={isTranslating}
        >
          {isTranslating ? (
            <>
              <Loader2 className="h-4 w-4 mr-1 animate-spin" />
              <span className="hidden sm:inline">{progress > 0 ? `${progress}%` : t('language.translating')}</span>
            </>
          ) : (
            <>
              <Globe className="h-4 w-4" />
              <span className="hidden sm:inline">{language === 'en' ? 'English' : 'العربية'}</span>
            </>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem
          className={`flex items-center gap-2 ${language === 'en' ? 'bg-blue-50 text-blue-700' : ''}`}
          onClick={() => handleLanguageChange('en')}
        >
          <span className="w-6 text-center">🇺🇸</span>
          <span>{t('language.english')}</span>
        </DropdownMenuItem>
        <DropdownMenuItem
          className={`flex items-center gap-2 ${language === 'ar' ? 'bg-blue-50 text-blue-700' : ''}`}
          onClick={() => handleLanguageChange('ar')}
        >
          <span className="w-6 text-center">🇸🇦</span>
          <span>{t('language.arabic')}</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        {translationAvailable && (
          <DropdownMenuItem 
            className="flex items-center gap-2 text-blue-600"
            onClick={translatePage}
          >
            <RefreshCw className="h-4 w-4" />
            <span>{isTranslated ? t('language.view_in_english') : t('language.view_in_arabic')}</span>
          </DropdownMenuItem>
        )}
        <DropdownMenuItem 
          className="flex items-center gap-2 text-blue-600"
          onClick={handleTranslateAll}
        >
          <RefreshCw className="h-4 w-4" />
          <span>{t('language.translate_all')}</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 