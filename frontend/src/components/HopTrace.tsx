"use client"

// Populated in F4 - Agentic Multi-hop Reasoning
// Collapsible panel showing the agent's reasoning chain before the answer.
// Each hop is one node that ran: router, decomposer, or rag_retrieve.

import { useState } from "react"
import { HopTraceEvent } from "@/lib/api"

interface HopTraceProps {
    traces: HopTraceEvent[]
}

// Human-readable label and icon for each node name
const NODE_META: Record<string, { label: string; icon: string }> = {
    router:           { label: "Router",      icon: "⇢" },
    decomposer:       { label: "Decomposer",  icon: "⊕" },
    rag_retrieve:     { label: "Retriever",   icon: "⊙" },
    map_summarize:    { label: "Summarizer",  icon: "⊞" },
    compare_retrieve: { label: "Retriever",   icon: "⊙" },
}

// Render the node-specific detail line under each hop
function HopDetail({ node, data }: HopTraceEvent) {
    if (node === "router") {
        const decision = data.decision as string
        return (
            <p className="text-xs text-muted-foreground mt-0.5">
                Classified as{" "}
                <span className={`font-semibold ${decision === "complex" ? "text-amber-500" : "text-green-500"}`}>
                    {decision}
                </span>
            </p>
        )
    }

    if (node === "decomposer") {
        const subs = data.sub_questions as string[]
        return (
            <ul className="mt-1 space-y-0.5">
                {subs.map((sq, i) => (
                    <li key={i} className="text-xs text-muted-foreground flex gap-1.5">
                        <span className="text-primary font-semibold shrink-0">{i + 1}.</span>
                        {sq}
                    </li>
                ))}
            </ul>
        )
    }

    if (node === "rag_retrieve") {
        return (
            <p className="text-xs text-muted-foreground mt-0.5">
                Retrieved{" "}
                <span className="font-semibold text-foreground">{data.chunks_found as number}</span>
                {" "}unique chunks
            </p>
        )
    }

    if (node === "map_summarize") {
        return (
            <p className="text-xs text-muted-foreground mt-0.5">
                Summarized{" "}
                <span className="font-semibold text-foreground">{data.total_chunks as number}</span>
                {" "}chunks across{" "}
                <span className="font-semibold text-foreground">{data.batches as number}</span>
                {" "}batches
            </p>
        )
    }

    if (node === "compare_retrieve") {
        return (
            <p className="text-xs text-muted-foreground mt-0.5">
                Retrieved{" "}
                <span className="font-semibold text-foreground">{data.chunks_found as number}</span>
                {" "}chunks across{" "}
                <span className="font-semibold text-foreground">{(data.doc_ids as string[]).length}</span>
                {" "}documents
            </p>
        )
    }

    return null
}

export default function HopTrace({ traces }: HopTraceProps) {
    const [open, setOpen] = useState(false)

    if (traces.length === 0) return null

    return (
        <div className="mt-2 max-w-[75%] w-full">
            {/* Toggle button */}
            <button
                onClick={() => setOpen((o) => !o)}
                className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
                <span className="text-[10px]">{open ? "▾" : "▸"}</span>
                Reasoning chain ({traces.length} step{traces.length !== 1 ? "s" : ""})
            </button>

            {/* Collapsible hop list */}
            {open && (
                <div className="mt-2 border rounded-lg px-3 py-2 space-y-3 bg-muted/40">
                    {traces.map((trace, i) => {
                        const meta = NODE_META[trace.node] ?? { label: trace.node, icon: "•" }
                        return (
                            <div key={i} className="flex gap-2">
                                {/* Icon + connector line */}
                                <div className="flex flex-col items-center">
                                    <span className="text-primary text-sm font-bold leading-none">{meta.icon}</span>
                                    {i < traces.length - 1 && (
                                        <div className="w-px flex-1 bg-border mt-1" />
                                    )}
                                </div>
                                {/* Content */}
                                <div className="pb-1">
                                    <p className="text-xs font-semibold text-foreground">{meta.label}</p>
                                    <HopDetail {...trace} />
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}
        </div>
    )
}
