"use client"

// Segmented button group that lets the user pick between Groq, Gemini, and Mistral.
// The active provider is highlighted. Clicking a button calls onChange so the
// parent (ChatInterface) can store the selection and pass it with every query.

const PROVIDERS = [
    { id: "groq",    label: "Groq" },
    { id: "gemini",  label: "Gemini" },
    { id: "mistral", label: "Mistral" },
]

interface Props {
    provider: string           // currently selected provider id
    onChange: (p: string) => void  // called when user clicks a different provider
    disabled?: boolean         // true while a query is in flight — prevents mid-stream switching
}

export default function ProviderSelector({ provider, onChange, disabled }: Props) {
    return (
        <div className="flex items-center gap-1 bg-muted rounded-lg p-1">
            {PROVIDERS.map((p) => (
                <button
                    key={p.id}
                    onClick={() => onChange(p.id)}
                    disabled={disabled}
                    className={`px-3 py-1 text-xs font-medium rounded-md transition-colors
                        ${provider === p.id
                            // active provider: white background to stand out from the muted container
                            ? "bg-background text-foreground shadow-sm"
                            // inactive: muted text, highlights on hover
                            : "text-muted-foreground hover:text-foreground"
                        } disabled:opacity-50`}
                >
                    {p.label}
                </button>
            ))}
        </div>
    )
}
