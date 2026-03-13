"use client"

import { useState } from "react"
import FileUpload from "@/components/FileUpload"
import DocumentList from "@/components/DocumentList"

export default function Home() {
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <header className="border-b bg-card px-8 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
            <svg className="w-3.5 h-3.5 text-primary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <span className="font-semibold text-sm">Agentic RAG DocQuery</span>
        </div>
      </header>

      {/* Main two-column layout */}
      <main className="max-w-5xl mx-auto px-8 py-8 flex gap-6 items-start">
        <div className="w-1/2">
          <FileUpload onUploadSuccess={() => setRefreshTrigger((p) => p + 1)} />
        </div>
        <div className="w-1/2">
          <DocumentList refreshTrigger={refreshTrigger} />
        </div>
      </main>
    </div>
  )
}
