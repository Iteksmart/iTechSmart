import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ProofLink.AI - The World\'s Trust Layer',
  description: 'Verify anything digital in seconds - no blockchain, no nonsense. Just $1 for digital truth.',
  keywords: 'proof, verification, digital trust, authentication, blockchain alternative',
  authors: [{ name: 'iTechSmart Inc.' }],
  openGraph: {
    title: 'ProofLink.AI - The World\'s Trust Layer',
    description: 'Verify anything digital in seconds',
    url: 'https://prooflink.ai',
    siteName: 'ProofLink.AI',
    images: [
      {
        url: 'https://prooflink.ai/og-image.png',
        width: 1200,
        height: 630,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ProofLink.AI - The World\'s Trust Layer',
    description: 'Verify anything digital in seconds',
    images: ['https://prooflink.ai/og-image.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster position="top-right" />
        </Providers>
      </body>
    </html>
  )
}