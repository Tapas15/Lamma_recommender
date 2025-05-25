"use client";
import Link from "next/link";
import { Button } from "./ui/button";
import { useI18n } from "../providers/i18n-provider";
import TranslatableImage from "./TranslatableImage";
import Image from "next/image";

export default function Hero() {
  const { t } = useI18n();
  
  return (
    <section className="hero relative overflow-hidden bg-gradient-to-r from-[#f0f7ff] via-[#e0edff] to-[#d5e5ff] py-20">
      {/* Background pattern */}
      <div className="absolute top-0 right-0 w-1/2 h-full opacity-80 z-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGRlZnM+CiAgPHBhdHRlcm4gaWQ9InBhdHRlcm4iIHg9IjAiIHk9IjAiIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CiAgICA8Y2lyY2xlIGN4PSIxIiBjeT0iMSIgcj0iMSIgZmlsbD0icmdiYSgyNCwgMTE5LCAyNDIsIDAuMDUpIi8+CiAgPC9wYXR0ZXJuPgo8L2RlZnM+CjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjcGF0dGVybikiLz4KPC9zdmc+')]"></div>
      
      {/* Circle decoration */}
      <div className="absolute bottom-[-50px] left-[-50px] w-[200px] h-[200px] rounded-full bg-gradient-to-r from-blue-500/10 to-blue-500/5 z-0"></div>

      <div className="container mx-auto px-4 relative z-10 max-w-7xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          {/* Left column - Text content */}
          <div className="max-w-full">
            <div className="inline-block px-6 py-3 rounded-full bg-gradient-to-r from-blue-500/10 to-blue-500/20 text-blue-600 text-sm font-semibold mb-6 shadow-sm uppercase tracking-wide">
              {t('home.hero.tagline')}
            </div>
            
            <h1 className="text-4xl md:text-5xl lg:text-[3.5rem] font-extrabold mb-6 leading-tight bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
              {t('home.hero.title')}
            </h1>
            
            <p className="text-lg md:text-xl text-slate-700 mb-8 font-normal">
              {t('home.hero.description')}
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 mt-8">
              <Button
                className="bg-gradient-to-r from-blue-600 to-blue-800 text-white hover:shadow-lg hover:-translate-y-1 transition-all duration-300 rounded-full px-8 py-6 font-semibold"
                asChild
              >
                <Link href="/get-started">
                  {t('home.hero.dashboard_btn')}
                </Link>
              </Button>
              
              <Button
                className="bg-white text-blue-600 border border-blue-200 hover:border-blue-300 hover:shadow-md hover:-translate-y-1 transition-all duration-300 rounded-full px-8 py-6 font-semibold"
                variant="outline"
                asChild
              >
                <Link href="/explore">
                  {t('home.hero.explore_btn')}
                </Link>
              </Button>
            </div>
            
            {/* Feature badges */}
            <div className="flex flex-wrap gap-4 mt-12">
              <div className="flex items-center gap-3 bg-white px-6 py-3 rounded-full shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                </svg>
                <span className="font-medium text-slate-700">{t('home.features.modern_stack')}</span>
              </div>
              
              <div className="flex items-center gap-3 bg-white px-6 py-3 rounded-full shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                </svg>
                <span className="font-medium text-slate-700">{t('home.features.community_driven')}</span>
              </div>
              
              <div className="flex items-center gap-3 bg-white px-6 py-3 rounded-full shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="font-medium text-slate-700">{t('home.features.production_ready')}</span>
              </div>
            </div>
          </div>
          
          {/* Right column - Visual */}
          <div className="relative flex justify-center items-center">
            {/* Decorative shapes */}
            <div className="absolute w-[300px] h-[300px] top-[-50px] right-[-50px] rounded-full bg-gradient-to-r from-blue-600 to-blue-800 opacity-10"></div>
            <div className="absolute w-[200px] h-[200px] bottom-[-30px] left-[20px] rounded-full bg-gradient-to-r from-blue-600 to-blue-800 opacity-10"></div>
            <div className="absolute w-[150px] h-[150px] top-[50px] left-[-20px] rounded-full bg-gradient-to-r from-blue-600 to-blue-800 opacity-10"></div>
            
            {/* Logo showcase */}
            <div className="w-[250px] h-[250px] bg-white rounded-full flex justify-center items-center shadow-xl relative z-2">
              <TranslatableImage
                sources={{
                  en: "/images/en/logo.png",
                  ar: "/images/ar/logo.png"
                }}
                fallback="/logo.png"
                alt="L&D Nexus Logo"
                width={175}
                height={175}
                className="w-auto h-auto"
                priority
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
