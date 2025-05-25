import { Inter } from "next/font/google";
import "./globals.css";
import { Metadata } from "next";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import { AuthProvider } from "./contexts/AuthContext";

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
          <Navbar />
          {children}
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
