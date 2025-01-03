import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

class Logger:
    def __init__(self, name='BotLogger'):
        # Cria o diretório de logs se não existir
        self.logs_dir = 'logs'
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        # Nome do arquivo de log com data
        self.log_filename = os.path.join(
            self.logs_dir, 
            'bot.log'  # Arquivo fixo para facilitar o acesso
        )

        # Configura o logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Remove handlers existentes para evitar duplicação
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Configuração do formato do log
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para arquivo com rotação
        file_handler = RotatingFileHandler(
            self.log_filename,
            maxBytes=5*1024*1024,  # 5MB por arquivo
            backupCount=5,  # Mantém 5 arquivos de backup
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        # Adiciona os handlers ao logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        """Registra mensagem de informação"""
        self.logger.info(message)

    def error(self, message, error=None):
        """Registra erro com detalhes da exceção"""
        if error:
            self.logger.error(f"{message} | Erro: {str(error)}")
        else:
            self.logger.error(message)

    def warning(self, message):
        """Registra mensagem de aviso"""
        self.logger.warning(message)

    def debug(self, message):
        """Registra mensagem de debug"""
        self.logger.debug(message)

    def get_latest_logs(self, lines=10):
        """Retorna as últimas linhas do log atual"""
        try:
            with open(self.log_filename, 'r', encoding='utf-8') as file:
                # Lê todas as linhas e pega as últimas 'lines' linhas
                all_lines = file.readlines()
                return all_lines[-lines:]
        except Exception as e:
            return [f"Erro ao ler logs: {str(e)}"]