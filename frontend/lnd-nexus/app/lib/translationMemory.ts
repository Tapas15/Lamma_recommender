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
