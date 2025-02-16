import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import Link from "next/link"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Recruiter Dashboard",
  description: "A dashboard for managing job applicants",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-3">
            <div className="flex gap-4">
              <Link href="/" className="text-gray-700 hover:text-gray-900">
                Dashboard
              </Link>
              <Link href="/shortlist" className="text-gray-700 hover:text-gray-900">
                Shortlisted
              </Link>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  )
}

