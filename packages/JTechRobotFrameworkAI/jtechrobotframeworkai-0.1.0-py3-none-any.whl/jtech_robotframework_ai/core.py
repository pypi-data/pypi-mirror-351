import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from tenacity import retry, stop_after_attempt, wait_exponential

class AIClient:
    """Cliente para interação com modelos de IA usando Google Generative AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa o cliente AI.
        
        Args:
            api_key: Chave da API do Google AI. Se não fornecida, tentará obter do ambiente.
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            # Não levanta erro imediatamente, apenas avisa
            self.api_key = None
            self.llm = None
            self.chain = None
        else:
            self._initialize_llm()
        
        self.chat_history = []
    
    def _initialize_llm(self):
        """Inicializa o modelo LLM e a chain."""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=self.api_key,
                temperature=0.7,
                convert_system_message_to_human=True
            )
            
            # Criar uma chain simples para prompts
            prompt = PromptTemplate(
                input_variables=["message"],
                template="{message}"
            )
            
            self.chain = LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=False
            )
        except Exception as e:
            raise ValueError(f"Erro ao inicializar modelo: {str(e)}")
    
    def _ensure_initialized(self):
        """Garante que o cliente está inicializado antes de usar."""
        if not self.api_key:
            # Tenta obter a chave do ambiente novamente
            self.api_key = os.getenv('GOOGLE_API_KEY')
            if not self.api_key:
                raise ValueError("Chave da API do Google é necessária. Configure via variável de ambiente GOOGLE_API_KEY.")
            self._initialize_llm()
    
    def send_message(self, message: str) -> str:
        """Envia uma mensagem para o modelo AI.
        
        Args:
            message: A mensagem a ser enviada.
            
        Returns:
            str: A resposta do modelo.
        """
        self._ensure_initialized()
        
        try:
            response = self.chain.run(message=message)
            self.add_to_chat_history({"role": "user", "content": message})
            self.add_to_chat_history({"role": "assistant", "content": response})
            return response
        except Exception as e:
            raise Exception(f"Erro ao enviar mensagem: {str(e)}")
    
    async def send_message_async(self, message: str) -> str:
        """Envia uma mensagem para o modelo AI de forma assíncrona.
        
        Args:
            message: A mensagem a ser enviada.
            
        Returns:
            str: A resposta do modelo.
        """
        self._ensure_initialized()
        
        try:
            response = await self.chain.arun(message=message)
            self.add_to_chat_history({"role": "user", "content": message})
            self.add_to_chat_history({"role": "assistant", "content": response})
            return response
        except Exception as e:
            raise Exception(f"Erro ao enviar mensagem assíncrona: {str(e)}")
    
    def add_to_chat_history(self, message: dict):
        """Adiciona uma mensagem ao histórico do chat.
        
        Args:
            message: Dicionário com 'role' e 'content'.
        """
        self.chat_history.append(message)
    
    def get_chat_history(self) -> list:
        """Obtém o histórico do chat.
        
        Returns:
            list: Lista com o histórico do chat.
        """
        return self.chat_history
    
    def reset_chat(self):
        """Reinicia o histórico do chat."""
        self.chat_history = []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def send_message_retry(self, message: str) -> str:
        """Envia uma mensagem para o modelo AI e obtém a resposta.
        
        Args:
            message: A mensagem a ser enviada para o modelo AI.
            
        Returns:
            str: A resposta do modelo AI.
            
        Raises:
            Exception: Se houver erro na comunicação com a API.
        """
        try:
            # Executa a chain com a pergunta
            response = self.chain.run(
                pergunta=message
            )
            
            # Atualiza o histórico
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "assistant", "content": response})
            
            return response
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para AI: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def send_message_async_retry(self, message: str) -> str:
        """Envia uma mensagem para o modelo AI de forma assíncrona e obtém a resposta.
        
        Args:
            message: A mensagem a ser enviada para o modelo AI.
            
        Returns:
            str: A resposta do modelo AI.
            
        Raises:
            Exception: Se houver erro na comunicação com a API.
        """
        try:
            # Executa a chain de forma assíncrona
            response = await self.chain.arun(
                pergunta=message
            )
            
            # Atualiza o histórico
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "assistant", "content": response})
            
            return response
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem assíncrona para AI: {str(e)}")
            raise 