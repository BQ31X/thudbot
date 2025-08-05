import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AI Chat Interface',
  description: 'A modern chat interface for interacting with AI',
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