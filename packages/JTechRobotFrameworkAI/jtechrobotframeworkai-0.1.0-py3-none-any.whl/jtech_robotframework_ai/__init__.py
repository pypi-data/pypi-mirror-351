from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

from .vertex import LLMVertex
from .core import AIClient
import asyncio
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import logging
import json
from crewai import Agent, Task, Crew, Process, LLM
from .tool import DatabaseTools

__version__ = '0.1.0'

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JTechRobotFrameworkAI:
    """Uma biblioteca Robot Framework que fornece keywords com recursos de IA para automação de testes.
    
    Esta biblioteca estende a funcionalidade do Robot Framework com keywords
    com recursos de IA usando o Google Generative AI.
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa a biblioteca.
        
        Args:
            api_key: Chave da API do Google AI. Se não fornecida, tentará obter do ambiente.
        """
        self.builtin = BuiltIn()
        self.client = AIClient(api_key)
        load_dotenv()
    
    @keyword
    def enviar_mensagem_para_ia(self, message: str) -> str:
        """Enviar uma mensagem para o modelo da AI e obter resposta.
        
        Args:
            message: A mensagem a ser enviada para o modelo AI.
            
        Returns:
            str: A resposta do modelo AI.
        """
        return self.client.send_message(message)
    
    @keyword
    def enviar_mensagem_para_ia_async(self, message: str) -> str:
        """Enviar uma mensagem para o modelo da AI assincronamente e obter resposta.
        
        Args:
            message: A mensagem a ser enviada para o modelo AI.
            
        Returns:
            str: A resposta do modelo AI.
        """
        return asyncio.run(self.client.send_message_async(message))
    
    @keyword
    def reiniciar_chat_ia(self):
        """Reiniciar a história do chat da AI."""
        self.client.reset_chat()
    
    @keyword
    def obter_historia_chat_ia(self) -> list:
        """Obter a história atual do chat da AI.
        
        Returns:
            list: A história do chat.
        """
        return self.client.get_chat_history()

    @keyword
    def exemplo_keyword(self, argumento1, argumento2):
        """Um exemplo de keyword que demonstra como criar keywords personalizadas.
        
        Args:
            argumento1: Descrição do primeiro argumento
            argumento2: Descrição do segundo argumento
            
        Returns:
            str: Uma string contendo os argumentos combinados
        """
        return f"Received arguments: {argumento1} and {argumento2}"

    @keyword("Usar Agente IA")
    def usar_agente_ia(self, pergunta: str, contexto: Optional[Dict[str, Any]] = None) -> str:
        """Usa o sistema de IA para responder uma pergunta.
        
        Args:
            pergunta: A pergunta ou instrução para o agente.
            contexto: Dicionário opcional com informações adicionais para o agente.
            
        Returns:
            str: Resposta do agente.
            
        Example:
            | ${resposta}= | Usar Agente IA | Qual é a capital da França? |
            | ${resposta}= | Usar Agente IA | Execute uma consulta SQL | ${contexto} |
        """
        try:
            # Adiciona o contexto à pergunta se fornecido
            if contexto:
                pergunta = f"{pergunta}\n\nContexto adicional: {contexto}"
            
            # Usa o cliente AI diretamente
            result = self.client.send_message(pergunta)
            
            return result
            
        except Exception as e:
            error_msg = f"Erro ao usar agente IA: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    @keyword("Consultar PostgreSQL com IA")
    def consultar_postgres_com_ia(self, pergunta: str, connection_string: str) -> str:
        """Consulta o PostgreSQL usando IA para interpretar a pergunta.
        
        Args:
            pergunta: Pergunta em linguagem natural sobre os dados.
            connection_string: String de conexão com o PostgreSQL.
            
        Returns:
            str: Resultado da consulta formatado.
            
        Example:
            | ${resposta}= | Consultar PostgreSQL com IA | Mostre os 5 primeiros registros da tabela usuarios | postgresql://user:pass@localhost:5432/db |
        """
        try:
            # Configura a string de conexão no ambiente
            os.environ["DB_CONNECTION_STRING"] = connection_string
            
            # Criar um prompt específico para consultas SQL
            prompt = f"""
            Você é um especialista em SQL e PostgreSQL. 
            
            Pergunta: {pergunta}
            
            Por favor:
            1. Analise a pergunta e identifique que tipo de consulta SQL seria necessária
            2. Gere uma consulta SQL apropriada (mas não execute)
            3. Explique o que a consulta faria
            4. Forneça sugestões de como melhorar ou otimizar a consulta
            
            Responda de forma clara e educativa.
            """
            
            result = self.client.send_message(prompt)
            
            return result
            
        except Exception as e:
            error_msg = f"Erro ao consultar PostgreSQL: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    @keyword(name="Query Database With AI")
    def query_database_with_ai(self, natural_language_question: str, response_format: str = "dict") -> Dict[str, Any]:
        """
        Uses a CrewAI agent to interpret a natural language question, query a PostgreSQL database,
        and return the answer in the specified format.

        Args:
            natural_language_question (str): The question to ask the database in natural language.
            response_format (str): The desired format for the answer. Can be "text", "json", or "dict".
                                   Defaults to "text". "json" will return a JSON string. "dict" will
                                   return a Python dictionary if the AI's response is valid JSON,
                                   otherwise a dictionary containing the text response.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - "answer" (Union[str, Dict, None]): The answer from the AI, formatted according to
                                                     `response_format`. None if a critical error occurred.
                - "error" (Optional[str]): An error message if an error occurred, otherwise None.
                - "sql_query_attempts" (List[str]): Currently not populated, intended for future SQL logging.
                                                    Verbose CrewAI logs will show SQL queries if `verbose=True`.

        Example:
        | &{db_response}= | Query Database With AI | How many users are registered? | response_format=json |
        | Log | ${db_response}[answer] |
        | Should Be Null | ${db_response}[error] |

        Note:
        - Requires the `DB_CONNECTION_STRING` environment variable to be set for PostgreSQL.
        - Ensure `GOOGLE_API_KEY` is set for the underlying LLM.
        - SQL queries generated and executed by the AI agent will appear in the Robot Framework
          console logs if CrewAI's verbose logging is active (which it is by default in this keyword).
        """
        final_response: Dict[str, Any] = {"answer": None, "error": None, "sql_query_attempts": []}
        logger.info(f"Received natural language question: {natural_language_question}")
        logger.info(f"Requested response format: {response_format}")

        try:
            # a. Get Database Connection String
            db_connection_string = os.getenv("DB_CONNECTION_STRING")
            if not db_connection_string:
                logger.error("DB_CONNECTION_STRING environment variable not set.")
                final_response["error"] = "DB_CONNECTION_STRING environment variable not set."
                return final_response
            logger.info("Using DB_CONNECTION_STRING from environment variable.")
            os.environ['DATABASE_URL'] = db_connection_string # For some Langchain tools

            # b. Initialize PostgreSQL Tools
            logger.info("Initializing PostgreSQL tools...")
            

            # c. Get LLM
            # llm = LLM(
            #     model="gemini/gemini-2.0-flash",
            #     api_key=os.getenv("GOOGLE_API_KEY"),
            #     temperature=0.5,
            # )
            llm = LLMVertex().llm
            
            if not llm:
                logger.error("LLM not available from AIClient. Ensure GOOGLE_API_KEY is set.")
                final_response["error"] = "LLM not available. GOOGLE_API_KEY might be missing or invalid."
                return final_response
            logger.info("LLM obtained successfully from AIClient.")

            # d. Create CrewAI Agent
            logger.info("Creating CrewAI Agent...")
            db_analyst_agent = Agent(
                role="Senior PostgreSQL Database Analyst",
                goal=f"Accurately answer the user's natural language question: '{natural_language_question}'. "
                     f"Use the provided PostgreSQL tools to inspect the database schema and execute queries "
                     f"to find the necessary information. Focus on providing a direct answer to the "
                     f"question based on the data.",
                backstory="You are an expert SQL developer and PostgreSQL database analyst. You are skilled "
                          "at understanding natural language questions, translating them into effective SQL "
                          "queries, and interpreting the results. You have a suite of tools to explore the "
                          "database (list tables, describe tables, find tables) and execute SQL queries. "
                          "You must use these tools to answer the question. Your final response should be "
                          "factual and derived directly from the database information.",
                tools=DatabaseTools.get_tools(),
                llm=llm,
                verbose=True,
                allow_delegation=False,
                memory=False
            )
            logger.info("CrewAI Agent created.")

            # e. Create CrewAI Task
            logger.info("Creating CrewAI Task...")
            query_task = Task(
                description=f"Answer the natural language question: '{natural_language_question}'. "
                            "Follow these steps: "
                            "1. Understand the question thoroughly. "
                            "2. If necessary, use the PostgreSQLListTablesTool or PostgreSQLFindTableTool to identify relevant tables. "
                            "3. If table structures are unknown, use PostgreSQLDescribeTableTool to understand pertinent table schemas. "
                            "4. Construct an SQL query using PostgreSQLQueryTool to extract the information needed to answer the question. "
                            "5. Execute the query using PostgreSQLQueryTool. "
                            "6. Based on the query result, formulate a concise and direct answer to the original question: '{natural_language_question}'. "
                            "Ensure the final output is only the answer to the question.",
                agent=db_analyst_agent,
                expected_output="A clear, concise, and factual answer to the user's question, derived from the PostgreSQL database. "
                                "For example, if the question is 'How many users are there?', the output should be something like 'There are 748 users.'."
            )
            logger.info("CrewAI Task created.")

            # f. Create and Execute Crew
            logger.info("Creating and kicking off Crew...")
            database_crew = Crew(agents=[db_analyst_agent], tasks=[query_task], verbose=True, process=Process.sequential)
            crew_result = database_crew.kickoff()
            print(f"==========================================================================")
            print(f">>>>> CrewAI raw result: {crew_result}")
            print(f"==========================================================================")
            logger.info(f"CrewAI raw result: {crew_result}")

            # Extrair resposta textual do CrewAI
            raw_answer = None
            # Tenta acessar atributos comuns de resposta
            for attr in ["result", "final_output", "output", "answer"]:
                if hasattr(crew_result, attr):
                    raw_answer = getattr(crew_result, attr)
                    break
            if raw_answer is None:
                # Fallback: usar str(crew_result)
                raw_answer = str(crew_result)

            # g. Format Response
            logger.info(f"Formatting response for type: {response_format}")
            if response_format == "json":
                try:
                    # Garante que SEMPRE será string JSON, nunca dict Python
                    if isinstance(raw_answer, str):
                        try:
                            parsed_result = json.loads(raw_answer)
                            # Se já é JSON válido, reserializa para garantir string
                            final_response["answer"] = json.dumps(parsed_result, indent=2)
                        except json.JSONDecodeError:
                            logger.warning("CrewAI result is a string but not valid JSON. Wrapping as text in JSON.")
                            final_response["answer"] = json.dumps({"text_response": raw_answer}, indent=2)
                    elif isinstance(raw_answer, (dict, list)):
                        # Sempre serializa para string JSON
                        final_response["answer"] = json.dumps(raw_answer, indent=2)
                    else: # Outros tipos
                        logger.warning(f"CrewAI result is of type {type(raw_answer)}, not string/dict/list. Converting to string and wrapping in JSON.")
                        final_response["answer"] = json.dumps({"text_response": str(raw_answer)}, indent=2)
                    # Garante que nunca será dict Python
                    if not isinstance(final_response["answer"], str):
                        final_response["answer"] = json.dumps(final_response["answer"], indent=2)
                    # Força para string (proteção extra para Robot Framework)
                    final_response["answer"] = str(final_response["answer"])
                except Exception as fmt_e:
                    logger.error(f"Could not format answer to JSON: {fmt_e}. Returning error JSON.", exc_info=True)
                    final_response["answer"] = json.dumps({"error": "Failed to format as JSON", "original_response": str(raw_answer)})
                    final_response["answer"] = str(final_response["answer"])
            elif response_format == "dict":
                try:
                    # Sempre retorna string, nunca dict aninhado
                    if isinstance(raw_answer, str):
                        try:
                            parsed = json.loads(raw_answer)
                            if isinstance(parsed, dict) and "text_response" in parsed:
                                final_response["answer"] = parsed["text_response"]
                            else:
                                final_response["answer"] = raw_answer
                        except json.JSONDecodeError:
                            final_response["answer"] = raw_answer
                    elif isinstance(raw_answer, dict):
                        # Se vier dict, pega o campo text_response se existir
                        if "text_response" in raw_answer:
                            final_response["answer"] = raw_answer["text_response"]
                        else:
                            final_response["answer"] = str(raw_answer)
                    else:
                        final_response["answer"] = str(raw_answer)
                except Exception as fmt_e:
                    logger.error(f"Could not format answer to dict: {fmt_e}. Returning raw text in dict with error.", exc_info=True)
                    final_response["answer"] = str(raw_answer)
            else: # "text" ou qualquer outro caso
                final_response["answer"] = str(raw_answer)

        except Exception as e:
            logger.error(f"Error in Query Database With AI keyword: {e}", exc_info=True)
            # Garante que o campo answer seja string JSON de erro se response_format=json
            if response_format == "json":
                final_response["answer"] = json.dumps({"error": str(e)})
            else:
                final_response["answer"] = ""
            final_response["error"] = str(e)

        if final_response["answer"] is None:
            final_response["answer"] = ""
        # Garante que answer é sempre string para o Robot Framework
        if not isinstance(final_response["answer"], str):
            final_response["answer"] = json.dumps(final_response["answer"], indent=2)
        return final_response


# Exporta a classe principal
__all__ = ['JTechRobotFrameworkAI']

# Cria uma instância da biblioteca para o Robot Framework
class RobotFrameworkLibrary(JTechRobotFrameworkAI):
    """Classe que expõe as keywords para o Robot Framework."""
    pass



