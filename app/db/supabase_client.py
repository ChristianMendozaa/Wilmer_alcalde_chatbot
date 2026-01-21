from supabase import create_client, Client
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from app.config import settings


# Initialize Supabase client
supabase_client: Client = create_client(
    supabase_url=settings.supabase_url,
    supabase_key=settings.supabase_service_role_key
)

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(
    openai_api_key=settings.openai_api_key,
    model=settings.openai_embedding_model
)


def get_vector_store() -> SupabaseVectorStore:
    """
    Get or create the Supabase vector store instance.
    
    Returns:
        SupabaseVectorStore: Configured vector store for wilmer_documents table
    """
    return SupabaseVectorStore(
        client=supabase_client,
        embedding=embeddings,
        table_name="wilmer_documents",
        query_name="match_wilmer_documents"
    )


def clear_all_documents() -> int:
    """
    Delete all documents from the wilmer_documents table.
    
    Returns:
        int: Number of documents deleted
    """
    try:
        # Get all document IDs
        response = supabase_client.table("wilmer_documents").select("id").execute()
        count = len(response.data) if response.data else 0
        
        if count > 0:
            # Delete each document individually to avoid type conversion issues
            for doc in response.data:
                supabase_client.table("wilmer_documents").delete().eq("id", doc["id"]).execute()
        
        return count
    except Exception as e:
        print(f"Error clearing documents: {e}")
        return 0
