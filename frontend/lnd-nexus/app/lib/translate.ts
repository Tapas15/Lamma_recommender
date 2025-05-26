// Translation utility functions for LibreTranslate integration

const LIBRETRANSLATE_URL = process.env.NEXT_PUBLIC_LIBRETRANSLATE_URL || 'http://localhost:5000';
const FALLBACK_MODE = process.env.NEXT_PUBLIC_TRANSLATION_FALLBACK_MODE === 'true';

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
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const response = await fetch(`${LIBRETRANSLATE_URL}/languages`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    return response.ok;
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        console.warn('Translation service check timed out - service may not be running');
      } else {
        console.warn('Translation service not available:', error.message);
      }
    } else {
      console.warn('Translation service not available:', String(error));
    }
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

  // Check if translation service is available first
  if (FALLBACK_MODE || !(await isTranslationAvailable())) {
    console.warn('Translation service not available, returning original HTML');
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

  // Check if translation service is available first
  if (FALLBACK_MODE || !(await isTranslationAvailable())) {
    console.warn('Translation service not available, returning original text');
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
