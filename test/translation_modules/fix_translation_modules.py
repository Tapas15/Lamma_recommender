#!/usr/bin/env python
"""
Fix script to create missing translation modules and setup frontend environment
"""
import os
import sys

def create_lib_directory():
    """Create the lib directory if it doesn't exist"""
    lib_path = os.path.join("frontend", "lnd-nexus", "app", "lib")
    if not os.path.exists(lib_path):
        os.makedirs(lib_path, exist_ok=True)
        print(f"✓ Created lib directory: {lib_path}")
    return lib_path

def create_translate_module(lib_path):
    """Create the translate.ts module"""
    translate_content = '''// Translation utility functions for LibreTranslate integration

const LIBRETRANSLATE_URL = process.env.NEXT_PUBLIC_LIBRETRANSLATE_URL || 'http://localhost:5000';

export interface TranslationResponse {
  translatedText: string;
}

export interface LanguageInfo {
  code: string;
  name: string;
}

/**
 * Check if LibreTranslate service is available
 */
export async function isTranslationAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${LIBRETRANSLATE_URL}/languages`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.ok;
  } catch (error) {
    console.error('Translation service check failed:', error);
    return false;
  }
}

/**
 * Translate HTML content while preserving structure
 */
export async function translateHtml(
  html: string,
  sourceLanguage: string = 'en',
  targetLanguage: string = 'ar'
): Promise<string> {
  if (!html || html.trim() === '') {
    return html;
  }

  try {
    const response = await fetch(`${LIBRETRANSLATE_URL}/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        q: html,
        source: sourceLanguage,
        target: targetLanguage,
        format: 'html'
      }),
    });

    if (!response.ok) {
      throw new Error(`HTML translation failed: ${response.statusText}`);
    }

    const result: TranslationResponse = await response.json();
    return result.translatedText || html;
  } catch (error) {
    console.error('HTML translation error:', error);
    return html; // Return original HTML if translation fails
  }
}

/**
 * Translate text using LibreTranslate
 */
export async function translateText(
  text: string,
  sourceLanguage: string = 'en',
  targetLanguage: string = 'ar'
): Promise<string> {
  if (!text || text.trim() === '') {
    return text;
  }

  try {
    const response = await fetch(`${LIBRETRANSLATE_URL}/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        q: text,
        source: sourceLanguage,
        target: targetLanguage,
        format: 'text'
      }),
    });

    if (!response.ok) {
      throw new Error(`Translation failed: ${response.statusText}`);
    }

    const result: TranslationResponse = await response.json();
    return result.translatedText || text;
  } catch (error) {
    console.error('Translation error:', error);
    return text; // Return original text if translation fails
  }
}
'''
    
    file_path = os.path.join(lib_path, "translate.ts")
    with open(file_path, "w") as f:
        f.write(translate_content)
    print(f"✓ Created translate.ts: {file_path}")

def create_image_translate_module(lib_path):
    """Create the imageTranslate.ts module"""
    image_translate_content = '''// Image translation utilities using Tesseract.js for OCR and LibreTranslate for translation

import { translateText } from './translate';

export interface ImageTranslationResult {
  originalText: string;
  translatedText: string;
  confidence: number;
}

/**
 * Extract text from an image using OCR (simplified version)
 */
export async function extractTextFromImage(
  imageElement: HTMLImageElement,
  language: string = 'eng'
): Promise<{ text: string; confidence: number }> {
  try {
    // For now, return empty result as Tesseract.js might not be available
    // This can be enhanced when Tesseract.js is properly loaded
    console.log('OCR functionality requires Tesseract.js to be properly loaded');
    return { text: '', confidence: 0 };
  } catch (error) {
    console.error('OCR extraction failed:', error);
    return { text: '', confidence: 0 };
  }
}

/**
 * Translate all images on the page (placeholder implementation)
 */
export async function translateAllImages(
  sourceLanguage: string = 'en',
  targetLanguage: string = 'ar'
): Promise<void> {
  console.log('Image translation feature is available but requires Tesseract.js setup');
  // Placeholder implementation
}

/**
 * Toggle image translations on/off
 */
export function toggleImageTranslations(show: boolean = true): void {
  console.log('Image translation toggle:', show);
  // Placeholder implementation
}
'''
    
    file_path = os.path.join(lib_path, "imageTranslate.ts")
    with open(file_path, "w") as f:
        f.write(image_translate_content)
    print(f"✓ Created imageTranslate.ts: {file_path}")

def create_translation_memory_module(lib_path):
    """Create the translationMemory.ts module"""
    memory_content = '''// Translation memory system for caching translations locally

export interface TranslationEntry {
  id: string;
  originalText: string;
  translatedText: string;
  sourceLanguage: string;
  targetLanguage: string;
  timestamp: number;
  useCount: number;
  lastUsed: number;
}

export interface MemoryStats {
  totalEntries: number;
  totalSize: number;
  oldestEntry: number;
  newestEntry: number;
  mostUsedEntry: TranslationEntry | null;
}

const STORAGE_KEY = 'translation_memory';
const MAX_ENTRIES = 1000;
const MAX_TEXT_LENGTH = 1000;

/**
 * Generate a unique ID for a translation entry
 */
function generateEntryId(originalText: string, sourceLanguage: string, targetLanguage: string): string {
  const combined = `${originalText}_${sourceLanguage}_${targetLanguage}`;
  let hash = 0;
  for (let i = 0; i < combined.length; i++) {
    const char = combined.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(36);
}

/**
 * Get all translation entries from localStorage
 */
function getTranslationMemory(): Map<string, TranslationEntry> {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return new Map();
    }
    const data = JSON.parse(stored);
    return new Map(Object.entries(data));
  } catch (error) {
    console.error('Error loading translation memory:', error);
    return new Map();
  }
}

/**
 * Save translation memory to localStorage
 */
function saveTranslationMemory(memory: Map<string, TranslationEntry>): void {
  try {
    const data = Object.fromEntries(memory);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (error) {
    console.error('Error saving translation memory:', error);
  }
}

/**
 * Store a translation in memory
 */
export function storeTranslation(
  originalText: string,
  translatedText: string,
  sourceLanguage: string,
  targetLanguage: string
): void {
  if (!originalText || !translatedText || originalText.length > MAX_TEXT_LENGTH) {
    return;
  }

  if (originalText.trim() === translatedText.trim()) {
    return;
  }

  const memory = getTranslationMemory();
  const id = generateEntryId(originalText, sourceLanguage, targetLanguage);
  const now = Date.now();

  const existingEntry = memory.get(id);
  
  if (existingEntry) {
    existingEntry.useCount += 1;
    existingEntry.lastUsed = now;
    existingEntry.translatedText = translatedText;
  } else {
    const newEntry: TranslationEntry = {
      id,
      originalText,
      translatedText,
      sourceLanguage,
      targetLanguage,
      timestamp: now,
      useCount: 1,
      lastUsed: now
    };
    memory.set(id, newEntry);
  }

  saveTranslationMemory(memory);
}

/**
 * Retrieve a translation from memory
 */
export function retrieveTranslation(
  originalText: string,
  sourceLanguage: string,
  targetLanguage: string
): string | null {
  if (!originalText || originalText.length > MAX_TEXT_LENGTH) {
    return null;
  }

  const memory = getTranslationMemory();
  const id = generateEntryId(originalText, sourceLanguage, targetLanguage);
  const entry = memory.get(id);

  if (entry) {
    entry.useCount += 1;
    entry.lastUsed = Date.now();
    saveTranslationMemory(memory);
    return entry.translatedText;
  }

  return null;
}

/**
 * Get memory statistics
 */
export function getMemoryStats(): MemoryStats {
  const memory = getTranslationMemory();
  const entries = Array.from(memory.values());

  if (entries.length === 0) {
    return {
      totalEntries: 0,
      totalSize: 0,
      oldestEntry: 0,
      newestEntry: 0,
      mostUsedEntry: null
    };
  }

  const totalSize = JSON.stringify(Object.fromEntries(memory)).length;
  const timestamps = entries.map(e => e.timestamp);
  const oldestEntry = Math.min(...timestamps);
  const newestEntry = Math.max(...timestamps);
  const mostUsedEntry = entries.reduce((prev, current) => 
    (prev.useCount > current.useCount) ? prev : current
  );

  return {
    totalEntries: entries.length,
    totalSize,
    oldestEntry,
    newestEntry,
    mostUsedEntry
  };
}
'''
    
    file_path = os.path.join(lib_path, "translationMemory.ts")
    with open(file_path, "w") as f:
        f.write(memory_content)
    print(f"✓ Created translationMemory.ts: {file_path}")

def setup_frontend_env():
    """Create .env.local file for Next.js frontend"""
    frontend_path = os.path.join("frontend", "lnd-nexus")
    
    if not os.path.exists(frontend_path):
        print("Frontend directory not found, skipping environment setup.")
        return False
    
    env_file_path = os.path.join(frontend_path, ".env.local")
    
    env_content = """# Next.js Environment Variables
# These variables are available in the browser (prefixed with NEXT_PUBLIC_)

# LibreTranslate API URL
NEXT_PUBLIC_LIBRETRANSLATE_URL=http://localhost:5000

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
"""
    
    try:
        with open(env_file_path, "w") as f:
            f.write(env_content)
        print(f"✓ Created frontend environment file: {env_file_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to create frontend environment file: {str(e)}")
        return False

def main():
    """Main function to fix all translation modules"""
    print("Fixing Translation Modules")
    print("=" * 50)
    
    frontend_app_path = os.path.join("frontend", "lnd-nexus", "app")
    
    if not os.path.exists(frontend_app_path):
        print(f"✗ Frontend app directory not found: {frontend_app_path}")
        print("Please ensure the Next.js frontend is properly set up.")
        return False
    
    try:
        # Create lib directory
        lib_path = create_lib_directory()
        
        # Create translation modules
        create_translate_module(lib_path)
        create_image_translate_module(lib_path)
        create_translation_memory_module(lib_path)
        
        # Setup frontend environment
        setup_frontend_env()
        
        print("\n" + "=" * 50)
        print("✓ All translation modules have been created successfully!")
        print("✓ Frontend environment variables have been configured!")
        print("\nYou can now restart your Next.js development server.")
        return True
        
    except Exception as e:
        print(f"\n✗ Error fixing translation modules: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 