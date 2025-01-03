# utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
from typing import List

class Logger:
    """Configuração personalizada de logging."""

    def __init__(self, name: str = 'DiscordBot', log_file: str = 'bot.log'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Evita adicionar múltiplos handlers caso o logger seja instanciado várias vezes
        if not self.logger.handlers:
            # Formato do log
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # Handler para escrever em arquivo com rotação
            file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            
            # Handler para exibir no console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            
            # Adiciona os handlers ao logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        self.logger.error(message, exc_info=exc_info)
    
    def get_latest_logs(self, lines: int = 10) -> List[str]:
        """Retorna as últimas linhas do arquivo de log."""
        try:
            with open('bot.log', 'r', encoding='utf-8') as f:
                return f.readlines()[-lines:]
        except FileNotFoundError:
            return ["Arquivo de log não encontrado."]
