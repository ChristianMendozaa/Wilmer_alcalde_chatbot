"""
Script de prueba para el chatbot Dr. Wilmer Gálvez
Ejecutar con: python test_chat.py
"""

import requests
import json


def test_health():
    """Probar endpoint de health check."""
    print("🔍 Probando health check...")
    response = requests.get("http://localhost:8000/health")
    print(f"✅ Status: {response.status_code}")
    print(f"📄 Response: {response.json()}\n")


def test_chat_stream(message: str):
    """Probar endpoint de chat con streaming."""
    print(f"💬 Enviando mensaje: '{message}'")
    print("📡 Respuesta del Dr. Wilmer Gálvez:\n")
    
    url = "http://localhost:8000/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "message": message,
        "conversationHistory": []
    }
    
    response = requests.post(url, json=data, headers=headers, stream=True)
    
    full_response = ""
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]  # Remove 'data: ' prefix
                try:
                    event = json.loads(data_str)
                    if event.get("type") == "text":
                        content = event.get("content", "")
                        print(content, end="", flush=True)
                        full_response += content
                    elif event.get("type") == "done":
                        print("\n\n✅ Streaming completado")
                    elif event.get("type") == "error":
                        print(f"\n❌ Error: {event.get('error')}")
                except json.JSONDecodeError:
                    pass
    
    return full_response


def test_with_conversation_history():
    """Probar chat con historial de conversación."""
    print("\n" + "="*60)
    print("🔄 Probando chat con historial de conversación")
    print("="*60 + "\n")
    
    url = "http://localhost:8000/api/chat"
    headers = {"Content-Type": "application/json"}
    
    # Primera pregunta
    message1 = "Hola, ¿quién eres?"
    print(f"💬 Usuario: {message1}\n")
    
    data1 = {
        "message": message1,
        "conversationHistory": []
    }
    
    response1 = requests.post(url, json=data1, headers=headers, stream=True)
    
    response1_text = ""
    for line in response1.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                try:
                    event = json.loads(data_str)
                    if event.get("type") == "text":
                        content = event.get("content", "")
                        print(content, end="", flush=True)
                        response1_text += content
                except json.JSONDecodeError:
                    pass
    
    print("\n\n" + "-"*60 + "\n")
    
    # Segunda pregunta con historial
    message2 = "¿Cuál es tu slogan?"
    print(f"💬 Usuario: {message2}\n")
    
    data2 = {
        "message": message2,
        "conversationHistory": [
            {"role": "user", "content": message1},
            {"role": "assistant", "content": response1_text}
        ]
    }
    
    response2 = requests.post(url, json=data2, headers=headers, stream=True)
    
    for line in response2.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                try:
                    event = json.loads(data_str)
                    if event.get("type") == "text":
                        content = event.get("content", "")
                        print(content, end="", flush=True)
                except json.JSONDecodeError:
                    pass
    
    print("\n\n✅ Test completado\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 TEST: Dr. Wilmer Gálvez Chatbot API")
    print("="*60 + "\n")
    
    # Test 1: Health check
    test_health()
    
    # Test 2: Chat simple
    print("="*60)
    print("💬 Test de Chat Simple")
    print("="*60 + "\n")
    test_chat_stream("¿Cuál es tu compromiso principal para El Alto?")
    
    # Test 3: Chat con historial
    test_with_conversation_history()
    
    print("="*60)
    print("✅ TODOS LOS TESTS COMPLETADOS")
    print("="*60)
