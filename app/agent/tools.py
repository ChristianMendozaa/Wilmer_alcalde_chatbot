from langchain.tools import Tool
from langchain_core.documents import Document
from app.db.supabase_client import get_vector_store
from app.config import settings


def create_rag_tool() -> Tool:
    """
    Create a RAG (Retrieval-Augmented Generation) tool for the agent.
    
    This tool allows the agent to search for relevant information in the
    knowledge base stored in Supabase.
    
    Returns:
        Tool: LangChain tool for RAG queries
    """
    
    def search_knowledge_base(query: str) -> str:
        """
        Search the knowledge base for relevant information.
        
        Args:
            query: Search query
            
        Returns:
            Formatted string with relevant documents
        """
        vector_store = get_vector_store()
        
        # Perform similarity search
        results: list[Document] = vector_store.similarity_search(
            query=query,
            k=settings.similarity_top_k
        )
        
        if not results:
            return "No se encontró información relevante en la base de conocimiento."
        
        # Format results
        formatted_results = []
        for i, doc in enumerate(results, 1):
            metadata = doc.metadata
            source_info = f"Fuente: {metadata.get('filename', 'Desconocido')}"
            if 'page' in metadata:
                source_info += f", Página {metadata['page']}"
            
            formatted_results.append(
                f"[Resultado {i}]\n"
                f"{source_info}\n"
                f"Contenido: {doc.page_content}\n"
            )
        
        return "\n---\n".join(formatted_results)
    
    return Tool(
        name="buscar_propuestas",
        description=(
            "Busca información sobre las propuestas, planes de gobierno, "
            "compromisos y posiciones del Dr. Wilmer Gálvez. "
            "Usa esta herramienta SIEMPRE que el usuario pregunte sobre "
            "propuestas específicas, planes, o cualquier tema relacionado "
            "con el programa de gobierno. "
            "Input: pregunta o tema a buscar en formato de texto."
        ),
        func=search_knowledge_base
    )


# Additional tools can be added here in the future
# For example:
# - Tool for querying voting statistics
# - Tool for checking event schedules
# - Tool for getting contact information
# etc.
