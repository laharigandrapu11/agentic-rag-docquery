// API client - populated progressively from F1 onwards
export interface DocumentMeta {
    doc_id: string
    filename: string
    source: string
    chunk_count: number
    created_at: string
}

export interface UploadResponse {
    doc_id: string
    filename: string
    chunk_count: number
}

export interface DeleteResponse {
    doc_id: string
    deleted: boolean
}

const BASE_URL = "http://localhost:8000/api"

export async function uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append("file", file)
    const res = await fetch(BASE_URL + "/upload", {
        method: "POST",
        body: formData,
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
}

export async function uploadUrl(url: string): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append("url", url)
    const res = await fetch(BASE_URL + "/upload", {
        method: "POST",
        body: formData,
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
}

export async function getDocuments(): Promise<DocumentMeta[]> {
    const res = await fetch(BASE_URL + "/documents")
    if (!res.ok) throw new Error(await res.text())
    return res.json()
}

export async function deleteDocument(doc_id: string): Promise<DeleteResponse> {
    const res = await fetch(BASE_URL + "/documents/" + doc_id, {
        method: "DELETE",
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
}

// Shape of the question payload sent to POST /query
export interface QueryRequest {
    question: string
    provider?: string  // defaults to "groq" on the backend
    top_k?: number     // how many chunks to retrieve, defaults to 5
}

// A single citation chunk streamed back after the answer tokens
export interface CitationChunk {
    doc_id: string
    source: string   // filename
    page: string     // page number as string
    chunk_index: number
    text: string     // the actual chunk text shown in the citation panel
}

// Streams the answer token by token from POST /query (SSE).
// onToken   — called for each word/token as it arrives
// onCitation — called for each source citation after the answer
// onDone    — called once the stream is fully complete
export async function streamQuery(
    request: QueryRequest,
    onToken: (token: string) => void,
    onCitation: (c: CitationChunk) => void,
    onDone: () => void,
) {
    const res = await fetch(BASE_URL + "/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
    })

    if (!res.ok) throw new Error(await res.text())

    // res.body is a ReadableStream of raw bytes — we read it chunk by chunk
    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ""

    while (true) {
        const { done, value } = await reader.read()
        if (done) break

        // Decode incoming bytes and add to buffer
        buffer += decoder.decode(value, { stream: true })

        // SSE events are separated by "\n\n" — split and process complete ones
        const events = buffer.split("\n\n")
        // The last element may be an incomplete event — keep it in the buffer
        buffer = events.pop() ?? ""

        for (const event of events) {
            if (!event.startsWith("data: ")) continue
            const data = JSON.parse(event.slice(6))  // strip "data: " prefix (6 chars)

            if (data.type === "token") onToken(data.content)
            else if (data.type === "citation") onCitation(data as CitationChunk)
            else if (data.type === "done") onDone()
        }
    }
}