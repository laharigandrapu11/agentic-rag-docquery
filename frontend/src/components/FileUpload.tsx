"use client"

// Upload panel — supports drag-and-drop, file browser, and URL submission.
// Calls onUploadSuccess() after a successful upload so the parent refreshes the list.

import { useRef, useState } from "react"
import { uploadFile, uploadUrl } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Props {
  onUploadSuccess: () => void
}

export default function FileUpload({ onUploadSuccess }: Props) {
  const [urlInput, setUrlInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  // Hidden file input — triggered by the Browse Files button or zone click
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function handleFile(file: File) {
    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const result = await uploadFile(file)
      setSuccess(`Uploaded "${result.filename}" — ${result.chunk_count} chunks`)
      onUploadSuccess()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  async function handleUrl() {
    if (!urlInput.trim()) return
    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const result = await uploadUrl(urlInput)
      setSuccess(`Uploaded "${result.filename}" — ${result.chunk_count} chunks`)
      setUrlInput("")
      onUploadSuccess()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Upload Document</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">

        {/* Drag-and-drop zone */}
        <div
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setIsDragging(false)
            const file = e.dataTransfer.files[0]
            if (file) handleFile(file)
          }}
          className={`cursor-pointer rounded-lg border-2 border-dashed p-8 flex flex-col items-center gap-3 transition-colors
            ${isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50"}`}
        >
          {/* Upload icon */}
          <div className="rounded-full bg-primary/10 p-3">
            <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium">Drag & drop a file here</p>
            <p className="text-xs text-muted-foreground mt-1">PDF, DOCX, TXT, MD</p>
          </div>
          <Button
            variant="outline"
            size="sm"
            type="button"
            onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click() }}
          >
            Browse Files
          </Button>
        </div>

        {/* Hidden native file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleFile(file)
          }}
        />

        {/* Divider */}
        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-border" />
          <span className="text-xs text-muted-foreground">or paste a URL</span>
          <div className="flex-1 h-px bg-border" />
        </div>

        {/* URL input row */}
        <div className="flex gap-2">
          <Input
            type="text"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleUrl()}
            placeholder="https://example.com"
          />
          <Button
            onClick={handleUrl}
            disabled={loading || !urlInput.trim()}
          >
            Submit
          </Button>
        </div>

        {/* Status messages */}
        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            Uploading...
          </div>
        )}
        {success && (
          <p className="text-sm text-green-600 bg-green-50 rounded-md px-3 py-2 border border-green-200">
            {success}
          </p>
        )}
        {error && (
          <p className="text-sm text-destructive bg-destructive/10 rounded-md px-3 py-2 border border-destructive/20">
            {error}
          </p>
        )}

      </CardContent>
    </Card>
  )
}
