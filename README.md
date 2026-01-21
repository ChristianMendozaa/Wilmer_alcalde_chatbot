# Dr. Wilmer Gálvez Chatbot API

API del chatbot agente para el Dr. Wilmer Gálvez, candidato a la Alcaldía de El Alto 2026 por la alianza LIBRE.

## 🚀 Inicio Rápido

### 1. Activar el entorno virtual e instalar dependencias

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Asegúrate de que tu archivo `.env` contenga:

```env
GROQ_API_KEY=tu_groq_api_key
OPENAI_API_KEY=tu_openai_api_key
SUPABASE_URL=tu_supabase_url
SUPABASE_SERVICE_ROLE_KEY=tu_supabase_service_role_key
```

### 3. Iniciar el servidor

```powershell
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

## 📚 Documentación API

### Endpoints Disponibles

#### 1. Health Check

```http
GET /
GET /health
```

Verifica que el servicio esté funcionando.

#### 2. Ingestar PDF

```http
POST /ingest
Content-Type: multipart/form-data
```

**Descripción**: Procesa un PDF con propuestas del Dr. Wilmer Gálvez. **IMPORTANTE: Este endpoint elimina todos los chunks existentes antes de indexar el nuevo PDF**, permitiendo actualizar completamente la base de conocimiento.

**Ejemplo con curl (PowerShell)**:

```powershell
$form = @{
    file = Get-Item -Path "Wilmer.pdf"
}
Invoke-RestMethod -Uri "http://localhost:8000/ingest" -Method Post -Form $form
```

**Respuesta**:

```json
{
  "success": true,
  "message": "Base de conocimiento actualizada. Eliminados: 35 chunks, Creados: 42 chunks",
  "chunks_created": 42,
  "filename": "Wilmer.pdf"
}
```

#### 3. Chat con Streaming

```http
POST /api/chat
Content-Type: application/json
```

**Descripción**: Inicia una conversación con el agente Dr. Wilmer Gálvez. Retorna la respuesta token por token usando Server-Sent Events (compatible con Vercel AI SDK).

**Ejemplo con curl (PowerShell)**:

```powershell
$body = @{
    message = "¿Cuáles son tus propuestas para combatir la corrupción en El Alto?"
    conversationHistory = @()
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/chat" -Method Post -Body $body -ContentType "application/json"
```

**Request Body**:

```json
{
  "message": "¿Cuáles son tus propuestas para combatir la corrupción?",
  "conversationHistory": [
    {
      "role": "user",
      "content": "Hola"
    },
    {
      "role": "assistant",
      "content": "¡Hola vecino alteño! Soy el Dr. Wilmer Gálvez..."
    }
  ]
}
```

**Respuesta (SSE Stream)**:

```
data: {"type":"text","content":"Como"}
data: {"type":"text","content":" candidato"}
data: {"type":"text","content":" con"}
data: {"type":"text","content":" el"}
data: {"type":"text","content":" slogan"}
...
data: {"type":"done"}
```

## 🏗️ Arquitectura

```
app/
├── main.py                 # Aplicación FastAPI principal
├── config.py              # Configuración y variables de entorno
├── agent/                 # Módulo del agente
│   ├── prompts.py        # System prompt de Dr. Wilmer Gálvez
│   ├── tools.py          # Herramientas (RAG + extensibles)
│   └── wilmer_agent.py   # Configuración del agente LangChain
├── db/                    # Módulo de base de datos
│   └── supabase_client.py # Cliente Supabase y vector store
├── routes/                # Endpoints API
│   ├── ingest.py         # Endpoint de ingesta de PDFs
│   └── chat.py           # Endpoint de chat con streaming
├── services/              # Servicios de negocio
│   └── document_service.py # Procesamiento de documentos
└── models/                # Modelos Pydantic
    └── chat_models.py    # Modelos de request/response
```

## 🧠 Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **LangChain**: Framework para aplicaciones con LLM
- **Groq**: LLM ultra-rápido (`llama-3.3-70b-versatile`)
- **OpenAI**: Embeddings (`text-embedding-3-small`)
- **Supabase**: Vector database para RAG
- **pypdf**: Extracción de texto desde PDFs

## 🤖 Personalidad del Agente

El agente está configurado con un `SYSTEM_PROMPT` que define:

- ✅ **Identidad**: Profesional técnico (Dr.), outsider político
- ✅ **Slogan**: "Sin cola de paja"
- ✅ **Compromiso**: Luchar contra la corrupción ("meter presos a los saqueadores")
- ✅ **Tono**: Cercano al vecino alteño, técnico pero accesible
- ✅ **Ética**: Admite cuando no sabe algo, NUNCA inventa información
- ✅ **Enfoque**: Propuestas técnicas, sin guerra sucia

## 📝 Próximos Pasos

1. **Ingestar documentos**: Ejecuta el script de prueba completo que ingesta `Wilmer.pdf`:
   ```powershell
   python test_full_workflow.py
   ```
2. **Probar el chat**: El script anterior también prueba el chat con consultas sobre el contenido
3. **Integrar frontend**: Conecta el frontend usando el formato de streaming compatible con Vercel AI SDK
4. **Agregar más tools**: Extiende las capacidades del agente agregando nuevas herramientas en `app/agent/tools.py`
5. **Actualizar base de conocimiento**: Simply sube un nuevo PDF con `/ingest` - automáticamente reemplazará el contenido anterior

## 🔗 Enlaces Útiles

- **Documentación interactiva**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
