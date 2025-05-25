/**
 * Synchronize translations between language files
 * This script ensures that all language files have the same keys
 * and updates missing keys with defaults from the template
 */

const fs = require('fs-extra');
const path = require('path');
const glob = require('glob');

// Configuration
const LOCALES_DIR = path.resolve(__dirname, '../app/locales');
const TEMPLATE_FILE = path.resolve(LOCALES_DIR, 'template.json');

// Ensure locales directory exists
fs.ensureDirSync(LOCALES_DIR);

// Find all language files
async function findLanguageFiles() {
  return glob.sync(`${LOCALES_DIR}/*.json`, {
    ignore: ['**/template.json']
  });
}

// Create language files if they don't exist
async function ensureLanguageFiles() {
  const languages = ['en', 'ar'];
  
  for (const lang of languages) {
    const langFile = path.resolve(LOCALES_DIR, `${lang}.json`);
    
    if (!fs.existsSync(langFile)) {
      console.log(`Creating language file for ${lang}...`);
      await fs.writeJson(langFile, {}, { spaces: 2 });
    }
  }
}

// Synchronize translations
async function syncTranslations() {
  // Load template
  if (!fs.existsSync(TEMPLATE_FILE)) {
    console.error('Template file not found. Run extract-messages first.');
    process.exit(1);
  }
  
  const template = await fs.readJson(TEMPLATE_FILE);
  const langFiles = await findLanguageFiles();
  
  for (const langFile of langFiles) {
    const lang = path.basename(langFile, '.json');
    console.log(`Synchronizing ${lang} translations...`);
    
    const translations = await fs.readJson(langFile);
    let updated = false;
    
    // Add missing keys from template
    for (const key in template) {
      if (!translations[key]) {
        translations[key] = lang === 'en' ? template[key] : `[${lang}] ${template[key]}`;
        updated = true;
      }
    }
    
    // Remove extra keys not in template
    for (const key in translations) {
      if (!template[key]) {
        delete translations[key];
        updated = true;
      }
    }
    
    if (updated) {
      await fs.writeJson(langFile, translations, { spaces: 2 });
      console.log(`Updated ${lang} translations`);
    } else {
      console.log(`No changes needed for ${lang}`);
    }
  }
}

// Main function
async function main() {
  try {
    console.log('Synchronizing translations...');
    
    await ensureLanguageFiles();
    await syncTranslations();
    
    console.log('Done!');
  } catch (error) {
    console.error('Error synchronizing translations:', error);
    process.exit(1);
  }
}

main(); 