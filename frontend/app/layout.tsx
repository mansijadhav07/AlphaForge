import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Navbar } from '@/components/layout/navbar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AlphaForge - Financial Intelligence Platform',
  description: 'Real-time financial feature intelligence and analytics',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-background/95">
          <Navbar />
          <main className="pt-16">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
