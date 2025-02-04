import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Build It Yourself',
  description: 'Transform your Python code by removing external dependencies',
  icons: {
    icon: '/favicon.png'
  }
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <link
        rel="icon"
        href="/icon.png"
        type="image/png"
        sizes="any"
      />
      <body className={inter.className}>{children}</body>
    </html>
  );
}
