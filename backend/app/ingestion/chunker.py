# Populated in F1 - Document Upload and Ingestion
from llama_index.core.schema import Document
from llama_index.core.node_parser import SentenceSplitter

def chunk_documents(docs:list[Document],doc_id:str) -> list[dict]:
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(docs)

    chunks = []         

    for i, node in enumerate(nodes):
        chunks.append({
            "doc_id": doc_id,
            "page": node.metadata.get("page_label", 0),
            "chunk_index": i,
            "text": node.get_content(),
            "source": node.metadata.get("file_name", ""),
        })
    return chunks





    
