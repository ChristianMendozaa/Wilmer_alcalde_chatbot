from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import create_rag_tool


def create_wilmer_agent() -> AgentExecutor:
    """
    Create and configure the Dr. Wilmer Gálvez agent with RAG capabilities.
    
    Returns:
        AgentExecutor: Configured LangChain agent ready to process queries
    """
    
    # Initialize Groq LLM
    llm = ChatGroq(
        groq_api_key=settings.groq_api_key,
        model_name=settings.groq_model,
        temperature=0.7,
        streaming=True
    )
    
    # Create tools list
    tools = [
        create_rag_tool(),
    ]
    
    # Create the Tool Calling prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create the Tool Calling agent
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create agent executor with streaming support
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        # Custom error handling: if parsing fails, assume the output is the final answer (often happens with "Invalid Format: Missing 'Action:'")
        handle_parsing_errors=lambda error: str(error).split("Could not parse LLM output: `")[1].split("`")[0] if "Could not parse LLM output: `" in str(error) else "Lo siento, hubo un error técnico al procesar tu respuesta. Por favor intenta de nuevo.",
        max_iterations=5,
        return_intermediate_steps=False
    )
    
    return agent_executor


# Singleton instance - lazily initialized
_agent_executor = None


def get_agent() -> AgentExecutor:
    """
    Get the singleton agent executor instance.
    
    Returns:
        AgentExecutor: The configured agent
    """
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = create_wilmer_agent()
    return _agent_executor
