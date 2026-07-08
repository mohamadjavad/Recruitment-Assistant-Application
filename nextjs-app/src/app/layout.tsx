import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Recruitment Assistant",
  description:
    "AI-powered recruitment assistant — automated candidate sourcing, matching, and reporting powered by CrewAI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <div className="min-h-screen flex flex-col">
          {/* Header */}
          <header className="border-b border-border bg-white px-4 py-3">
            <div className="container flex items-center gap-3">
              <h1 className="text-lg font-semibold tracking-tight">
                Recruitment Assistant
              </h1>
              <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
                v0.2.0
              </span>
            </div>
          </header>

          {/* Main content */}
          <main className="flex-1 container py-4">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
