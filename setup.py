import os
import sys
import subprocess
import logging
from datetime import datetime

# Configuração de logging
log_filename = f"setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename, mode="w", encoding="utf-8")
    ]
)

class BotSetup:
    def __init__(self):
        self.directories = ['cogs', 'utils', 'logs']
        self.files_created = []
    
    def create_directory_structure(self):
        """Cria a estrutura de diretórios do projeto"""
        try:
            for directory in self.directories:
                os.makedirs(directory, exist_ok=True)
                init_file = os.path.join(directory, '__init__.py')
                if not os.path.exists(init_file):
                    with open(init_file, 'w', encoding='utf-8') as f:
                        pass
                    self.files_created.append(init_file)
            logging.info("✓ Estrutura de diretórios criada com sucesso")
        except Exception as e:
            logging.error(f"✗ Erro ao criar diretórios: {e}")
            raise

    def create_bot_file(self):
        """Cria o arquivo principal bot.py"""
        content = '''import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("logs", "bot.log"), 
                          mode="a", 
                          encoding="utf-8")
    ]
)

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.messages = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            description="Bot Discord com Gemini AI"
        )
    
    async def setup_hook(self):
        """Configurações iniciais do bot"""
        await self.load_cogs()
    
    async def load_cogs(self):
        """Carrega todas as extensões/cogs"""
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    logging.info(f"Cog carregado: {filename}")
                except Exception as e:
                    logging.error(f"Erro ao carregar cog {filename}: {e}")

    async def on_ready(self):
        """Evento chamado quando o bot está pronto"""
        logging.info(f"{self.user} está online!")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="!help para comandos"
            )
        )

async def main():
    """Função principal assíncrona"""
    bot = DiscordBot()
    
    @bot.command(name="test")
    async def test(ctx):
        """Teste simples para verificar se o bot está funcionando"""
        await ctx.send("✓ Bot está funcionando!")
    
    try:
        await bot.start(TOKEN)
    except Exception as e:
        logging.error(f"Erro ao iniciar o bot: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''
        try:
            with open('bot.py', 'w', encoding='utf-8') as f:
                f.write(content)
            self.files_created.append('bot.py')
            logging.info("✓ Arquivo bot.py criado com sucesso")
        except Exception as e:
            logging.error(f"✗ Erro ao criar bot.py: {e}")
            raise

    def create_gemini_cog(self):
        """Cria o arquivo gemini_cog.py"""
        content = '''import discord
from discord.ext import commands
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
from typing import Optional

load_dotenv()

class GeminiCog(commands.Cog, name="Comandos Gemini"):
    """Comandos de IA usando Google Gemini"""
    
    def __init__(self, bot):
        self.bot = bot
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            logging.error("GOOGLE_API_KEY não encontrada no arquivo .env")
            raise ValueError("GOOGLE_API_KEY não configurada")
            
        # Configura o Gemini
        genai.configure(api_key=api_key)
        # Inicializa o modelo
        self.model = genai.GenerativeModel('gemini-pro')
        # Dicionário para armazenar chats ativos
        self.chats = {}

    @commands.command(
        name="chat",
        description="Conversa com o Gemini AI",
        brief="Inicia uma conversa com IA"
    )
    async def chat(self, ctx, *, message: str):
        """
        Conversa com o Gemini AI
        
        Argumentos:
            message (str): Mensagem para enviar ao Gemini
        """
        try:
            # Cria ou obtém um chat para o usuário
            if ctx.author.id not in self.chats:
                self.chats[ctx.author.id] = self.model.start_chat(
                    history=[],
                    generation_config={
                        'temperature': 0.7,
                        'max_output_tokens': 800,
                    }
                )

            chat = self.chats[ctx.author.id]
            
            async with ctx.typing():
                response = chat.send_message(message)
                response_text = response.text
                
                # Divide a resposta se for muito longa
                if len(response_text) > 1900:
                    parts = [response_text[i:i+1900] for i in range(0, len(response_text), 1900)]
                    for part in parts:
                        await ctx.send(f"🤖 {part}")
                else:
                    await ctx.send(f"🤖 {response_text}")

        except Exception as e:
            error_msg = f"❌ Erro ao processar sua mensagem: {str(e)}"
            await ctx.send(error_msg)
            logging.error(f"Erro no comando chat: {e}")

    @commands.command(
        name="limpar",
        description="Limpa o histórico de conversa",
        brief="Limpa histórico do chat"
    )
    async def clear_chat(self, ctx):
        """Limpa o histórico de conversa do usuário"""
        if ctx.author.id in self.chats:
            self.chats[ctx.author.id] = self.model.start_chat(
                history=[],
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 800,
                }
            )
            await ctx.send("✨ Histórico de conversa limpo!")
        else:
            await ctx.send("📝 Você ainda não tem um histórico de conversa.")

    @commands.command(
        name="config",
        description="Configura parâmetros do chat",
        brief="Configura parâmetros"
    )
    async def configure(
        self, 
        ctx, 
        temperatura: Optional[float] = None, 
        tokens: Optional[int] = None
    ):
        """
        Configura os parâmetros do chat
        
        Argumentos:
            temperatura (float): Valor entre 0 e 1 (opcional)
            tokens (int): Valor entre 1 e 2048 (opcional)
        """
        if temperatura is not None and not 0 <= temperatura <= 1:
            await ctx.send("❌ Temperatura deve estar entre 0 e 1!")
            return
            
        if tokens is not None and not 1 <= tokens <= 2048:
            await ctx.send("❌ Número de tokens deve estar entre 1 e 2048!")
            return
            
        if ctx.author.id not in self.chats:
            self.chats[ctx.author.id] = self.model.start_chat(history=[])
            
        config = {
            'temperature': temperatura if temperatura is not None else 0.7,
            'max_output_tokens': tokens if tokens is not None else 800,
        }
        
        self.chats[ctx.author.id] = self.model.start_chat(
            history=self.chats[ctx.author.id].history,
            generation_config=config
        )
        
        await ctx.send(
            f"✅ Configurações atualizadas:\n"
            f"📊 Temperatura: {config['temperature']}\n"
            f"🔢 Máx. Tokens: {config['max_output_tokens']}"
        )

async def setup(bot):
    """Função de setup do cog"""
    await bot.add_cog(GeminiCog(bot))
'''
        cog_path = os.path.join('cogs', 'gemini_cog.py')
        try:
            with open(cog_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.files_created.append(cog_path)
            logging.info("✓ Arquivo gemini_cog.py criado com sucesso")
        except Exception as e:
            logging.error(f"✗ Erro ao criar gemini_cog.py: {e}")
            raise

    def create_env_file(self):
        """Cria o arquivo .env"""
        content = '''# Token do seu bot Discord
DISCORD_TOKEN=seu_token_aqui

# Chave API do Google (para Gemini)
GOOGLE_API_KEY=seu_google_api_key_aqui
'''
        try:
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(content)
            self.files_created.append('.env')
            logging.info("✓ Arquivo .env criado com sucesso")
        except Exception as e:
            logging.error(f"✗ Erro ao criar .env: {e}")
            raise

    def create_requirements(self):
        """Cria o arquivo requirements.txt"""
        content = '''# Dependências principais
discord.py>=2.3.2
python-dotenv>=1.0.0
google-generativeai>=0.3.0

# Dependências opcionais
aiohttp>=3.8.0
'''
        try:
            with open('requirements.txt', 'w', encoding='utf-8') as f:
                f.write(content)
            self.files_created.append('requirements.txt')
            logging.info("✓ Arquivo requirements.txt criado com sucesso")
        except Exception as e:
            logging.error(f"✗ Erro ao criar requirements.txt: {e}")
            raise

    def install_dependencies(self):
        """Instala as dependências do projeto"""
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            logging.info("✓ Dependências instaladas com sucesso")
        except subprocess.CalledProcessError as e:
            logging.error(f"✗ Erro ao instalar dependências: {e}")
            raise

    def setup(self):
        """Executa todas as etapas da configuração"""
        try:
            self.create_directory_structure()
            self.create_bot_file()
            self.create_gemini_cog()
            self.create_env_file()
            self.create_requirements()
            self.install_dependencies()
            
            # Exibe resumo da instalação
            print("\n✨ Configuração concluída com sucesso!")
            print("\n📁 Arquivos criados:")
            for file in self.files_created:
                print(f"  ✓ {file}")
            
            print("\n📋 Próximos passos:")
            print("1. Configure suas chaves no arquivo .env:")
            print("   - DISCORD_TOKEN")
            print("   - GOOGLE_API_KEY")
            print("\n2. Execute o bot:")
            print("   python bot.py")
            
            print("\n🤖 Comandos disponíveis:")
            print("!test    - Testa se o bot está funcionando")
            print("!chat    - Conversa com o Gemini AI")
            print("!limpar  - Limpa o histórico de conversa")
            print("!config  - Configura parâmetros do chat")
            
        except Exception as e:
            logging.error(f"✗ Erro durante a configuração: {e}")
            raise

if __name__ == "__main__":
    setup = BotSetup()
    setup.setup()