"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "./ui/button";
import {
  Menu,
  Home,
  Users,
  Briefcase,
  BookOpen,
  MessageSquare,
  LogOut,
  User,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { useI18n } from "../providers/i18n-provider";
import LanguageSwitcher from "./LanguageSwitcher";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { isAuthenticated, isLoading, user, logout } = useAuth();
  const { t, isRTL } = useI18n();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const handleLogout = () => {
    logout();
    setMobileMenuOpen(false);
  };

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-white shadow-md" : "bg-white/95 backdrop-blur-md"
      }`}
    >
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <div className="bg-gradient-to-r from-blue-700 to-blue-500 text-white font-bold text-xl p-2 rounded-lg mr-2">
                L&D
              </div>
              <span className="text-slate-800 font-bold text-2xl">Nexus</span>
            </Link>

            <nav className="hidden md:block ml-10">
              <ul className="flex space-x-6">
                <li>
                  <Link
                    href="/"
                    className="flex items-center px-3 py-2 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50 transition-colors"
                  >
                    <Home className="h-4 w-4 mr-1.5 text-slate-500" />
                    {t('nav.home')}
                  </Link>
                </li>
                <li>
                  <Link
                    href="/professionals"
                    className="flex items-center px-3 py-2 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50 transition-colors"
                  >
                    <Users className="h-4 w-4 mr-1.5 text-slate-500" />
                    {t('nav.professionals')}
                  </Link>
                </li>
                <li>
                  <Link
                    href="/jobs"
                    className="flex items-center px-3 py-2 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50 transition-colors"
                  >
                    <Briefcase className="h-4 w-4 mr-1.5 text-slate-500" />
                    {t('nav.jobs')}
                  </Link>
                </li>
                <li>
                  <Link
                    href="/resources"
                    className="flex items-center px-3 py-2 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50 transition-colors"
                  >
                    <BookOpen className="h-4 w-4 mr-1.5 text-slate-500" />
                    {t('nav.resources')}
                  </Link>
                </li>
                <li>
                  <Link
                    href="/forum"
                    className="flex items-center px-3 py-2 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50 transition-colors"
                  >
                    <MessageSquare className="h-4 w-4 mr-1.5 text-slate-500" />
                    {t('nav.community')}
                  </Link>
                </li>
              </ul>
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-4">
              {/* Language Switcher with Translation */}
              <LanguageSwitcher />
              
              {isLoading ? (
                <div className="w-16 h-8 bg-gray-200 animate-pulse rounded"></div>
              ) : isAuthenticated ? (
                <>
                  <Link href="/dashboard">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-slate-700 hover:text-blue-700 hover:bg-blue-50"
                    >
                      <User className="h-4 w-4 mr-1.5" />
                      {user?.full_name || t('nav.dashboard')}
                    </Button>
                  </Link>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700 hover:border-red-300"
                    onClick={handleLogout}
                  >
                    <LogOut className="h-4 w-4 mr-1.5" />
                    {t('nav.logout')}
                  </Button>
                </>
              ) : (
                <>
                  <Link href="/login">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-slate-700 hover:text-blue-700 hover:bg-blue-50"
                    >
                      {t('nav.signin')}
                    </Button>
                  </Link>
                  <Link href="/register">
                    <Button
                      size="sm"
                      className="bg-gradient-to-r from-blue-700 to-blue-600 text-white border-none shadow-sm hover:shadow-md hover:from-blue-800 hover:to-blue-700 transition-all"
                    >
                      {t('nav.register')}
                    </Button>
                  </Link>
                </>
              )}
            </div>

            <button
              className="md:hidden p-1.5 rounded-md text-slate-700 hover:bg-slate-100"
              onClick={toggleMobileMenu}
              aria-label="Toggle mobile menu"
            >
              <Menu className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 px-2 bg-white border-t border-slate-100 rounded-b-lg shadow-lg">
            <div className="flex items-center justify-center px-3 py-2 mb-2 border-b border-slate-100">
              <LanguageSwitcher />
            </div>
            <ul className="space-y-1">
              <li>
                <Link
                  href="/"
                  className="flex items-center px-3 py-2.5 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50"
                >
                  <Home className="h-5 w-5 mr-3 text-slate-500" />
                  {t('nav.home')}
                </Link>
              </li>
              <li>
                <Link
                  href="/professionals"
                  className="flex items-center px-3 py-2.5 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50"
                >
                  <Users className="h-5 w-5 mr-3 text-slate-500" />
                  {t('nav.professionals')}
                </Link>
              </li>
              <li>
                <Link
                  href="/jobs"
                  className="flex items-center px-3 py-2.5 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50"
                >
                  <Briefcase className="h-5 w-5 mr-3 text-slate-500" />
                  {t('nav.jobs')}
                </Link>
              </li>
              <li>
                <Link
                  href="/resources"
                  className="flex items-center px-3 py-2.5 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50"
                >
                  <BookOpen className="h-5 w-5 mr-3 text-slate-500" />
                  Resources
                </Link>
              </li>
              <li>
                <Link
                  href="/forum"
                  className="flex items-center px-3 py-2.5 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50"
                >
                  <MessageSquare className="h-5 w-5 mr-3 text-slate-500" />
                  Community
                </Link>
              </li>

              <li className="pt-2 mt-2 border-t border-slate-100">
                {isLoading ? (
                  <div className="w-full h-10 bg-gray-200 animate-pulse rounded"></div>
                ) : isAuthenticated ? (
                  <>
                    <Link
                      href="/dashboard"
                      className="flex items-center px-3 py-2.5 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50"
                    >
                      <User className="h-5 w-5 mr-3 text-slate-500" />
                      Dashboard
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex items-center w-full px-3 py-2.5 rounded-md text-slate-700 hover:text-red-600 hover:bg-red-50 mt-1"
                    >
                      <LogOut className="h-5 w-5 mr-3 text-slate-500" />
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/login"
                      className="flex items-center px-3 py-2.5 rounded-md text-slate-700 hover:text-blue-600 hover:bg-slate-50"
                    >
                      <Users className="h-5 w-5 mr-3 text-slate-500" />
                      Sign In
                    </Link>
                    <li className="mt-3 px-3">
                      <Link
                        href="/register"
                        className="block w-full text-center py-2.5 bg-gradient-to-r from-blue-700 to-blue-600 hover:from-blue-800 hover:to-blue-700 text-white font-medium rounded-md shadow-sm"
                      >
                        Register
                      </Link>
                    </li>
                  </>
                )}
              </li>
            </ul>
          </div>
        )}
      </div>
    </header>
  );
}
