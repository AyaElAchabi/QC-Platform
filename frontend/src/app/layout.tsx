import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/lib/providers/query-provider";

export const metadata: Metadata = {
  title: "MLOps QC Platform",
  description: "Plateforme de contrôle qualité visuel avec ML",
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className="font-sans antialiased" suppressHydrationWarning>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
