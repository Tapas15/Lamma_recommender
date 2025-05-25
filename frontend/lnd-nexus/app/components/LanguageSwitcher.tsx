"use client";
import { useState } from 'react';
import { useI18n, Language } from '../providers/i18n-provider';
import { Button } from './ui/button';
import { Globe, RefreshCw } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from './ui/dropdown-menu';

export default function LanguageSwitcher() {
  const { language, setLanguage, t, translateAll } = useI18n();
  const [isOpen, setIsOpen] = useState(false);

  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    setIsOpen(false);
  };

  const handleTranslateAll = () => {
    translateAll();
    setIsOpen(false);
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="flex items-center gap-1 text-slate-700 hover:text-blue-700 hover:bg-blue-50 rounded-md border-blue-200"
        >
          <Globe className="h-4 w-4" />
          <span className="hidden sm:inline">{language === 'en' ? 'English' : 'العربية'}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem
          className={`flex items-center gap-2 ${language === 'en' ? 'bg-blue-50 text-blue-700' : ''}`}
          onClick={() => handleLanguageChange('en')}
        >
          <span className="w-6 text-center">🇺🇸</span>
          <span>{t('language.english')}</span>
        </DropdownMenuItem>
        <DropdownMenuItem
          className={`flex items-center gap-2 ${language === 'ar' ? 'bg-blue-50 text-blue-700' : ''}`}
          onClick={() => handleLanguageChange('ar')}
        >
          <span className="w-6 text-center">🇸🇦</span>
          <span>{t('language.arabic')}</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem 
          className="flex items-center gap-2 text-blue-600"
          onClick={handleTranslateAll}
        >
          <RefreshCw className="h-4 w-4" />
          <span>{t('language.translate_all')}</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 