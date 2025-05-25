/**
 * Extract translation keys from the codebase
 * This script scans the codebase for t('key') patterns and extracts them
 * into a JSON file that can be used as a template for translations
 */

const fs = require('fs-extra');
const path = require('path');
const glob = require('glob');

// Configuration
const APP_DIR = path.resolve(__dirname, '../app');
const LOCALES_DIR = path.resolve(__dirname, '../app/locales');
const TEMPLATE_FILE = path.resolve(LOCALES_DIR, 'template.json');
const PATTERN = /t\(['"]([^'"]+)['"]\)/g;

// Ensure locales directory exists
fs.ensureDirSync(LOCALES_DIR);

// Find all TypeScript and TypeScript React files
async function findSourceFiles() {
  return glob.sync(`${APP_DIR}/**/*.{ts,tsx}`, {
    ignore: ['**/node_modules/**', '**/.next/**']
  });
}

// Extract translation keys from a file
function extractKeysFromFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const keys = new Set();
  let match;

  while ((match = PATTERN.exec(content)) !== null) {
    keys.add(match[1]);
  }

  return Array.from(keys);
}

// Organize keys by namespace/section
function organizeKeys(keys) {
  const organizedKeys = {};

  keys.forEach(key => {
    const parts = key.split('.');
    const section = parts[0];
    
    if (!organizedKeys[section]) {
      organizedKeys[section] = {};
    }
    
    if (parts.length === 1) {
      organizedKeys[section][key] = key;
    } else {
      const subKey = parts.slice(1).join('.');
      organizedKeys[section][subKey] = key;
    }
  });

  return organizedKeys;
}

// Create a template file with all keys
async function createTemplateFile(keys) {
  const template = {};
  
  keys.forEach(key => {
    // Use the key as the default English translation
    template[key] = key.split('.').pop().replace(/_/g, ' ');
  });
  
  await fs.writeJson(TEMPLATE_FILE, template, { spaces: 2 });
  console.log(`Template file created: ${TEMPLATE_FILE}`);
}

// Main function
async function main() {
  try {
    console.log('Extracting translation keys...');
    
    const files = await findSourceFiles();
    console.log(`Found ${files.length} source files`);
    
    const allKeys = new Set();
    
    files.forEach(file => {
      const keys = extractKeysFromFile(file);
      keys.forEach(key => allKeys.add(key));
    });
    
    console.log(`Found ${allKeys.size} unique translation keys`);
    
    await createTemplateFile(allKeys);
    
    console.log('Done!');
  } catch (error) {
    console.error('Error extracting translation keys:', error);
    process.exit(1);
  }
}

main(); 