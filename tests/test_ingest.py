"""
Script para probar la ingesta de PDF
Ejecutar con: python test_ingest.py
"""

import requests
from pathlib import Path


def test_ingest_pdf(pdf_path: str):
    """Probar el endpoint de ingesta de PDF."""
    print("="*60)
    print("🔍 TEST: Ingesta de PDF")
    print("="*60 + "\n")
    
    # Verificar que el archivo existe
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"❌ Error: El archivo {pdf_path} no existe")
        return
    
    print(f"📄 Archivo: {pdf_file.name}")
    print(f"📊 Tamaño: {pdf_file.stat().st_size / 1024:.2f} KB\n")
    print("⏳ Procesando PDF...")
    print("   - Eliminando chunks existentes")
    print("   - Extrayendo texto del PDF")
    print("   - Dividiendo en chunks")
    print("   - Generando embeddings")
    print("   - Indexando en Supabase\n")
    
    url = "http://localhost:8000/ingest"
    
    with open(pdf_file, 'rb') as f:
        files = {'file': (pdf_file.name, f, 'application/pdf')}
        response = requests.post(url, files=files)
    
    print("-"*60)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Ingesta exitosa!\n")
        print(f"📝 Mensaje: {data['message']}")
        print(f"📦 Chunks creados: {data['chunks_created']}")
        print(f"📄 Archivo: {data['filename']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"📄 Detalle: {response.text}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # Probar con el archivo Wilmer.pdf
    test_ingest_pdf("Wilmer.pdf")
