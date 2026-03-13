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

// A single retrieved chunk returned alongside the answer
export interface ChunkSource {
    doc_id: string
    source: string
    page: number
    chunk_index: number
    text: string
}

// Shape of the response from POST /query
export interface QueryResponse {
    answer: string
    sources: ChunkSource[]
}

// Sends a question to the backend and returns the answer + source chunks
export async function sendQuery(req: QueryRequest): Promise<QueryResponse> {
    const res = await fetch(BASE_URL + "/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
}