import '../globals.css';
import Link from 'next/link';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
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
        <main>{children}</main>
      </body>
    </html>
  );
}

