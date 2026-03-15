"use client"

// Full chat panel: message history + streaming assistant answers + citations
// Extended in F3 — tokens stream in live, citations appear after the answer
// Extended in F4 — hop_trace events build up the reasoning chain in real time

import { useState, useRef, useEffect } from "react"
import { streamQuery, CitationChunk, HopTraceEvent } from "@/lib/api"
import MessageBubble from "@/components/MessageBubble"

// A single message in the conversation history
interface Message {
    role: "user" | "assistant"
    content: string
    citations: CitationChunk[]
    hopTraces: HopTraceEvent[]  // reasoning chain steps collected during streaming
}

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Auto-scroll to the bottom after each message update
    const bottomRef = useRef<HTMLDivElement>(null)
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        const question = input.trim()
        if (!question || loading) return

        // Add user message immediately so the UI feels responsive
        setMessages((prev) => [...prev, { role: "user", content: question, citations: [], hopTraces: [] }])
        setInput("")
        setLoading(true)
        setError(null)

        // Add an empty assistant bubble that will be filled token by token
        setMessages((prev) => [...prev, { role: "assistant", content: "", citations: [], hopTraces: [] }])

        try {
            await streamQuery(
                { question },
                // onToken — append each new token to the last (assistant) message
                (token) => {
                    setMessages((prev) => {
                        const updated = [...prev]
                        const last = updated[updated.length - 1]
                        updated[updated.length - 1] = { ...last, content: last.content + token }
                        return updated
                    })
                },
                // onCitation — collect citations into the assistant message
                (citation) => {
                    setMessages((prev) => {
                        const updated = [...prev]
                        const last = updated[updated.length - 1]
                        updated[updated.length - 1] = {
                            ...last,
                            citations: [...last.citations, citation],
                        }
                        return updated
                    })
                },
                // onDone — stream finished
                () => setLoading(false),
                // onHopTrace — append each reasoning step to the assistant message
                (hop) => {
                    setMessages((prev) => {
                        const updated = [...prev]
                        const last = updated[updated.length - 1]
                        updated[updated.length - 1] = {
                            ...last,
                            hopTraces: [...last.hopTraces, hop],
                        }
                        return updated
                    })
                },
            )
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong")
            setLoading(false)
        }
    }

    return (
        <div className="flex flex-col h-[600px] border rounded-xl bg-card overflow-hidden">

            {/* Scrollable message history */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
                {messages.length === 0 && (
                    <p className="text-sm text-muted-foreground text-center mt-8">
                        Ask a question about your uploaded documents.
                    </p>
                )}
                {messages.map((msg, i) => (
                    <MessageBubble
                        key={i}
                        role={msg.role}
                        content={msg.content}
                        citations={msg.citations}
                        hopTraces={msg.hopTraces}
                    />
                ))}
                {/* Show "Thinking…" only while waiting for the first token */}
                {loading && messages[messages.length - 1]?.content === "" && (
                    <div className="flex justify-start">
                        <div className="bg-muted rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm text-muted-foreground">
                            Thinking…
                        </div>
                    </div>
                )}
                {error && (
                    <p className="text-xs text-destructive text-center">{error}</p>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Input box pinned to the bottom */}
            <form onSubmit={handleSubmit} className="border-t px-4 py-3 flex gap-2">
                <input
                    className="flex-1 rounded-lg border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    placeholder="Ask a question…"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={loading}
                />
                <button
                    type="submit"
                    disabled={loading || !input.trim()}
                    className="rounded-lg bg-primary text-primary-foreground px-4 py-2 text-sm font-medium disabled:opacity-50"
                >
                    Send
                </button>
            </form>
        </div>
    )
}
