from langchain_groq import ChatGroq
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
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
    
    # Create tools list (RAG tool + future tools)
    tools = [
        create_rag_tool(),
        # Add more tools here as needed
    ]
    
    # Create the ReAct prompt template
    template = """
{system_prompt}

Tienes acceso a las siguientes herramientas:

{tools}

Usa el siguiente formato:

Question: la pregunta del usuario
Thought: debes pensar siempre qué hacer
Action: la acción a tomar, debe ser una de [{tool_names}]
Action Input: el input para la acción
Observation: el resultado de la acción
... (este proceso Thought/Action/Action Input/Observation puede repetirse N veces)
Thought: Ahora sé la respuesta final
Final Answer: la respuesta final al usuario

IMPORTANTE: Siempre usa la herramienta "buscar_propuestas" antes de responder sobre propuestas o planes de gobierno.

Conversación actual:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}
"""
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["input", "agent_scratchpad", "chat_history"],
        partial_variables={
            "system_prompt": SYSTEM_PROMPT,
            "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
            "tool_names": ", ".join([tool.name for tool in tools])
        }
    )
    
    # Create the ReAct agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create agent executor with streaming support
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
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
