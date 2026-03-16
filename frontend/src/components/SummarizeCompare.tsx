"use client"

// F6 - Summarize and Compare panel
// Sits below DocumentList in the left sidebar.
// 1 doc selected  → Summarize button
// 2+ docs selected → question input + Compare button

import { useState } from "react"
import { streamSummarize, streamCompare, CitationChunk, HopTraceEvent, DocumentMeta } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import SourceCitation from "@/components/SourceCitation"
import HopTrace from "@/components/HopTrace"

interface Props {
    documents: DocumentMeta[]
    selectedIds: string[]
    provider: string
}

export default function SummarizeCompare({ documents, selectedIds, provider }: Props) {
    const [question, setQuestion] = useState("")
    const [result, setResult] = useState("")
    const [citations, setCitations] = useState<CitationChunk[]>([])
    const [hopTraces, setHopTraces] = useState<HopTraceEvent[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const canSummarize = selectedIds.length === 1
    const canCompare = selectedIds.length >= 2

    if (!canSummarize && !canCompare) return null

    function reset() {
        setResult("")
        setCitations([])
        setHopTraces([])
        setError(null)
    }

    async function handleSummarize() {
        reset()
        setLoading(true)
        try {
            await streamSummarize(
                { doc_id: selectedIds[0], provider },
                (token) => setResult((prev) => prev + token),
                () => setLoading(false),
                (hop) => setHopTraces((prev) => [...prev, hop]),
            )
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong")
            setLoading(false)
        }
    }

    async function handleCompare(e: React.FormEvent) {
        e.preventDefault()
        if (!question.trim()) return
        reset()
        setLoading(true)
        try {
            await streamCompare(
                { doc_ids: selectedIds, question: question.trim(), provider },
                (token) => setResult((prev) => prev + token),
                (citation) => setCitations((prev) => [...prev, citation]),
                () => setLoading(false),
                (hop) => setHopTraces((prev) => [...prev, hop]),
            )
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong")
            setLoading(false)
        }
    }

    const selectedNames = selectedIds.map(
        (id) => documents.find((d) => d.doc_id === id)?.filename ?? id
    )

    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-base">
                    {canCompare ? "Compare" : "Summarize"}
                </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">

                {/* Show which docs are selected */}
                <p className="text-xs text-muted-foreground">
                    {selectedNames.join(", ")}
                </p>

                {/* Summarize — single doc */}
                {canSummarize && (
                    <Button
                        onClick={handleSummarize}
                        disabled={loading}
                        size="sm"
                    >
                        {loading ? "Summarizing…" : "Summarize"}
                    </Button>
                )}

                {/* Compare — two or more docs */}
                {canCompare && (
                    <form onSubmit={handleCompare} className="flex flex-col gap-2">
                        <input
                            className="rounded-lg border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                            placeholder="What do you want to compare?"
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            disabled={loading}
                        />
                        <Button
                            type="submit"
                            disabled={loading || !question.trim()}
                            size="sm"
                        >
                            {loading ? "Comparing…" : "Compare"}
                        </Button>
                    </form>
                )}

                {/* Reasoning chain */}
                {hopTraces.length > 0 && <HopTrace traces={hopTraces} />}

                {/* Streaming result */}
                {result && (
                    <div className="rounded-lg bg-muted px-3 py-2 text-sm whitespace-pre-wrap leading-relaxed max-h-64 overflow-y-auto">
                        {result}
                    </div>
                )}

                {/* Citations (compare only) */}
                {citations.length > 0 && <SourceCitation citations={citations} />}

                {error && (
                    <p className="text-xs text-destructive">{error}</p>
                )}

            </CardContent>
        </Card>
    )
}
