// Renders a single chat message bubble.
// User messages are right-aligned; assistant messages are left-aligned.
// For assistant messages, [Source N] markers are highlighted as badges.
// Extended in F4 - shows HopTrace reasoning chain above citations.

import { CitationChunk, HopTraceEvent } from "@/lib/api"
import SourceCitation from "@/components/SourceCitation"
import HopTrace from "@/components/HopTrace"

interface MessageBubbleProps {
    role: "user" | "assistant"
    content: string
    citations?: CitationChunk[]     // only present on assistant messages
    hopTraces?: HopTraceEvent[]     // reasoning chain steps, F4+
}

// Converts [Source N] markers in text into highlighted badge spans
function renderWithCitations(text: string) {
    const parts = text.split(/(\[Source \d+\])/g)
    return parts.map((part, i) =>
        /^\[Source \d+\]$/.test(part) ? (
            <span
                key={i}
                className="inline-block bg-primary/15 text-primary text-[10px] font-semibold px-1.5 py-0.5 rounded mx-0.5 align-middle"
            >
                {part}
            </span>
        ) : (
            <span key={i}>{part}</span>
        )
    )
}

export default function MessageBubble({ role, content, citations = [], hopTraces = [] }: MessageBubbleProps) {
    const isUser = role === "user"

    return (
        <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
            <div
                className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                    isUser
                        ? "bg-primary text-primary-foreground rounded-br-sm"
                        : "bg-muted text-foreground rounded-bl-sm"
                }`}
            >
                {/* For assistant messages, render [Source N] as styled badges */}
                {isUser ? content : renderWithCitations(content)}
            </div>

            {/* Reasoning chain — shown before citations, only on assistant messages */}
            {!isUser && <HopTrace traces={hopTraces} />}

            {/* Source citations panel below assistant messages */}
            {!isUser && citations.length > 0 && (
                <div className="max-w-[75%] w-full">
                    <SourceCitation citations={citations} />
                </div>
            )}
        </div>
    )
}
