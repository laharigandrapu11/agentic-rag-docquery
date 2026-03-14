"use client"

// Renders the expandable source citations panel below an assistant answer.
// Each citation is a pill showing [Source N] — clicking it expands to show
// the filename, page, and the actual chunk text retrieved from Qdrant.

import { useState } from "react"
import { CitationChunk } from "@/lib/api"

interface Props {
    citations: CitationChunk[]
}

export default function SourceCitation({ citations }: Props) {
    // expandedIndex tracks which citation is currently open (-1 = none)
    const [expandedIndex, setExpandedIndex] = useState<number>(-1)

    if (citations.length === 0) return null

    return (
        <div className="mt-2 flex flex-col gap-1">
            {/* Row of source pills */}
            <div className="flex flex-wrap gap-1.5">
                {citations.map((c, i) => (
                    <button
                        key={i}
                        onClick={() => setExpandedIndex(expandedIndex === i ? -1 : i)}
                        className={`text-xs px-2.5 py-1 rounded-full border transition-colors font-medium
                            ${expandedIndex === i
                                ? "bg-primary text-primary-foreground border-primary"
                                : "bg-muted text-muted-foreground border-border hover:border-primary/50 hover:text-foreground"
                            }`}
                    >
                        Source {i + 1}
                    </button>
                ))}
            </div>

            {/* Expanded citation detail panel */}
            {expandedIndex !== -1 && (
                <div className="rounded-lg border bg-muted/40 p-3 text-xs flex flex-col gap-1.5">
                    {/* Filename and page */}
                    <p className="font-medium text-foreground">
                        {citations[expandedIndex].source}
                        {citations[expandedIndex].page && (
                            <span className="text-muted-foreground font-normal ml-1">
                                — Page {citations[expandedIndex].page}
                            </span>
                        )}
                    </p>
                    {/* The actual chunk text */}
                    <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
                        {citations[expandedIndex].text}
                    </p>
                </div>
            )}
        </div>
    )
}
