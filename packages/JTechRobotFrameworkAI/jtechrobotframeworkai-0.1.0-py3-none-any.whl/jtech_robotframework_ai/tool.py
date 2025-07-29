"""
Tools para interação com banco de dados PostgreSQL usando CrewAI.
"""
import os
from typing import List, Dict, Any, Optional, Union, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from crewai.tools import BaseTool

class PostgreSQLQueryTool(BaseTool):
    """Tool para executar consultas SQL."""
    
    name: str = "executar_consulta"
    description: str = "Executa uma consulta SQL no banco de dados PostgreSQL"
    
    # Permite conexão por dicionário OU por URL
    connection_params: Dict[str, str] = {
        'host': os.getenv("DB_HOST", "localhost"),
        'port': os.getenv("DB_PORT", "5432"),
        'dbname': os.getenv("DB_NAME", "postgres"),
        'user': os.getenv("DB_USER", "postgres"),
        'password': os.getenv("DB_PASSWORD", "")
    }

    def _get_connection(self):
        connection_url = os.getenv("DB_CONNECTION_STRING")
        if connection_url:
            return psycopg2.connect(connection_url, cursor_factory=RealDictCursor)
        else:
            return psycopg2.connect(**self.connection_params, cursor_factory=RealDictCursor)

    def _execute(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def _run(self, query: str, params: Optional[Union[Tuple, List, Dict, None]] = None) -> str:
        """
        Executa a consulta e retorna os resultados formatados.
        
        Args:
            query: Query SQL a ser executada
            params: Parâmetros para a query (opcional). Pode ser uma tupla, lista ou None.
            
        Returns:
            str: Resultados formatados como string
        """
        try:
            # Converter params para tupla se não for None
            params_tuple = None
            if params is not None:
                if isinstance(params, tuple):
                    params_tuple = params
                elif isinstance(params, list):
                    params_tuple = tuple(params)
                elif isinstance(params, dict):
                    # Se for um dicionário, assumimos que é vazio e não usamos parâmetros
                    params_tuple = None
                else:
                    params_tuple = (params,)
                    
            results = self._execute(query, params_tuple)
            return str(results)
        except Exception as e:
            return f"Erro ao executar consulta: {str(e)}"

class ListTablesTool(BaseTool):
    """Tool para listar tabelas do banco."""
    
    name: str = "listar_tabelas"
    description: str = "Lista todas as tabelas do banco de dados"

    def _run(self) -> str:
        """Lista todas as tabelas do schema public."""
        query_tool = PostgreSQLQueryTool()
        results = query_tool._execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        return str([r['table_name'] for r in results])

class DescribeTableTool(BaseTool):
    """Tool para descrever estrutura de tabelas."""
    
    name: str = "descrever_tabela"
    description: str = "Retorna a estrutura de uma tabela específica"

    def _run(self, table: str) -> str:
        """
        Descreve a estrutura de uma tabela.
        
        Args:
            table: Nome da tabela
            
        Returns:
            str: Estrutura da tabela formatada
        """
        query_tool = PostgreSQLQueryTool()
        results = query_tool._execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            AND table_schema = 'public'
        """, (table,))
        return str(results)


class DatabaseTools:
    """Classe para agrupar as ferramentas de banco de dados."""
    
    @staticmethod
    def get_tools() -> List[BaseTool]:
        """Retorna todas as tools disponíveis."""
        return [
            PostgreSQLQueryTool(),
            ListTablesTool(),
            DescribeTableTool(),
        ]

def get_tools() -> List[BaseTool]:
    """Retorna todas as tools disponíveis."""
    return [
        PostgreSQLQueryTool(),
        ListTablesTool(),
        DescribeTableTool(),
    ]
