"use client";

import React from 'react';
import Link from 'next/link';
import { Button } from './ui/button';
import { Settings, ChevronDown, Database, Globe } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from './ui/dropdown-menu';

export default function AdminMenu() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="flex items-center gap-1"
        >
          <Settings className="h-4 w-4" />
          <span className="hidden sm:inline">Admin</span>
          <ChevronDown className="h-3 w-3 ml-1" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuItem asChild>
          <Link href="/admin/dashboard" className="flex items-center gap-2 w-full">
            <Settings className="h-4 w-4" />
            <span>Dashboard</span>
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href="/admin/users" className="flex items-center gap-2 w-full">
            <Settings className="h-4 w-4" />
            <span>User Management</span>
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/admin/translation-memory" className="flex items-center gap-2 w-full">
            <Database className="h-4 w-4" />
            <span>Translation Memory</span>
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href="/admin/language-settings" className="flex items-center gap-2 w-full">
            <Globe className="h-4 w-4" />
            <span>Language Settings</span>
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 