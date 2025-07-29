from jtech_robotframework_ai.agent import JTechRobotFrameworkAIAgent
from jtech_robotframework_ai.task import JTechRobotFrameworkAITask
from crewai import Crew
import logging

logger = logging.getLogger(__name__)

class JTechRobotFrameworkAICrew:
    def __init__(self):
        self.agents = JTechRobotFrameworkAIAgent().get_agents()
        
    def get_crew(self, pergunta: str) -> Crew:
        """Cria uma nova instância do Crew com as tasks atualizadas para a pergunta.
        
        Args:
            pergunta: A pergunta ou instrução para processar.
            
        Returns:
            Crew: Instância do Crew configurada com as tasks.
        """
        # Cria uma nova instância de tasks com a pergunta atual
        tasks = JTechRobotFrameworkAITask().get_tasks(pergunta)
        
        return Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=True,
        )
        
    def execute_crew(self, pergunta: str) -> str:
        """Executa o Crew com a pergunta fornecida.
        
        Args:
            pergunta: A pergunta ou instrução para processar.
            
        Returns:
            str: Resultado do processamento da pergunta.
        """
        try:
            logger.info(f"Executando Crew com pergunta: {pergunta}")
            
            # Cria uma nova instância do Crew com as tasks atualizadas
            crew = self.get_crew(pergunta)
            
            # Executa o Crew
            result = crew.kickoff()
            
            logger.info(f"Resultado do Crew: {result}")
            return result
            
        except Exception as e:
            error_msg = f"Erro ao executar Crew: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)