import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "iTechSmart PassPort - The One Login for Your Entire Life",
  description: "AI-managed MCP identity vault for $1/month. Zero-knowledge encryption, 2FA, breach detection, and more.",
  keywords: "password manager, password vault, security, encryption, 2FA, biometric",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}