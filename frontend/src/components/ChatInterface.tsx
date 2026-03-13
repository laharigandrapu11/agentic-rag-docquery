// Populated in F2 - Basic Q&A
// Extended in F3 - Streaming and Citations
// Full chat panel: message history + input box + send button

"use client"

import { useState, useRef, useEffect } from "react"
import { sendQuery } from "@/lib/api"
import MessageBubble from "@/components/MessageBubble"

// A single message in the conversation history
interface Message {
    role: "user" | "assistant"
    content: string
}

// Main chat component — handles state, API calls, and rendering the message list
export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Used to auto-scroll to the latest message after each response
    const bottomRef = useRef<HTMLDivElement>(null)
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    // Called when the user submits a question
    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        const question = input.trim()
        if (!question || loading) return

        // Add user message immediately so the UI feels responsive
        setMessages((prev) => [...prev, { role: "user", content: question }])
        setInput("")
        setLoading(true)
        setError(null)

        try {
            const res = await sendQuery({ question })
            // Append the assistant's answer once the backend responds
            setMessages((prev) => [...prev, { role: "assistant", content: res.answer }])
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong")
        } finally {
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
                    <MessageBubble key={i} role={msg.role} content={msg.content} />
                ))}
                {/* Loading indicator while waiting for the backend */}
                {loading && (
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
