"use client";
import { useEffect, useState } from 'react';
import Image, { ImageProps } from 'next/image';
import { useI18n } from '../providers/i18n-provider';

interface TranslatableImageProps extends Omit<ImageProps, 'src'> {
  sources: {
    en: string;
    ar: string;
  };
  fallback: string;
  alt: string;
}

export default function TranslatableImage({
  sources,
  fallback,
  alt,
  ...props
}: TranslatableImageProps) {
  const { language } = useI18n();
  const [src, setSrc] = useState<string>(fallback);
  const [error, setError] = useState<boolean>(false);

  useEffect(() => {
    // Reset error state when language changes
    setError(false);
    
    // Use the language-specific source or fallback
    const newSrc = sources[language] || fallback;
    setSrc(newSrc);
  }, [language, sources, fallback]);

  const handleError = () => {
    setError(true);
    setSrc(fallback);
  };

  return (
    <Image
      src={error ? fallback : src}
      alt={alt}
      onError={handleError}
      {...props}
    />
  );
} 