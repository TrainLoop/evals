'use client'
import { useState } from 'react'
import { ResultsList } from '@/components/results-list'

export default function ResultsPage() {
  const [ts, setTs] = useState('')
  const [suite, setSuite] = useState('')
  return (
    <div className="flex gap-4">
      <div className="w-48 space-y-2">
        <input placeholder="timestamp" value={ts} onChange={(e) => setTs(e.target.value)} className="w-full border px-2 py-1 text-sm" />
        <input placeholder="suite" value={suite} onChange={(e) => setSuite(e.target.value)} className="w-full border px-2 py-1 text-sm" />
      </div>
      <div className="flex-1">
        <ResultsList ts={ts} suite={suite} />
      </div>
    </div>
  )
}
