"use client";
import { useState } from 'react';
import { useLanguage, Language } from '../contexts/LanguageContext';
import { Button } from './ui/button';
import { Globe } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';

export default function LanguageSwitcher() {
  const { language, setLanguage, t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    setIsOpen(false);
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="flex items-center gap-1 text-slate-700 hover:text-blue-700 hover:bg-blue-50 rounded-md"
        >
          <Globe className="h-4 w-4" />
          <span className="hidden sm:inline">{language === 'en' ? 'EN' : 'AR'}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40">
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
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 