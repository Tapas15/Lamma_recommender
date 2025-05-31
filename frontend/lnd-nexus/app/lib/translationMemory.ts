// Translation memory system for caching translations locally

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
export function getMemoryStats(): { totalEntries: number; languagePairs: string[] } {
  const memory = getTranslationMemory();
  const entries = Array.from(memory.values());

  if (entries.length === 0) {
    return {
      totalEntries: 0,
      languagePairs: []
    };
  }

  const languagePairs = Array.from(new Set(
    entries.map(e => `${e.sourceLanguage} → ${e.targetLanguage}`)
  ));

  return {
    totalEntries: entries.length,
    languagePairs
  };
}

/**
 * Clear all translation memory
 */
export function clearMemoryBank(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
    console.log('Translation memory cleared');
  } catch (error) {
    console.error('Error clearing translation memory:', error);
  }
}

/**
 * Save memory bank to a file (download)
 */
export function saveMemoryBank(): void {
  try {
    const memory = getTranslationMemory();
    const data = JSON.stringify(Object.fromEntries(memory), null, 2);
    
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `translation-memory-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    console.log('Translation memory saved to file');
  } catch (error) {
    console.error('Error saving translation memory:', error);
  }
}
