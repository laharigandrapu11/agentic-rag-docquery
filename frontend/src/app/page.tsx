"use client"

// Home page — three-panel layout: upload + document list on the left, chat on the right
// Extended in F6 — selectedIds state drives SummarizeCompare panel

import { useState } from "react"
import FileUpload from "@/components/FileUpload"
import DocumentList from "@/components/DocumentList"
import ChatInterface from "@/components/ChatInterface"
import SummarizeCompare from "@/components/SummarizeCompare"
import { DocumentMeta } from "@/lib/api"

export default function Home() {
  // Incremented on each successful upload so DocumentList knows to refresh
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  // Tracks which doc_ids the user has checked in DocumentList
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  // Mirror of the document list so SummarizeCompare can display filenames
  const [documents, setDocuments] = useState<DocumentMeta[]>([])

  return (
    <div className="min-h-screen bg-background">

      {/* Top navigation bar */}
      <header className="border-b bg-card px-8 py-4">
        <div className="max-w-6xl mx-auto flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
            <svg className="w-3.5 h-3.5 text-primary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <span className="font-semibold text-sm">Agentic RAG DocQuery</span>
        </div>
      </header>

      {/* Main layout: narrow left sidebar for docs, wide right area for chat */}
      <main className="max-w-6xl mx-auto px-8 py-8 flex gap-6 items-start">

        {/* Left column: upload, document list with checkboxes, summarize/compare panel */}
        <div className="w-80 flex-shrink-0 flex flex-col gap-4">
          <FileUpload onUploadSuccess={() => setRefreshTrigger((p) => p + 1)} />
          <DocumentList
            refreshTrigger={refreshTrigger}
            selectedIds={selectedIds}
            onSelectionChange={setSelectedIds}
            onDocumentsLoaded={setDocuments}
          />
          <SummarizeCompare
            documents={documents}
            selectedIds={selectedIds}
            provider="groq"
          />
        </div>

        {/* Right column: chat interface — scoped to selected docs if any are checked */}
        <div className="flex-1">
          <ChatInterface docIds={selectedIds} />
        </div>

      </main>
    </div>
  )
}
