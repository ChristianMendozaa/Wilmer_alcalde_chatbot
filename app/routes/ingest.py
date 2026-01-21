from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_service import document_service
from app.models.chat_models import IngestResponse


router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Ingest a PDF file into the knowledge base.
    
    This endpoint:
    1. Deletes all existing documents in the knowledge base
    2. Accepts a PDF file upload
    3. Extracts text from the PDF
    4. Splits the text into chunks
    5. Generates embeddings and stores them in Supabase
    
    Args:
        file: PDF file to ingest
        
    Returns:
        IngestResponse with success status, chunks deleted, and chunks created
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Solo se aceptan archivos PDF"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Process the PDF (this will clear existing docs and add new ones)
        from io import BytesIO
        file_obj = BytesIO(content)
        
        chunks_deleted, chunks_created = await document_service.process_pdf(
            file=file_obj,
            filename=file.filename,
            clear_existing=True
        )
        
        message = f"Base de conocimiento actualizada. Eliminados: {chunks_deleted} chunks, Creados: {chunks_created} chunks"
        
        return IngestResponse(
            success=True,
            message=message,
            chunks_created=chunks_created,
            filename=file.filename
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando el PDF: {str(e)}"
        )
