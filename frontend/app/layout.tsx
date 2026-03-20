import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import ThemeToggle from "@/components/ThemeToggle";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Premium Video Downloader",
  description: "Download high quality videos from YouTube, Instagram, Facebook, and TikTok",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <body className={inter.className}>
        <header className="navbar">
          <div className="navbar__logo">⚡ Downloader</div>
          <ThemeToggle />
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
