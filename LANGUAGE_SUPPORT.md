# Language Support Implementation

## Overview

The Job Recommender Application now supports multiple languages, with initial support for English and Arabic. This document provides information on how language support is implemented across the application.

## Features

- **Multilingual UI**: The frontend supports switching between English and Arabic
- **RTL Support**: Automatic Right-to-Left layout for Arabic language
- **Language Persistence**: User language preference is stored in localStorage
- **Backend Translation**: Backend API responses can be translated based on language preference
- **API Language Selection**: Language can be selected via Accept-Language header or lang query parameter

## Implementation Details

### Frontend Implementation

1. **Language Context**:
   - Located in `frontend/lnd-nexus/app/contexts/LanguageContext.tsx`
   - Provides language state management across the application
   - Includes translation functions and RTL detection

2. **Language Switcher Component**:
   - Located in `frontend/lnd-nexus/app/components/LanguageSwitcher.tsx`
   - Dropdown menu for selecting language
   - Visual indication of current language

3. **Integration with Layout**:
   - The LanguageProvider wraps the application in `frontend/lnd-nexus/app/layout.tsx`
   - Automatically applies RTL direction for Arabic language

4. **Translation Usage**:
   - Components use the `t()` function from the language context to translate text
   - Example: `{t('nav.home')}` instead of hardcoded "Home"

### Backend Implementation

1. **Language Middleware**:
   - Located in `backend/utils/language_middleware.py`
   - Detects user language preference from headers or query parameters
   - Sets language in request state for use in API endpoints

2. **Translation Files**:
   - English translations: `backend/utils/translations/en.json`
   - Arabic translations: `backend/utils/translations/ar.json`
   - Structured key-value pairs for consistent translation

3. **API Endpoints**:
   - Language selection endpoint: `GET /languages`
   - Translation endpoint: `GET /translate/{key}`
   - All API responses can include translated messages

## Usage

### For Users

1. **Changing Language**:
   - Click on the language selector in the navigation bar
   - Select desired language from the dropdown
   - UI will immediately update to reflect the selected language

2. **API Language Selection**:
   - Set the `Accept-Language` header to `en` or `ar`
   - Or append `?lang=en` or `?lang=ar` to API URLs

### For Developers

1. **Adding New Translations**:
   - Frontend: Add new keys and translations to the translation objects in `LanguageContext.tsx`
   - Backend: Add new keys and translations to the JSON files in `backend/utils/translations/`

2. **Adding New Languages**:
   - Frontend: Add new language option to the `Language` type and translations object
   - Backend: Add new language code to `SUPPORTED_LANGUAGES` and create a new translation file

3. **Using Translations in Components**:
   - Import the language context: `import { useLanguage } from "../contexts/LanguageContext"`
   - Access translation function: `const { t } = useLanguage()`
   - Use translation keys: `{t('key.name')}`

## Dependencies

- Frontend:
  - `@radix-ui/react-dropdown-menu`: For the language selector dropdown
  - `clsx`: For conditional class name handling
  - `tailwind-merge`: For merging Tailwind CSS classes

- Backend:
  - FastAPI middleware for language detection
  - JSON files for translation storage

## Future Improvements

- Add more languages beyond English and Arabic
- Implement a translation management system for easier updates
- Add language-specific formatting for dates, numbers, and currencies
- Implement automatic language detection based on user browser settings
- Add translation coverage reporting to track untranslated content 