"use client";

import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { 
  getMemoryStats, 
  clearMemoryBank, 
  saveMemoryBank 
} from '@/lib/translationMemory';
import { Download, Trash2, RefreshCw } from 'lucide-react';

export default function TranslationMemoryManager() {
  const [stats, setStats] = useState({ totalEntries: 0, languagePairs: [] as string[] });
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  useEffect(() => {
    updateStats();
  }, []);
  
  const updateStats = () => {
    setStats(getMemoryStats());
  };
  
  const handleClearMemory = () => {
    if (confirm('Are you sure you want to clear the translation memory? This cannot be undone.')) {
      clearMemoryBank();
      updateStats();
    }
  };
  
  const handleSaveMemory = () => {
    saveMemoryBank();
    alert('Translation memory saved successfully.');
  };
  
  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      updateStats();
      setIsRefreshing(false);
    }, 300);
  };
  
  return (
    <div className="p-4 border rounded-md bg-white shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Translation Memory</h2>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={handleRefresh}
          disabled={isRefreshing}
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        </Button>
      </div>
      
      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">
          Total entries: <span className="font-medium">{stats.totalEntries}</span>
        </p>
        
        {stats.languagePairs.length > 0 && (
          <>
            <p className="text-sm text-gray-600 mb-1">
              Language pairs:
            </p>
            <ul className="text-sm list-disc pl-5 space-y-1">
              {stats.languagePairs.map((pair, index) => (
                <li key={index}>{pair}</li>
              ))}
            </ul>
          </>
        )}
        
        {stats.totalEntries === 0 && (
          <p className="text-sm text-gray-500 italic">
            No translations stored in memory yet.
          </p>
        )}
      </div>
      
      <div className="flex space-x-2">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleSaveMemory}
          className="flex items-center gap-1"
          disabled={stats.totalEntries === 0}
        >
          <Download className="h-4 w-4" />
          <span>Save Memory</span>
        </Button>
        <Button 
          variant="outline" 
          size="sm" 
          className="text-red-600 hover:bg-red-50 flex items-center gap-1"
          onClick={handleClearMemory}
          disabled={stats.totalEntries === 0}
        >
          <Trash2 className="h-4 w-4" />
          <span>Clear Memory</span>
        </Button>
      </div>
    </div>
  );
} 