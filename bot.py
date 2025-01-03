import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.logger import Logger

# Inicializa o logger
logger = Logger()

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configurações do bot
intents = discord.Intents.all()
intents.message_content = True

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.logger = logger

    async def setup_hook(self):
        """Configurações iniciais do bot"""
        try:
            extension = "cogs.gemini_cog"
            if await self.load_extension(extension):
                self.logger.info(f"Cog {extension} carregado com sucesso!")
            else:
                self.logger.error(f"Falha ao carregar {extension}")
        except Exception as e:
            self.logger.error("Erro ao carregar cog do Gemini", e)

    async def on_ready(self):
        """Evento chamado quando o bot está online"""
        self.logger.info(f"{self.user} está online!")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="suas mensagens"
            )
        )

def main():
    """Função principal"""
    bot = DiscordBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()