"""
Script completo para probar el sistema de chatbot Dr. Wilmer Gálvez
1. Ingesta del PDF Wilmer.pdf (elimina chunks existentes y crea nuevos)
2. Realiza consultas al chatbot para verificar el RAG

Ejecutar con: python test_full_workflow.py
NOTA: El servidor debe estar corriendo en http://localhost:8000
"""

import requests
from pathlib import Path
import json
import time


def test_health():
    """Verificar que el servidor esté activo."""
    print("🔍 Verificando servidor...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Servidor activo\n")
            return True
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}\n")
            return False
    except Exception as e:
        print(f"❌ Servidor no disponible: {str(e)}")
        print("   Por favor, inicia el servidor con: uvicorn app.main:app --reload --port 8000\n")
        return False


def ingest_pdf(pdf_path: str):
    """Ingestar PDF en la base de conocimiento."""
    print("="*60)
    print("📄 INGESTA DE PDF")
    print("="*60 + "\n")
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"❌ Error: El archivo {pdf_path} no existe\n")
        return False
    
    print(f"📂 Archivo: {pdf_file.name}")
    print(f"📊 Tamaño: {pdf_file.stat().st_size / 1024:.2f} KB\n")
    print("⏳ Procesando...")
    print("   - Eliminando chunks existentes en Supabase")
    print("   - Extrayendo texto del PDF")
    print("   - Dividiendo en chunks (1000 chars, overlap 200)")
    print("   - Generando embeddings con OpenAI")
    print("   - Indexando en Supabase vector store\n")
    
    url = "http://localhost:8000/ingest"
    
    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file.name, f, 'application/pdf')}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Ingesta exitosa!\n")
            print(f"   📝 {data['message']}")
            print(f"   📦 Chunks creados: {data['chunks_created']}")
            print(f"   📄 Archivo: {data['filename']}\n")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   📄 Detalle: {response.text}\n")
            return False
    except Exception as e:
        print(f"❌ Error durante la ingesta: {str(e)}\n")
        return False


def chat_with_streaming(message: str, show_header: bool = True):
    """Chatear con el agente Dr. Wilmer."""
    if show_header:
        print("="*60)
        print("💬 CHAT CON DR. WILMER GÁLVEZ")
        print("="*60 + "\n")
    
    print(f"👤 Usuario: {message}\n")
    print("🤖 Dr. Wilmer: ", end="", flush=True)
    
    url = "http://localhost:8000/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "message": message,
        "conversationHistory": []
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, stream=True)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    try:
                        event = json.loads(data_str)
                        if event.get("type") == "text":
                            content = event.get("content", "")
                            print(content, end="", flush=True)
                        elif event.get("type") == "done":
                            print("\n\n")
                        elif event.get("type") == "error":
                            print(f"\n❌ Error: {event.get('error')}\n")
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        print(f"\n❌ Error durante el chat: {str(e)}\n")


def main():
    """Flujo completo de prueba."""
    print("\n" + "="*60)
    print("🤖 TEST COMPLETO: Dr. Wilmer Gálvez Chatbot")
    print("="*60 + "\n")
    
    # 1. Verificar servidor
    if not test_health():
        return
    
    # 2. Ingestar PDF
    if not ingest_pdf("Wilmer.pdf"):
        print("⚠️  La ingesta falló, pero continuaremos con el chat\n")
    
    time.sleep(1)
    
    # 3. Probar el chatbot con preguntas generales
    chat_with_streaming("Hola, ¿quién eres?")
    
    time.sleep(0.5)
    
    # 4. Probar RAG con preguntas sobre el contenido del PDF
    print("-"*60 + "\n")
    chat_with_streaming("¿Cuáles son tus propuestas principales para El Alto?", show_header=False)
    
    time.sleep(0.5)
    
    print("-"*60 + "\n")
    chat_with_streaming("¿Qué piensas sobre la corrupción?", show_header=False)
    
    print("="*60)
    print("✅ TEST COMPLETADO")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
