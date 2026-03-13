// Populated in F2 - Basic Q&A
// Renders a single chat message — right-aligned for user, left-aligned for assistant

interface MessageBubbleProps {
    role: "user" | "assistant"
    content: string
}

// Displays one message bubble with different styles depending on who sent it
export default function MessageBubble({ role, content }: MessageBubbleProps) {
    const isUser = role === "user"

    return (
        <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
            <div
                className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                    isUser
                        ? "bg-primary text-primary-foreground rounded-br-sm"
                        : "bg-muted text-foreground rounded-bl-sm"
                }`}
            >
                {content}
            </div>
        </div>
    )
}
