"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { translateHtml, isTranslationAvailable } from '@/lib/translate';
import { translateAllImages, toggleImageTranslations } from '@/lib/imageTranslate';
import { Globe, Loader2, GripVertical, MoveIcon } from 'lucide-react';

export default function FloatingTranslateButton() {
  const [isTranslating, setIsTranslating] = useState(false);
  const [isTranslated, setIsTranslated] = useState(false);
  const [isAvailable, setIsAvailable] = useState(false);
  const [position, setPosition] = useState({ x: 20, y: 20 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const buttonRef = useRef<HTMLDivElement>(null);
  
  // Load saved position from localStorage on component mount
  useEffect(() => {
    try {
      const savedPosition = localStorage.getItem('translationButtonPosition');
      if (savedPosition) {
        setPosition(JSON.parse(savedPosition));
      }
    } catch (error) {
      console.error('Error loading saved position:', error);
    }
    
    // Check translation state from localStorage
    try {
      const savedTranslationState = localStorage.getItem('isPageTranslated');
      if (savedTranslationState === 'true') {
        setIsTranslated(true);
        // We'll need to re-apply translation when the page loads
        setTimeout(() => {
          translatePage();
        }, 500);
      }
    } catch (error) {
      console.error('Error loading translation state:', error);
    }
  }, []);
  
  // Check if translation service is available
  useEffect(() => {
    const checkTranslationService = async () => {
      const available = await isTranslationAvailable();
      setIsAvailable(available);
    };
    
    checkTranslationService();
  }, []);

  // Handle mouse down for dragging
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!buttonRef.current) return;
    
    setIsDragging(true);
    const rect = buttonRef.current.getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
    
    // Prevent text selection during drag
    e.preventDefault();
  };

  // Handle mouse move for dragging
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      
      // Calculate new position
      const newX = Math.max(0, Math.min(e.clientX - dragOffset.x, window.innerWidth - 100));
      const newY = Math.max(0, Math.min(e.clientY - dragOffset.y, window.innerHeight - 100));
      
      // Update position
      setPosition({ x: newX, y: newY });
    };

    const handleMouseUp = () => {
      if (isDragging) {
        setIsDragging(false);
        
        // Save position to localStorage
        try {
          localStorage.setItem('translationButtonPosition', JSON.stringify(position));
        } catch (error) {
          console.error('Error saving position:', error);
        }
      }
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset, position]);
  
  // Function to translate the entire page
  const translatePage = async () => {
    if (isTranslating) return;
    
    setIsTranslating(true);
    
    try {
      // Get the document body
      const body = document.body;
      
      // Save the original HTML if not already translated
      if (!isTranslated) {
        body.setAttribute('data-original-html', body.innerHTML);
        
        // Save the original button HTML to restore it later
        if (buttonRef.current) {
          const buttonHtml = buttonRef.current.outerHTML;
          body.setAttribute('data-button-html', buttonHtml);
        }
      } else {
        // If already translated, revert to original
        const originalHtml = body.getAttribute('data-original-html');
        if (originalHtml) {
          body.innerHTML = originalHtml;
          
          // Save translation state to localStorage
          localStorage.setItem('isPageTranslated', 'false');
          
          setIsTranslated(false);
          setIsTranslating(false);
          return;
        }
      }
      
      // Get HTML content
      const htmlContent = body.innerHTML;
      
      // Translate HTML content
      const translatedHtml = await translateHtml(htmlContent, 'en', 'ar');
      
      // Update the content with translated text
      body.innerHTML = translatedHtml;
      
      // Restore the floating button
      const buttonHtml = body.getAttribute('data-button-html');
      if (buttonHtml) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = buttonHtml;
        const newButton = tempDiv.firstChild;
        if (newButton) {
          body.appendChild(newButton);
        }
      }
      
      // Add RTL direction for Arabic
      body.setAttribute('dir', isTranslated ? 'ltr' : 'rtl');
      
      // Handle image translations
      if (!isTranslated) {
        // Translate images when switching to Arabic
        await translateAllImages();
        
        // Save translation state to localStorage
        localStorage.setItem('isPageTranslated', 'true');
      } else {
        // Toggle image translations when switching back to English
        toggleImageTranslations(true);
        
        // Save translation state to localStorage
        localStorage.setItem('isPageTranslated', 'false');
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
    <div 
      ref={buttonRef}
      className="fixed z-50 flex flex-col items-center bg-white dark:bg-gray-900 rounded-lg shadow-lg p-2 border border-gray-200 dark:border-gray-700"
      style={{ 
        left: `${position.x}px`, 
        top: `${position.y}px`,
        cursor: isDragging ? 'grabbing' : 'auto',
        transition: isDragging ? 'none' : 'all 0.2s ease'
      }}
    >
      <div 
        className="flex items-center justify-center w-full mb-2 cursor-grab hover:bg-gray-100 dark:hover:bg-gray-800 rounded p-1"
        onMouseDown={handleMouseDown}
        title="Drag to move"
      >
        <MoveIcon className="h-4 w-4 text-gray-400" />
      </div>
      <Button
        onClick={translatePage}
        variant="outline"
        size="sm"
        className="w-full"
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
    </div>
  );
} 