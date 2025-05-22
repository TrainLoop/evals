"use client"

import type React from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { BarChart3, Home, Activity, Trophy, Award, ListChecks } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface DashboardShellProps {
  children: React.ReactNode
}

export function DashboardShell({ children }: DashboardShellProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b bg-background">
        <div className="flex h-16 items-center px-4 md:px-6">
          <Link href="/" className="flex items-center gap-2 font-semibold">
            <BarChart3 className="h-6 w-6" />
            <span>LLM Evals</span>
          </Link>
          <nav className="ml-auto flex gap-2">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <Home className="mr-2 h-4 w-4" />
                Dashboard
              </Button>
            </Link>
            <Link href="/events">
              <Button variant="ghost" size="sm">
                <Activity className="mr-2 h-4 w-4" />
                Events
              </Button>
            </Link>
            <Link href="/results">
              <Button variant="ghost" size="sm">
                <ListChecks className="mr-2 h-4 w-4" />
                Results
              </Button>
            </Link>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="cursor-not-allowed">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="opacity-60 pointer-events-none"
                      tabIndex={-1}
                    >
                      <Award className="mr-2 h-4 w-4" />
                      Benchmarks
                    </Button>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Coming Soon</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </nav>
        </div>
      </header>
      <main className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">{children}</main>
    </div>
  )
}
