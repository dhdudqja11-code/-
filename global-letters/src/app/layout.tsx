import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  style: ["normal", "italic"],
  variable: "--font-serif",
});

export const metadata: Metadata = {
  title: "마음을 묻다 - 당신만의 선명한 빛을 찾아가세요",
  description: "무거운 마음은 이 정원에 묻고, 당신만의 선명한 빛을 찾아가세요.",
};

import Script from "next/script";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className={`${inter.variable} ${playfair.variable} antialiased`}>
        <Script src="https://cdn.jsdelivr.net/npm/html2canvas-pro@latest/dist/html2canvas-pro.min.js" strategy="afterInteractive" />
        <Script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js" strategy="afterInteractive" />
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
