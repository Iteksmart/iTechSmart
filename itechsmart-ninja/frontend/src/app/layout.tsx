import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'iTechSmart Ninja',
  description: 'Autonomous AI Agents for IT Operations',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}