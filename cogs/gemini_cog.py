# cogs/gemini_cog.py

import discord
from discord.ext import commands
import google.generativeai as genai
import os
from dotenv import load_dotenv
from utils.logger import Logger
from typing import Optional, List
from huggingface_hub import InferenceClient
import asyncio
from io import BytesIO

load_dotenv()

class GeminiCog(commands.Cog, name="Comandos Gemini"):
    """Comandos de IA usando Google Gemini e HuggingFace para suporte jurídico e geração de imagens."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = Logger('GeminiCog')
        
        # Validação das variáveis de ambiente
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            self.logger.error("GOOGLE_API_KEY não encontrada no .env")
            raise ValueError("GOOGLE_API_KEY não encontrada")
        
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        if not self.hf_token:
            self.logger.error("HUGGINGFACE_TOKEN não encontrada no .env")
            raise ValueError("HUGGINGFACE_TOKEN não encontrada")
        
        # Configuração do Google Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chats = {}
        
        # Configuração inicial do modelo
        self.generation_config = {
            "temperature": 0.9,
            "top_p": 1.0,
            "top_k": 32,
            "max_output_tokens": 4096,
        }
        
        self.logger.info("GeminiCog inicializado com sucesso")

        # Configuração do HuggingFace InferenceClient
        self.hf_client = InferenceClient("prashanth970/flux-lora-uncensored", token=self.hf_token)
        self.logger.info("HuggingFace InferenceClient configurado com sucesso")

        # Prompt do sistema com exemplos
        self.system_prompt = """
        <identity>
            Você é Samélio, um ex-juiz aposentado que ajuda estudantes a se prepararem para concursos públicos, com conhecimento abrangente em diversas áreas do Direito.
        </identity>
        <context>
            Você fornece respostas precisas e verificadas sobre tópicos jurídicos, utilizando documentos disponíveis, recursos online e APIs. Seu objetivo é ajudar os estudantes a entender conceitos complexos de forma simples e acessível.
        </context>
        <task>
            Responda a perguntas sobre Direito com base em seu conhecimento e nos documentos disponíveis. Forneça explicações claras e concisas, evitando especulações e mantendo um tom amigável.
        </task>
        <constraints>
            - Fale apenas sobre tópicos que você conhece.
            - Evite respostas genéricas ou não verificadas.
            - Respeite a privacidade e a confidencialidade das informações.
            - Utilize algoritmos de verificação de precisão para garantir a exatidão das respostas.
        </constraints>
        <examples>
            <example>
                <input>
                    O que é o princípio da legalidade no Direito Penal?
                </input>
                <output>
                    O princípio da legalidade, previsto no artigo 5º, inciso XXXIX da Constituição Federal, estabelece que não há crime nem pena sem uma lei anterior que os defina. Isso significa que uma conduta só pode ser considerada criminosa se houver uma legislação que a tipifique como tal, garantindo assim a segurança jurídica e a proteção dos direitos individuais.
                </output>
            </example>
            <example>
                <input>
                    Quais são os requisitos para a validade de um contrato?
                </input>
                <output>
                    Para que um contrato seja considerado válido, ele deve atender aos seguintes requisitos: 
                    1. Capacidade das partes: ambas devem ser capazes de contratar, ou seja, ter a idade e a sanidade mental necessárias.
                    2. Objeto lícito: o objeto do contrato deve ser lícito, possível e determinado ou determinável.
                    3. Forma prescrita ou não defesa em lei: alguns contratos exigem uma forma específica (escrito, por exemplo), enquanto outros podem ser feitos de forma verbal.
                    4. Consentimento: as partes devem consentir livremente, sem vícios como coação, dolo ou erro.
                </output>
            </example>
        </examples>
        """

    def get_channel_name(self, channel: discord.abc.GuildChannel) -> str:
        """Retorna o nome do canal de forma segura."""
        if isinstance(channel, discord.DMChannel):
            return "Mensagem Direta"
        elif isinstance(channel, discord.GroupChannel):
            return "Grupo Privado"
        elif isinstance(channel, discord.Thread):
            return f"Thread: {channel.name}"
        else:
            return f"#{channel.name}"

    async def get_gemini_response(self, message_content: str, user_id: int) -> str:
        """Obtém resposta do Gemini com base nas instruções personalizadas e tratamento de erros."""
        try:
            self.logger.info(f"Processando mensagem do usuário {user_id}")
            
            # Monta o prompt completo
            full_prompt = f"{self.system_prompt}\n\nUsuário: {message_content}\nAssistente:"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config,
                stream=False
            )
            
            if response and response.text:
                self.logger.info(f"Resposta gerada com sucesso para usuário {user_id}")
                return response.text.strip()
                
            self.logger.warning(f"Resposta vazia gerada para usuário {user_id}")
            return "Desculpe, não consegui gerar uma resposta. Pode reformular sua pergunta?"
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta para usuário {user_id}: {e}", exc_info=True)
            return "Desculpe, ocorreu um erro. Por favor, tente novamente."

    async def generate_image(self, prompt: str) -> Optional[discord.File]:
        """
        Gera uma imagem usando o HuggingFace e retorna como um discord.File.
        Retorna None se ocorrer um erro.
        """
        try:
            self.logger.info(f"Iniciando geração de imagem para prompt: {prompt}")
            # Chamada síncrona, então executa em um executor para não bloquear o event loop
            image = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.hf_client.text_to_image(prompt)
            )
            
            if image:
                # Salva a imagem em BytesIO
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                
                discord_file = discord.File(fp=img_byte_arr, filename='image.png')
                self.logger.info("Imagem gerada com sucesso")
                return discord_file
            else:
                self.logger.warning("Imagem gerada está vazia")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar imagem: {e}", exc_info=True)
            return None

    def should_respond(self, message: discord.Message) -> bool:
        """Verifica se o bot deve responder à mensagem."""
        # Ignora mensagens de bots
        if message.author.bot:
            return False

        # Obtém o conteúdo limpo da mensagem
        content = message.content.strip().lower()
        
        # Verifica menção direta ao bot
        is_mentioned = self.bot.user in message.mentions
        
        # Lista de possíveis ativações (nomes e sinônimos)
        activation_phrases = ['samer', f'<@{self.bot.user.id}>', f'<@!{self.bot.user.id}>']
        
        # Verifica se começa com alguma das frases de ativação
        starts_with_activation = any(content.startswith(phrase + ' ') or 
                                     content.startswith(phrase + ',') or 
                                     content.startswith(phrase + ':') or 
                                     content.startswith(phrase + '?') or 
                                     content.startswith(phrase + '!') 
                                     for phrase in activation_phrases)
        
        # Verifica se é uma resposta a uma mensagem do bot
        is_reply_to_bot = (
            message.reference and 
            isinstance(message.reference.resolved, discord.Message) and 
            message.reference.resolved.author.id == self.bot.user.id
        )
        
        # Só responde se for mencionado ou chamado pelo nome
        should_respond = is_mentioned or starts_with_activation or is_reply_to_bot
        
        # Loga a decisão para debug
        if should_respond:
            self.logger.debug(
                f"Respondendo mensagem | "
                f"Autor: {message.author} | "
                f"Conteúdo: {content} | "
                f"Mencionado: {is_mentioned} | "
                f"Ativado por frase: {starts_with_activation} | "
                f"Resposta a bot: {is_reply_to_bot}"
            )
        
        return should_respond

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Responde apenas quando explicitamente chamado."""
        if not self.should_respond(message):
            return

        try:
            # Remove menções e nome do bot
            content = message.content
            
            # Remove menções ao bot
            for mention in message.mentions:
                if mention.id == self.bot.user.id:
                    content = content.replace(str(mention), '').strip()
            
            # Remove "samer" do início se presente
            content_lower = content.lower()
            for phrase in ['samer', f'<@{self.bot.user.id}>', f'<@!{self.bot.user.id}>']:
                if content_lower.startswith(phrase):
                    parts = content.split(None, 1)
                    if len(parts) > 1:
                        content = parts[1].strip()
                    else:
                        content = ''
                    break
            
            # Se não sobrou conteúdo após limpeza, não responde
            if not content:
                return
                
            channel_name = self.get_channel_name(message.channel)
            
            self.logger.info(
                f"Mensagem recebida | Canal: {channel_name} | "
                f"Usuário: {message.author} | ID: {message.author.id}"
            )
            
            async with message.channel.typing():
                # Verifica se o usuário deseja gerar uma imagem
                if content.startswith("imagem ") or content.startswith("image "):
                    # Extrai o prompt para a imagem
                    prompt = content[len("imagem "):].strip() or content[len("image "):].strip()
                    if not prompt:
                        await message.reply("❌ Por favor, forneça um prompt para gerar a imagem. Exemplo: `imagem Astronauta montando um cavalo`")
                        return
                    
                    discord_file = await self.generate_image(prompt)
                    if discord_file:
                        await message.reply(file=discord_file)
                        self.logger.info("Imagem enviada com sucesso")
                    else:
                        await message.reply("❌ Não foi possível gerar a imagem no momento. Por favor, tente novamente mais tarde.")
                else:
                    # Processa como uma pergunta de texto normal
                    response = await self.get_gemini_response(
                        content,
                        message.author.id
                    )
                    
                    if len(response) > 1900:
                        chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                        for i, chunk in enumerate(chunks, 1):
                            await message.reply(chunk)
                            self.logger.info(f"Enviada parte {i}/{len(chunks)} da resposta")
                    else:
                        await message.reply(response)
                        self.logger.info("Resposta enviada com sucesso")
                    
        except Exception as e:
            channel_name = self.get_channel_name(message.channel)
            self.logger.error(f"Erro no canal {channel_name}: {e}", exc_info=True)
            await message.reply("Desculpe, ocorreu um erro. Pode tentar novamente?")

    @commands.command(name="config")
    @commands.has_permissions(administrator=True)
    async def configure(self, ctx: commands.Context, 
                        temperatura: Optional[float] = None,
                        top_p: Optional[float] = None,
                        top_k: Optional[int] = None,
                        max_tokens: Optional[int] = None):
        """Configura os parâmetros do modelo."""
        try:
            updates = {}
            if temperatura is not None:
                if not 0 <= temperatura <= 1:
                    self.logger.warning(
                        f"Temperatura inválida: {temperatura} | "
                        f"Usuário: {ctx.author}"
                    )
                    await ctx.send("❌ Temperatura deve estar entre 0 e 1!")
                    return
                updates["temperature"] = temperatura

            if top_p is not None:
                if not 0 <= top_p <= 1:
                    self.logger.warning(
                        f"top_p inválido: {top_p} | "
                        f"Usuário: {ctx.author}"
                    )
                    await ctx.send("❌ top_p deve estar entre 0 e 1!")
                    return
                updates["top_p"] = top_p

            if top_k is not None:
                if not 1 <= top_k <= 1000:
                    self.logger.warning(
                        f"top_k inválido: {top_k} | "
                        f"Usuário: {ctx.author}"
                    )
                    await ctx.send("❌ top_k deve estar entre 1 e 1000!")
                    return
                updates["top_k"] = top_k

            if max_tokens is not None:
                if not 1 <= max_tokens <= 8192:
                    self.logger.warning(
                        f"max_output_tokens inválido: {max_tokens} | "
                        f"Usuário: {ctx.author}"
                    )
                    await ctx.send("❌ max_output_tokens deve estar entre 1 e 8192!")
                    return
                updates["max_output_tokens"] = max_tokens

            if updates:
                old_config = self.generation_config.copy()
                self.generation_config.update(updates)
                self.logger.info(
                    f"Configuração alterada de {old_config} para {self.generation_config} | "
                    f"Usuário: {ctx.author}"
                )
                config_messages = [
                    f"✅ `temperature`: {self.generation_config['temperature']}",
                    f"✅ `top_p`: {self.generation_config['top_p']}",
                    f"✅ `top_k`: {self.generation_config['top_k']}",
                    f"✅ `max_output_tokens`: {self.generation_config['max_output_tokens']}"
                ]
                await ctx.send("Configurações atualizadas:\n" + "\n".join(config_messages))
            else:
                current_config = (
                    f"Temperatura: {self.generation_config['temperature']}\n"
                    f"Top P: {self.generation_config['top_p']}\n"
                    f"Top K: {self.generation_config['top_k']}\n"
                    f"Max Output Tokens: {self.generation_config['max_output_tokens']}"
                )
                await ctx.send(f"📊 Configurações atuais:\n{current_config}")
                
        except Exception as e:
            self.logger.error("Erro ao configurar parâmetros do modelo", exc_info=True)
            await ctx.send("❌ Erro ao configurar parâmetros do modelo.")

    @commands.command(name="logs")
    @commands.has_permissions(administrator=True)
    async def show_logs(self, ctx: commands.Context, lines: int = 10):
        """Mostra as últimas linhas do log (apenas para administradores)."""
        try:
            latest_logs: List[str] = self.logger.get_latest_logs(lines)
            log_text = "```\n" + "".join(latest_logs) + "\n```"
            
            if len(log_text) > 2000:
                chunks = [log_text[i:i+2000] for i in range(0, len(log_text), 2000)]
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(log_text)
                
            self.logger.info(f"Logs mostrados para {ctx.author}")
            
        except Exception as e:
            self.logger.error("Erro ao mostrar logs", exc_info=True)
            await ctx.send("❌ Erro ao recuperar logs.")

    @commands.command(name="convite")
    async def convite(self, ctx: commands.Context):
        """Gera um link de convite para adicionar o bot a outros servidores."""
        try:
            permissions = discord.Permissions(
                send_messages=True,
                read_messages=True,
                read_message_history=True,
                embed_links=True,
                external_emojis=True,
                manage_messages=False,
                manage_channels=False,
                # Adicione outras permissões conforme necessário
            )
            link = discord.utils.oauth_url(
                self.bot.user.id,
                permissions=permissions,
                scopes=['bot', 'applications.commands']
            )
            await ctx.send(f"🔗 Link para me adicionar: {link}")
            self.logger.info(f"Link de convite enviado para {ctx.author}")
        except Exception as e:
            self.logger.error("Erro ao gerar link de convite", exc_info=True)
            await ctx.send("❌ Erro ao gerar link de convite.")

async def setup(bot: commands.Bot):
    """Função de setup do cog."""
    await bot.add_cog(GeminiCog(bot))
