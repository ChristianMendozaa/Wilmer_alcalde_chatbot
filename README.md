# Dr. Wilmer Gálvez Chatbot API

![Status](https://img.shields.io/badge/Status-Active-success)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.13+-yellow)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688)

Professional AI agent service for Dr. Wilmer Gálvez, Mayoral Candidate for El Alto 2026 (LIBRE alliance). This service provides a robust, streaming-enabled chat interface powered by advanced LLMs and RAG (Retrieval-Augmented Generation) technology.

## 🏗️ Architecture

The system is designed as a modular microservice using FastAPI, LangChain, and Supabase.

```mermaid
graph TD
    Client[Frontend Client (Next.js)]
    
    subgraph "FastAPI Microservice"
        API[API Router]
        Agent[LangChain Agent Host]
    end
    
    subgraph "Knowledge Base"
        Supabase[(Supabase Vector Store)]
    end
    
    subgraph "External AI Services"
        Groq[Groq API (Inference)]
        OpenAI[OpenAI API (Embeddings)]
    end

    Client -- "SSE Stream (Token-by-token)" --> API
    API --> Agent
    
    Agent -- "Reasoning & Tool Calls" --> Groq
    Agent -- "Semantic Search" --> Supabase
    Supabase -- "Context/Chunks" --> Agent
    
    Ingest[PDF Ingestion] -- "Parse & Embed" --> OpenAI
    OpenAI -- "Vectors" --> Supabase
```

## 🚀 Key Features

*   **Streaming Support**: Native Server-Sent Events (SSE) support for real-time token streaming, compatible with Vercel AI SDK.
*   **Tool Calling Agent**: Utilizes modern tool-calling capabilities of LLMs for precise action execution.
*   **RAG Integration**: Retrieval-Augmented Generation using Supabase `pgvector` for accurate, context-aware responses based on official campaign documents.
*   **Modular Design**: Clean separation of concerns between routing, agent logic, and database interactions.

## 🔧 Technical Decisions

### Inference Engine: `openai/gpt-oss-20b` via Groq
We selected the **`openai/gpt-oss-20b`** model hosted on **Groq** for the following reasons:

1.  **Latency & Speed**: Groq's LPU (Language Processing Unit) architecture delivers exceptionally fast inference speeds (>300 tokens/s), which is crucial for a responsive real-time chat experience that feels conversational and instant.
2.  **Cost-Effectiveness**: The 20B parameter model offers an optimal balance between reasoning capability and operational cost. It is sufficiently powerful to understand complex queries and strictly follow the system prompt (Dr. Wilmer Gálvez persona) without the overhead of larger 70B+ models.
3.  **Accuracy**: For the specific domain of campaign proposals, the model's ability to utilize RAG tools effectively allows it to provide highly accurate answers grounded in the provided context, minimizing hallucinations.

### Vector Storage: Supabase & `pgvector`
We use Supabase with the `pgvector` extension to store document embeddings. This allows for:
*   **Hybrid Search**: Combining semantic vector search with keyword filtering if needed.
*   **Scalability**: Built on PostgreSQL, ensuring reliability and easy management.

### Orchestration: LangChain
LangChain provides the framework for:
*   **Agent Logic**: Managing the ReAct/Tool-calling loop.
*   **Prompt Management**: Templating the sophisticated "Dr. Wilmer Gálvez" persona.
*   **Tool Binding**: Standardizing the interface between the LLM and the vector store.

## 🛠️ Quick Start

### 1. Prerequisites
*   Python 3.10+
*   Supabase account
*   Groq API Key
*   OpenAI API Key (for embeddings)

### 2. Installation

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_key
```

### 4. Running the Server

```bash
uvicorn app.main:app --reload --port 8000
```
Server will be available at `http://localhost:8000`.

## 📚 API Documentation

### Chat Endpoint
*   **URL**: `POST /api/chat`
*   **Description**: Streaming chat interface. accepts a list of conversation messages and streams the assistant's response.

### Ingestion Endpoint
*   **URL**: `POST /ingest`
*   **Description**: Uploads and indexes a PDF file.
    *   *Note*: This performs a full refresh (deletes old chunks) to ensure the knowledge base is always 1:1 with the official source.

## 🤖 Agent Persona

The agent is strictly instructed to embody Dr. Wilmer Gálvez:
*   **Tone**: Professional yet accessible ("vecino alteño").
*   **Slogan**: "Sin cola de paja" (Without corruption/baggage).
*   **Core Promise**: "Meter presos a los saqueadores" (Jail the plunderers).
*   **Behavior**: It **always** consults the knowledge base for specific proposals and refuses to invent information.

---
*Developed for the "La Paz del Futuro" Campaign 2026*
