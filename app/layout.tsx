import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800", "900"],
  display: "swap",
  variable: "--font-inter"
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0a0e12"
};

export const metadata: Metadata = {
  title: "EngineerOS — AI Engineering Command Center",
  description:
    "A living digital twin that learns from code, incidents, architecture choices, interview simulations, and collaboration behavior to accelerate engineering growth.",
  keywords: [
    "engineering",
    "digital twin",
    "AI",
    "operating system",
    "career growth",
    "system design",
    "incident response"
  ],
  openGraph: {
    title: "EngineerOS — AI Engineering Command Center",
    description:
      "A living digital twin that learns from code, incidents, architecture choices, interview simulations, and collaboration behavior to accelerate engineering growth.",
    type: "website",
    locale: "en_US",
    siteName: "EngineerOS"
  },
  twitter: {
    card: "summary_large_image",
    title: "EngineerOS — AI Engineering Command Center",
    description:
      "A living digital twin that learns from code, incidents, architecture choices, interview simulations, and collaboration behavior to accelerate engineering growth."
  },
  robots: { index: true, follow: true }
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={`${inter.className} antialiased`}>{children}</body>
    </html>
  );
}
