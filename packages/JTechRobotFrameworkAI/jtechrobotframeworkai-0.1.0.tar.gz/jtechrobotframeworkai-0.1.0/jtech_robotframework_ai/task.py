from typing import List
from crewai import Task
import logging

from jtech_robotframework_ai.agent import JTechRobotFrameworkAIAgent

logger = logging.getLogger(__name__)

class JTechRobotFrameworkAITask:
    def __init__(self):
        self.query_agent = JTechRobotFrameworkAIAgent().query_agent()
        self.query_research_agent = JTechRobotFrameworkAIAgent().query_research_agent()
        self.agents = JTechRobotFrameworkAIAgent().get_agents()

    def query_task(self, pergunta: str) -> Task:
        """Cria uma task para executar a consulta SQL.
        
        Args:
            pergunta: A pergunta ou instrução para processar.
            
        Returns:
            Task: Task configurada para executar a consulta.
        """
        return Task(
            description=f"""
                Analise a seguinte pergunta e execute as ações necessárias:
                
                "{pergunta}"
                
                Considere os seguintes aspectos:
                1. Identifique as tabelas relevantes para a consulta
                2. Gere uma consulta SQL apropriada
                3. Execute a consulta usando as ferramentas disponíveis
                4. Formate os resultados de forma clara
                
                Use as ferramentas disponíveis para:
                - Listar tabelas disponíveis
                - Descrever a estrutura das tabelas
                - Encontrar tabelas relevantes
                - Executar consultas SQL
            """,
            expected_output="Um dicionário com os resultados da consulta e a query SQL utilizada.",
            agent=self.query_agent,
        )

    def query_research_task(self, pergunta: str) -> Task:
        """Cria uma task para analisar e interpretar os resultados.
        
        Args:
            pergunta: A pergunta ou instrução para processar.
            
        Returns:
            Task: Task configurada para analisar os resultados.
        """
        return Task(
            description=f"""
                Com base nos resultados obtidos, responda à seguinte pergunta:
                
                "{pergunta}"
                
                Considere:
                1. Os dados obtidos das consultas
                2. O contexto da pergunta original
                3. A relevância dos resultados
                
                Formule uma resposta que:
                - Seja clara e direta
                - Inclua dados específicos quando relevante
                - Explique o raciocínio usado
                - Sugira próximos passos se necessário
            """,
            expected_output="Uma resposta completa e bem estruturada que responde à pergunta original.",
            agent=self.query_research_agent,
        )

    def get_tasks(self, pergunta: str) -> List[Task]:
        """Retorna a lista de tasks necessárias para processar a pergunta.
        
        Args:
            pergunta: A pergunta ou instrução para processar.
            
        Returns:
            List[Task]: Lista de tasks configuradas.
        """
        logger.info(f"Criando tasks para pergunta: {pergunta}")
        return [
            self.query_task(pergunta),
            self.query_research_task(pergunta)
        ]
