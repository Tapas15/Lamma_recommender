# Translation Memory Bank

## Overview

The Translation Memory Bank is an enhancement to the integrated translation system that stores previously translated phrases to improve performance, consistency, and reduce API calls to the translation service. This document provides a walkthrough for implementing this feature.

## Benefits

1. **Improved Performance**
   - Reduced API calls to translation service
   - Faster translation of repeated content
   - Lower bandwidth usage

2. **Translation Consistency**
   - Same phrases always translated the same way
   - Consistent terminology across the application
   - Better user experience with predictable translations

3. **Reduced Server Load**
   - Fewer requests to LibreTranslate service
   - Less computational overhead on the server
   - More scalable translation system

## Implementation Walkthrough

### Step 1: Create the Memory Bank Store

First, create a new file `translationMemory.ts` in the `lib` directory:

```typescript
/**
 * Translation Memory Bank
 * Stores and retrieves previously translated phrases
 */

// Memory structure for storing translations
interface TranslationMemory {
  [sourceLanguage: string]: {
    [targetLanguage: string]: {
      [sourceText: string]: string;
    };
  };
}

// In-memory storage
let memoryBank: TranslationMemory = {};

// Local storage key
const STORAGE_KEY = 'translation_memory_bank';

/**
 * Initialize the memory bank from localStorage if available
 */
export function initMemoryBank(): void {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      memoryBank = JSON.parse(stored);
    }
  } catch (error) {
    console.error('Error loading translation memory:', error);
    memoryBank = {};
  }
}

/**
 * Save the current memory bank to localStorage
 */
export function saveMemoryBank(): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(memoryBank));
  } catch (error) {
    console.error('Error saving translation memory:', error);
  }
}

/**
 * Store a translation in the memory bank
 */
export function storeTranslation(
  sourceText: string,
  translatedText: string,
  sourceLanguage: string = 'en',
  targetLanguage: string = 'ar'
): void {
  // Initialize language objects if they don't exist
  if (!memoryBank[sourceLanguage]) {
    memoryBank[sourceLanguage] = {};
  }
  
  if (!memoryBank[sourceLanguage][targetLanguage]) {
    memoryBank[sourceLanguage][targetLanguage] = {};
  }
  
  // Store the translation
  memoryBank[sourceLanguage][targetLanguage][sourceText] = translatedText;
  
  // Save to localStorage (throttled to prevent excessive writes)
  throttledSave();
}

/**
 * Retrieve a translation from the memory bank
 * Returns null if the translation is not found
 */
export function retrieveTranslation(
  sourceText: string,
  sourceLanguage: string = 'en',
  targetLanguage: string = 'ar'
): string | null {
  try {
    return memoryBank[sourceLanguage]?.[targetLanguage]?.[sourceText] || null;
  } catch (error) {
    return null;
  }
}

/**
 * Clear the memory bank
 */
export function clearMemoryBank(): void {
  memoryBank = {};
  localStorage.removeItem(STORAGE_KEY);
}

/**
 * Get statistics about the memory bank
 */
export function getMemoryStats(): { totalEntries: number, languagePairs: string[] } {
  let totalEntries = 0;
  const languagePairs: string[] = [];
  
  Object.keys(memoryBank).forEach(srcLang => {
    Object.keys(memoryBank[srcLang]).forEach(tgtLang => {
      const entries = Object.keys(memoryBank[srcLang][tgtLang]).length;
      totalEntries += entries;
      languagePairs.push(`${srcLang}-${tgtLang} (${entries})`);
    });
  });
  
  return { totalEntries, languagePairs };
}

// Throttle save operations to prevent excessive localStorage writes
let saveTimeout: NodeJS.Timeout | null = null;
function throttledSave(): void {
  if (saveTimeout) {
    clearTimeout(saveTimeout);
  }
  
  saveTimeout = setTimeout(() => {
    saveMemoryBank();
    saveTimeout = null;
  }, 2000);
}

// Initialize the memory bank when the module loads
if (typeof window !== 'undefined') {
  initMemoryBank();
}
```

### Step 2: Update the Translation Utilities

Modify the `translate.ts` file to use the memory bank:

```typescript
import { retrieveTranslation, storeTranslation } from './translationMemory';

/**
 * Translates text from one language to another using LibreTranslate
 * with memory bank support
 */
export async function translateText(text: string, source: string = 'en', target: string = 'ar') {
  try {
    // Check if we already have this translation in memory
    const cachedTranslation = retrieveTranslation(text, source, target);
    if (cachedTranslation) {
      return cachedTranslation;
    }
    
    // If not in memory, call the API
    const response = await fetch(`${LIBRETRANSLATE_URL}/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        q: text,
        source: source,
        target: target,
        format: 'text',
      }),
    });

    if (!response.ok) {
      throw new Error(`Translation failed with status: ${response.status}`);
    }

    const data = await response.json();
    const translatedText = data.translatedText;
    
    // Store in memory bank for future use
    storeTranslation(text, translatedText, source, target);
    
    return translatedText;
  } catch (error) {
    console.error('Translation error:', error);
    return text; // Return original text on error
  }
}

// Similar update for translateHtml function...
```

### Step 3: Create a Memory Bank Management Component

Create a component to manage the translation memory:

```typescript
// components/TranslationMemoryManager.tsx
"use client";

import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { 
  getMemoryStats, 
  clearMemoryBank, 
  saveMemoryBank 
} from '@/lib/translationMemory';

export default function TranslationMemoryManager() {
  const [stats, setStats] = useState({ totalEntries: 0, languagePairs: [] as string[] });
  
  useEffect(() => {
    updateStats();
  }, []);
  
  const updateStats = () => {
    setStats(getMemoryStats());
  };
  
  const handleClearMemory = () => {
    if (confirm('Are you sure you want to clear the translation memory? This cannot be undone.')) {
      clearMemoryBank();
      updateStats();
    }
  };
  
  const handleSaveMemory = () => {
    saveMemoryBank();
    alert('Translation memory saved successfully.');
  };
  
  return (
    <div className="p-4 border rounded-md">
      <h2 className="text-lg font-semibold mb-2">Translation Memory</h2>
      
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          Total entries: <span className="font-medium">{stats.totalEntries}</span>
        </p>
        <p className="text-sm text-gray-600">
          Language pairs: 
        </p>
        <ul className="text-sm list-disc pl-5">
          {stats.languagePairs.map((pair, index) => (
            <li key={index}>{pair}</li>
          ))}
        </ul>
      </div>
      
      <div className="flex space-x-2">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleSaveMemory}
        >
          Save Memory
        </Button>
        <Button 
          variant="outline" 
          size="sm" 
          className="text-red-600 hover:bg-red-50"
          onClick={handleClearMemory}
        >
          Clear Memory
        </Button>
      </div>
    </div>
  );
}
```

### Step 4: Enhance the LanguageSwitcher Component

Update the `LanguageSwitcher.tsx` component to use the memory bank for translating text nodes:

```typescript
// Add import for translation memory
import { retrieveTranslation, storeTranslation } from '@/lib/translationMemory';

// Update the translateTextNodesProgressively function
const translateTextNodesProgressively = async (element: Element, source: string, target: string) => {
  // ... existing code ...
  
  // Process batch in parallel
  await Promise.all(batch.map(async (el) => {
    if (!el.hasAttribute('data-original-text') && el.textContent && el.textContent.trim()) {
      // Store original text
      const originalText = el.textContent.trim();
      el.setAttribute('data-original-text', originalText);
      
      try {
        // Check memory bank first
        let translatedText = retrieveTranslation(originalText, source, target);
        
        // If not in memory, translate via API
        if (!translatedText) {
          translatedText = await translateHtml(el.innerHTML, source, target);
          
          // Store in memory bank
          if (translatedText && originalText !== translatedText) {
            storeTranslation(originalText, translatedText, source, target);
          }
        }
        
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
  
  // ... existing code ...
};
```

### Step 5: Create an Admin Page for Translation Memory

Create a new page for managing the translation memory:

```typescript
// app/admin/translation-memory/page.tsx
"use client";

import React from 'react';
import TranslationMemoryManager from '@/app/components/TranslationMemoryManager';

export default function TranslationMemoryPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Translation Memory Management</h1>
      
      <div className="grid gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Memory Bank Status</h2>
          <TranslationMemoryManager />
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">About Translation Memory</h2>
          <p className="mb-4">
            Translation memory stores previously translated phrases to improve performance,
            consistency, and reduce API calls to the translation service.
          </p>
          <h3 className="text-lg font-medium mb-2">Benefits:</h3>
          <ul className="list-disc pl-5 space-y-1 mb-4">
            <li>Faster translations for repeated content</li>
            <li>Consistent terminology across the application</li>
            <li>Reduced server load and bandwidth usage</li>
            <li>Improved user experience with quicker translations</li>
          </ul>
          <p className="text-sm text-gray-600">
            The translation memory is stored in your browser's local storage.
            Clearing your browser data will reset the translation memory.
          </p>
        </div>
      </div>
    </div>
  );
}
```

### Step 6: Add Memory Bank Statistics to the Language Switcher

Enhance the LanguageSwitcher to show memory usage statistics:

```typescript
// Add to LanguageSwitcher.tsx
import { getMemoryStats } from '@/lib/translationMemory';

// Add state for memory stats
const [memoryStats, setMemoryStats] = useState({ totalEntries: 0 });

// Update stats when dropdown opens
const handleDropdownOpen = (open: boolean) => {
  setIsOpen(open);
  if (open) {
    setMemoryStats(getMemoryStats());
  }
};

// In the return statement, update the DropdownMenu
<DropdownMenu open={isOpen} onOpenChange={handleDropdownOpen}>
  {/* ... existing code ... */}
  
  {/* Add memory stats at the bottom */}
  <DropdownMenuSeparator />
  <div className="px-2 py-1 text-xs text-gray-500">
    Translation memory: {memoryStats.totalEntries} phrases
  </div>
</DropdownMenu>
```

## Performance Considerations

### Memory Usage

The translation memory is stored in the browser's localStorage, which has a limit of about 5MB. To prevent excessive memory usage:

1. **Limit Entry Size**: Only store translations for text under a certain length (e.g., 1000 characters)
2. **Implement Pruning**: When the memory reaches a certain size, remove older or less frequently used entries
3. **Compress Data**: Consider compressing the data before storing in localStorage

### Code Example for Memory Pruning:

```typescript
// Add to translationMemory.ts

const MAX_ENTRIES = 5000; // Maximum number of entries to store

// Add usage tracking
interface TranslationEntry {
  text: string;
  lastUsed: number;
  useCount: number;
}

// Modified memory structure
interface TranslationMemory {
  [sourceLanguage: string]: {
    [targetLanguage: string]: {
      [sourceText: string]: TranslationEntry;
    };
  };
}

// Function to prune memory when it gets too large
function pruneMemoryIfNeeded(): void {
  let totalEntries = 0;
  
  // Count entries
  Object.keys(memoryBank).forEach(srcLang => {
    Object.keys(memoryBank[srcLang]).forEach(tgtLang => {
      totalEntries += Object.keys(memoryBank[srcLang][tgtLang]).length;
    });
  });
  
  // If we're over the limit, prune
  if (totalEntries > MAX_ENTRIES) {
    // Collect all entries with their metadata
    const allEntries: Array<{
      srcLang: string;
      tgtLang: string;
      text: string;
      entry: TranslationEntry;
    }> = [];
    
    Object.keys(memoryBank).forEach(srcLang => {
      Object.keys(memoryBank[srcLang]).forEach(tgtLang => {
        Object.keys(memoryBank[srcLang][tgtLang]).forEach(text => {
          allEntries.push({
            srcLang,
            tgtLang,
            text,
            entry: memoryBank[srcLang][tgtLang][text]
          });
        });
      });
    });
    
    // Sort by least recently used and lowest use count
    allEntries.sort((a, b) => {
      // First compare use count
      if (a.entry.useCount !== b.entry.useCount) {
        return a.entry.useCount - b.entry.useCount;
      }
      // If equal, compare last used timestamp
      return a.entry.lastUsed - b.entry.lastUsed;
    });
    
    // Remove 20% of entries (oldest and least used)
    const entriesToRemove = Math.floor(totalEntries * 0.2);
    for (let i = 0; i < entriesToRemove && i < allEntries.length; i++) {
      const entry = allEntries[i];
      delete memoryBank[entry.srcLang][entry.tgtLang][entry.text];
    }
    
    // Save the pruned memory bank
    saveMemoryBank();
  }
}
```

## Testing the Memory Bank

To test the translation memory bank:

1. Translate a page with repeated phrases
2. Observe the network requests - subsequent translations should not generate API calls
3. Check the memory statistics to see the number of stored translations
4. Clear the memory and observe that translations now require API calls again

## Conclusion

The Translation Memory Bank significantly improves the performance and consistency of translations across the application. By storing previously translated phrases, it reduces the need for repeated API calls, provides faster translations, and ensures consistent terminology.

Implement this feature to enhance the user experience, especially for users who frequently switch between languages or visit pages with similar content. 