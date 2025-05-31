"use client";

import React from 'react';
import TranslationMemoryManager from '../../components/TranslationMemoryManager';
import { Database, BarChart3, Zap } from 'lucide-react';

export default function TranslationMemoryPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Translation Memory Management</h1>
      
      <div className="grid gap-6 md:grid-cols-2">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center gap-2 mb-4">
            <Database className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold">Memory Bank Status</h2>
          </div>
          <TranslationMemoryManager />
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold">Performance Impact</h2>
          </div>
          
          <div className="space-y-4">
            <p className="text-sm text-gray-700">
              Translation memory significantly improves performance by reducing API calls:
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-blue-50 rounded-md">
                <p className="font-medium text-blue-700">Without Memory</p>
                <p className="text-sm text-gray-600">100% API calls</p>
              </div>
              <div className="p-3 bg-green-50 rounded-md">
                <p className="font-medium text-green-700">With Memory</p>
                <p className="text-sm text-gray-600">~40% API calls</p>
              </div>
            </div>
            <p className="text-sm text-gray-600">
              Actual reduction depends on content repetition and user behavior.
            </p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow md:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold">About Translation Memory</h2>
          </div>
          
          <p className="mb-4 text-gray-700">
            Translation memory stores previously translated phrases to improve performance,
            consistency, and reduce API calls to the translation service.
          </p>
          
          <h3 className="text-lg font-medium mb-2">Benefits:</h3>
          <ul className="list-disc pl-5 space-y-1 mb-4 text-gray-700">
            <li>Faster translations for repeated content</li>
            <li>Consistent terminology across the application</li>
            <li>Reduced server load and bandwidth usage</li>
            <li>Improved user experience with quicker translations</li>
          </ul>
          
          <div className="bg-yellow-50 p-3 rounded-md">
            <p className="text-sm text-yellow-800">
              <strong>Note:</strong> The translation memory is stored in your browser's local storage.
              Clearing your browser data will reset the translation memory.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 