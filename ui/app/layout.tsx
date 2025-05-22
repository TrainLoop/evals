import type { Metadata } from 'next'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { DashboardShell } from '@/components/dashboard-shell'

export const metadata: Metadata = {
  title: 'TrainLoop Evals',
  description: 'TrainLoop Evaluation Platform',
  generator: 'Next.js',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background" suppressHydrationWarning>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="flex min-h-screen flex-col">
            <DashboardShell>
              <main className="flex-1 p-4">{children}</main>
            </DashboardShell>
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}
