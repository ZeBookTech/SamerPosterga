# bot.py

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.logger import Logger
from typing import List

load_dotenv()

# Inicializa o logger
logger = Logger()

# Carrega variáveis de ambiente
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    logger.error("DISCORD_TOKEN não encontrada no .env")
    raise ValueError("DISCORD_TOKEN não encontrada no .env")

# Configurações do bot com os intents necessários
intents = discord.Intents.default()
intents.message_content = True  # Necessário para ler o conteúdo das mensagens
intents.guilds = True
intents.members = True  # Necessário se você planeja acessar informações de membros

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.logger = logger

    async def setup_hook(self):
        """Configurações iniciais do bot."""
        try:
            # Carrega todos os cogs da pasta 'cogs', exceto '__init__.py'
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py') and filename != '__init__.py':
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    self.logger.info(f"Cog {filename} carregado com sucesso!")
            
            # Adiciona um comando de ajuda personalizado
            @self.command(name="ajuda")
            async def ajuda(ctx: commands.Context):
                """Exibe a lista de comandos disponíveis."""
                help_text = (
                    "**Comandos Disponíveis:**\n"
                    "`!ajuda` - Exibe esta mensagem de ajuda.\n"
                    "`!config [temperatura] [top_p] [top_k] [max_tokens]` - Configura os parâmetros do modelo (administradores).\n"
                    "`!logs [linhas]` - Mostra as últimas linhas do log (administradores).\n"
                    "`!convite` - Gera um link de convite para adicionar o bot a outros servidores.\n"
                    "`!imagem <prompt>` - Gera uma imagem com base no prompt fornecido."
                )
                await ctx.send(help_text)
                self.logger.info(f"Comando de ajuda utilizado por {ctx.author}")
            
            self.logger.info("Todos os cogs foram carregados com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar cogs: {str(e)}", exc_info=True)

    async def on_ready(self):
        """Evento chamado quando o bot está online."""
        self.logger.info(f"{self.user} está online e conectado em {len(self.guilds)} servidores!")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="suas mensagens"
            )
        )

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Tratamento de erros de comandos."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão para executar este comando.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argumento inválido fornecido.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Comando não encontrado. Use `!ajuda` para ver os comandos disponíveis.")
        else:
            self.logger.error(f"Erro no comando {ctx.command}: {error}", exc_info=True)
            await ctx.send("❌ Ocorreu um erro ao executar o comando.")

def main():
    """Função principal para iniciar o bot."""
    bot = DiscordBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
