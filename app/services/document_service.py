from typing import BinaryIO
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config import settings
from app.db.supabase_client import get_vector_store, clear_all_documents


class DocumentService:
    """Service for processing and indexing documents."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, file: BinaryIO, filename: str) -> list[Document]:
        """
        Extract text from a PDF file and convert to documents.
        
        Args:
            file: Binary file object
            filename: Name of the file
            
        Returns:
            List of Document objects with text and metadata
        """
        pdf_reader = PdfReader(file)
        documents = []
        
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            if text.strip():  # Only add non-empty pages
                doc = Document(
                    page_content=text,
                    metadata={
                        "filename": filename,
                        "page": page_num,
                        "total_pages": len(pdf_reader.pages)
                    }
                )
                documents.append(doc)
        
        return documents
    
    def chunk_documents(self, documents: list[Document]) -> list[Document]:
        """
        Split documents into smaller chunks.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        return self.text_splitter.split_documents(documents)
    
    async def index_documents(self, documents: list[Document]) -> int:
        """
        Index documents into Supabase vector store.
        
        Args:
            documents: List of Document objects to index
            
        Returns:
            Number of documents indexed
        """
        vector_store = get_vector_store()
        
        # Extract texts and metadatas
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Add to vector store
        await vector_store.aadd_texts(texts=texts, metadatas=metadatas)
        
        return len(documents)
    
    async def process_pdf(self, file: BinaryIO, filename: str, clear_existing: bool = True) -> tuple[int, int]:
        """
        Complete pipeline: extract, chunk, and index a PDF.
        
        Args:
            file: Binary file object
            filename: Name of the file
            clear_existing: If True, clear all existing documents before indexing (default: True)
            
        Returns:
            Tuple of (chunks_deleted, chunks_created)
        """
        chunks_deleted = 0
        
        # Clear existing documents if requested
        if clear_existing:
            chunks_deleted = clear_all_documents()
        
        # Extract text from PDF
        documents = self.extract_text_from_pdf(file, filename)
        
        # Chunk documents
        chunks = self.chunk_documents(documents)
        
        # Index into vector store
        num_indexed = await self.index_documents(chunks)
        
        return chunks_deleted, num_indexed


# Singleton instance
document_service = DocumentService()
