# Populate
from pathlib import Path
from llama_index.core.schema import Document
from llama_index.readers.file import PDFReader, DocxReader
from llama_index.readers.web import SimpleWebPageReader

def load_documents(source: str) -> list[Document]:
    #for url sources, use SimpleWebPageReader
    if source.startswith("http"):
        return SimpleWebPageReader(html_to_text=True).load_data(urls=[source])

    else:
        source_path = Path(source)
        if source_path.is_file():
            if source_path.suffix == ".pdf":
                return PDFReader().load_data(file=source_path)
            elif source_path.suffix == ".docx":
                return DocxReader().load_data(file=source_path)
            elif source_path.suffix in (".txt", ".md"):
                content = source_path.read_text(encoding="utf-8")
                return [Document(text=content, metadata={"file_name": source_path.name})]
            else:
                raise ValueError(f"Unsupported file type: {source_path.suffix}")
        else:
            raise ValueError(f"File not found: {source}")



