import type { Metadata } from "next";

import "./globals.css";
import { IconSprite } from "@/components/IconSprite";
import { PWARegister } from "@/components/PWARegister";
import { ThemeScript } from "@/components/ThemeScript";
import { getLang } from "@/lib/api";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return {
    title: {
      default: "SLAnything",
      template: "%s · SLAnything",
    },
    description:
      lang === "en"
        ? "An interactive library of courses for learning AI by building."
        : "SLAnything · biblioteca de cursos interactivos para aprender IA construyendo.",
    applicationName: "SLAnything",
    icons: {
      icon: "/icon.svg",
      apple: "/apple-touch-icon.png",
    },
    appleWebApp: {
      capable: true,
      title: "SLAnything",
      statusBarStyle: "default",
    },
  };
}

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const lang = await getLang();
  return (
    <html lang={lang} data-theme="light" suppressHydrationWarning>
      <head>
        <meta name="color-scheme" content="light dark" />
        <ThemeScript />
      </head>
      <body>
        <IconSprite />
        {children}
        <PWARegister />
      </body>
    </html>
  );
}
