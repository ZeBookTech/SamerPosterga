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
            # Carrega o cog diretamente
            from cogs.gemini_cog import GeminiCog
            await self.add_cog(GeminiCog(self))
            self.logger.info("Cog do Gemini carregado com sucesso!")
            
            # Adiciona comando de convite
            @self.command(name="convite")
            async def convite(ctx):
                link = discord.utils.oauth_url(
                    self.user.id,
                    permissions=discord.Permissions(
                        send_messages=True,
                        read_messages=True,
                        read_message_history=True
                    ),
                    scopes=['bot', 'applications.commands']
                )
                await ctx.send(f"🔗 Link para me adicionar: {link}")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar cog do Gemini: {str(e)}")

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