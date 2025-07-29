from typing import List
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class JTechRobotFrameworkAIAgent:
    """Classe que fornece agentes para interação com IA."""
    
    def __init__(self):
        """Inicializa a classe."""
        load_dotenv()
        # Verificar se a chave da API está disponível
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",  # Usar modelo mais específico
                google_api_key=api_key,
                temperature=0.7,
            )
        else:
            self.llm = None
    
    def query_agent(self) -> Agent:
        """Cria um agente para executar consultas.
        
        Returns:
            Agent: Agente configurado para executar consultas.
        """
        return Agent(
            role="Especialista em Consultas SQL",
            goal="Executar consultas SQL de forma eficiente e segura",
            backstory="""Você é um especialista em SQL com vasta experiência em PostgreSQL.
            Sua função é ajudar a executar consultas SQL de forma eficiente e segura,
            garantindo que os resultados sejam precisos e úteis.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[],  # Removendo ferramentas por enquanto
        )
    
    def query_research_agent(self) -> Agent:
        """Cria um agente para analisar resultados.
        
        Returns:
            Agent: Agente configurado para analisar resultados.
        """
        return Agent(
            role="Analista de Dados",
            goal="Analisar e interpretar resultados de consultas SQL",
            backstory="""Você é um analista de dados experiente, especializado em
            interpretar resultados de consultas SQL e transformá-los em insights
            úteis e acionáveis.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
        )
    
    def get_agents(self) -> List[Agent]:
        """Retorna a lista de agentes disponíveis.
        
        Returns:
            List[Agent]: Lista de agentes configurados.
        """
        return [self.query_agent(), self.query_research_agent()]

