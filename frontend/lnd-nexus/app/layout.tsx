import { Inter } from "next/font/google";
import "./globals.css";
import { Metadata } from "next";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import { AuthProvider } from "./contexts/AuthContext";
import { I18nProvider } from "./providers/i18n-provider";
import FloatingTranslateButton from "./components/FloatingTranslateButton";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "L&D Nexus",
  description: "L&D Nexus",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <I18nProvider>
            <Navbar />
            {children}
            <Footer />
            <FloatingTranslateButton />
          </I18nProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
