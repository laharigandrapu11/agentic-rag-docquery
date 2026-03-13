"use client"

// Shows all uploaded documents. Re-fetches when refreshTrigger changes.

import { useEffect, useState } from "react"
import { getDocuments, deleteDocument, DocumentMeta } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Props {
  refreshTrigger: number
}

export default function DocumentList({ refreshTrigger }: Props) {
  const [docs, setDocs] = useState<DocumentMeta[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  async function fetchDocs() {
    setLoading(true)
    setError(null)
    try {
      setDocs(await getDocuments())
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchDocs() }, [refreshTrigger])

  async function handleDelete(docId: string) {
    setDeletingId(docId)
    try {
      await deleteDocument(docId)
      fetchDocs()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Uploaded Documents</CardTitle>
          {docs.length > 0 && (
            <Badge variant="secondary">{docs.length}</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">

        {/* Loading */}
        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground py-2">
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            Loading...
          </div>
        )}

        {/* Error */}
        {error && (
          <p className="text-sm text-destructive bg-destructive/10 rounded-md px-3 py-2">
            {error}
          </p>
        )}

        {/* Empty state */}
        {!loading && docs.length === 0 && (
          <div className="flex flex-col items-center gap-2 py-10 text-center">
            <div className="rounded-full bg-muted p-3">
              <svg className="w-5 h-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-sm text-muted-foreground">No documents uploaded yet</p>
          </div>
        )}

        {/* Document rows */}
        {docs.map((doc) => (
          <div
            key={doc.doc_id}
            className="flex items-center justify-between rounded-lg border bg-card px-4 py-3 hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-center gap-3 min-w-0">
              {/* File icon */}
              <div className="rounded-md bg-primary/10 p-1.5 flex-shrink-0">
                <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium truncate">{doc.filename}</p>
                <p className="text-xs text-muted-foreground">{doc.chunk_count} chunks</p>
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleDelete(doc.doc_id)}
              disabled={deletingId === doc.doc_id}
              className="text-destructive hover:text-destructive hover:bg-destructive/10 flex-shrink-0"
            >
              {deletingId === doc.doc_id ? "Deleting..." : "Delete"}
            </Button>
          </div>
        ))}

      </CardContent>
    </Card>
  )
}
