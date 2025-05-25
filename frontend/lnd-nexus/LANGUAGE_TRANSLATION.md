# Language Translation System

This document explains how to use and extend the language translation system in the L&D Nexus application.

## Overview

The application supports multiple languages (currently English and Arabic) with a comprehensive translation system that includes:

- Text translations
- Image translations
- Right-to-left (RTL) layout support
- A language switcher component
- Translation extraction and synchronization tools

## Key Components

### 1. I18n Provider

Located at `app/providers/i18n-provider.tsx`, this provider integrates React's Context API with the i18next library to manage translations. It provides:

- Language state management
- Translation functions
- RTL layout detection
- Image path translation
- Translation synchronization events

### 2. Translation Files

Translation files are stored in `app/locales/` with separate files for each language:

- `en.json` - English translations
- `ar.json` - Arabic translations

These files are structured with nested objects for organization:

```json
{
  "common": {
    "loading": "Loading...",
    "error": "An error occurred"
  },
  "home": {
    "hero": {
      "title": "Welcome to L&D Nexus"
    }
  }
}
```

### 3. Image Translations

Image translations allow different images to be displayed based on the selected language. This is particularly useful for images containing text or culturally specific content.

### 4. Utility Components

- `TranslatableImage` - A component for displaying language-specific images
- `TranslatableContent` - A component for displaying complex language-specific content (including HTML)
- `LanguageSwitcher` - A dropdown component for changing the language

## How to Use

### 1. Text Translation

```tsx
import { useI18n } from "../providers/i18n-provider";

export default function MyComponent() {
  const { t } = useI18n();
  
  return (
    <div>
      <h1>{t('page.title')}</h1>
      <p>{t('page.description')}</p>
    </div>
  );
}
```

### 2. Image Translation

```tsx
import TranslatableImage from "./TranslatableImage";

<TranslatableImage
  sources={{
    en: "/images/en/logo.png",
    ar: "/images/ar/logo.png"
  }}
  fallback="/logo.png"
  alt="Company Logo"
  width={200}
  height={100}
/>
```

### 3. Complex Content Translation

```tsx
import TranslatableContent from "./TranslatableContent";

<TranslatableContent
  content={{
    en: <p>This is <strong>complex</strong> content in English</p>,
    ar: <p>هذا <strong>محتوى معقد</strong> باللغة العربية</p>
  }}
/>
```

## Extending the System

### 1. Adding New Languages

1. Create a new translation file in `app/locales/` (e.g., `fr.json`)
2. Update the `I18nProvider` in `app/providers/i18n-provider.tsx` to include the new language
3. Update the `LanguageSwitcher` component to include the new language
4. Add the new language to the supported languages in the backend

### 2. Adding New Translation Keys

1. Add the new key to the translation files
2. Use the key in your components with the `t` function

### 3. Translation Tools

The project includes two utility scripts for managing translations:

- `npm run extract-messages` - Extracts translation keys from the codebase
- `npm run sync-translations` - Synchronizes translation files to ensure they have the same keys

## Backend Integration

The backend also supports localization through:

- Language detection middleware
- Translation files for API responses
- Image path translations for API responses

## Best Practices

1. Use descriptive, hierarchical keys (e.g., `page.section.element`)
2. Always provide fallbacks for translations
3. Run the sync-translations script after adding new keys
4. Test all languages when making UI changes
5. Use TranslatableImage for images with text
6. Consider cultural differences when designing layouts

## Troubleshooting

- If translations aren't working, check that the component is wrapped in the I18nProvider
- If images aren't loading, check that the image paths are correct
- If RTL layout isn't working correctly, check that the component supports RTL layout
- If new translations aren't showing up, try running the sync-translations script 