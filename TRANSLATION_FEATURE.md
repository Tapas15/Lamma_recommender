# Translation Feature

## Overview

The application includes a comprehensive English to Arabic translation feature powered by LibreTranslate. This feature allows users to translate the entire page content, including text and images, with a single click using a floating, draggable translation button that persists across all pages.

## Components

### LibreTranslate Integration

- **LibreTranslate Docker Container**: The setup script automatically pulls and runs the LibreTranslate Docker container if Docker is installed.
- **API Endpoint**: The translation service is available at `http://localhost:5000` by default.
- **Environment Configuration**: The LibreTranslate URL is configured in the Next.js environment.

### Frontend Components

1. **FloatingTranslateButton Component**: 
   - Draggable button that can be positioned anywhere on the screen
   - Persists across page navigation
   - Remembers its position using localStorage
   - Maintains translation state between page loads
   - Toggles between English and Arabic translations
   - Shows loading state during translation
   - Automatically detects if LibreTranslate is available

2. **Translation Utilities**:
   - `lib/translate.ts`: Core translation functions for text and HTML content
   - `lib/imageTranslate.ts`: Specialized functions for handling image translations

3. **OCR Capabilities**:
   - Text extraction from images using Tesseract.js
   - Translation of image alt text and titles

## Usage

1. **Translating a Page**:
   - Click the "عرض بالعربية" (View in Arabic) button in the floating translator
   - The entire page content will be translated to Arabic
   - Text direction will automatically switch to RTL (right-to-left)
   - Image alt text and titles will be translated
   - The translation state persists across page navigation

2. **Reverting to English**:
   - Click the "View in English" button
   - The page will return to its original English content
   - Text direction will switch back to LTR (left-to-right)

3. **Moving the Translation Button**:
   - Drag the button using the move handle at the top
   - The button position is saved and will be restored when you return to the site
   - The button stays within the viewport boundaries

## Technical Details

### Translation Process

1. **HTML Content Translation**:
   - The original HTML content is saved for later restoration
   - HTML is sent to LibreTranslate with format=html parameter
   - Translated HTML replaces the original content
   - Direction attribute is set to RTL for Arabic

2. **Image Translation**:
   - Alt text and title attributes are extracted from images
   - Text is sent to LibreTranslate for translation
   - Original values are stored for later restoration
   - Images are wrapped in containers with translated metadata

3. **State Persistence**:
   - Button position is saved in localStorage as 'translationButtonPosition'
   - Translation state is saved in localStorage as 'isPageTranslated'
   - These values are restored when the page loads

### Dependencies

- **tesseract.js**: For OCR (Optical Character Recognition) capabilities
- **lucide-react**: For UI icons
- **LibreTranslate**: Docker container for translation services

## Setup

The translation feature is automatically set up during the installation process:

1. LibreTranslate Docker container is pulled and started if Docker is installed
2. Required frontend dependencies are installed
3. Environment variables are configured

If Docker is not installed, the setup will continue without LibreTranslate, but the translation button will not appear in the UI until LibreTranslate is manually installed and running.

## Manual Setup

If you need to manually set up the translation feature:

1. Install Docker from https://www.docker.com/products/docker-desktop
2. Pull the LibreTranslate image: `docker pull libretranslate/libretranslate:latest`
3. Run the container: `docker run -d --name libretranslate -p 5000:5000 libretranslate/libretranslate:latest`
4. Install frontend dependencies: 
   ```bash
   cd frontend/lnd-nexus
   npm install tesseract.js lucide-react @radix-ui/react-toast react-draggable
   ```

## Troubleshooting

- **Translation Button Not Appearing**: Verify that LibreTranslate is running (`docker ps`)
- **Translation Errors**: Check the browser console for error messages
- **Slow Translation**: Large pages with many images may take longer to translate
- **OCR Issues**: Ensure the image is clear and text is readable for best results
- **Button Position Reset**: If the button position is reset, check if localStorage is disabled in your browser 