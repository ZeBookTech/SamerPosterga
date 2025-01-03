# cogs/gemini_cog.py

import discord
from discord.ext import commands
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
from utils.logger import Logger

load_dotenv()

class GeminiCog(commands.Cog, name="Comandos Gemini"):
    """Comandos de IA usando Google Gemini para suporte jurídico."""

    def __init__(self, bot):
        self.bot = bot
        self.logger = Logger('GeminiCog')
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            self.logger.error("GOOGLE_API_KEY não encontrada no .env")
            raise ValueError("GOOGLE_API_KEY não encontrada")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chats = {}
        
        self.generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 4096,
        }
        
        self.logger.info("GeminiCog inicializado com sucesso")

        # Instruções personalizadas para o modelo
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

    def get_channel_name(self, channel):
        """Retorna o nome do canal de forma segura"""
        if isinstance(channel, discord.DMChannel):
            return "Mensagem Direta"
        elif isinstance(channel, discord.GroupChannel):
            return "Grupo Privado"
        elif isinstance(channel, discord.Thread):
            return f"Thread: {channel.name}"
        else:
            return f"#{channel.name}"

    async def get_gemini_response(self, message_content, user_id):
        """Obtém resposta do Gemini com base nas instruções personalizadas e tratamento de erros"""
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
            self.logger.error(f"Erro ao gerar resposta para usuário {user_id}: {e}", e)
            return "Desculpe, ocorreu um erro. Por favor, tente novamente."

    def should_respond(self, message):
        """Verifica se o bot deve responder à mensagem"""
        # Ignora mensagens de bots
        if message.author.bot:
            return False

        # Obtém o conteúdo limpo da mensagem
        content = message.content.strip().lower()
        
        # Verifica menção direta ao bot
        is_mentioned = self.bot.user.id in [m.id for m in message.mentions]
        
        # Verifica se começa com "samer" seguido de espaço ou pontuação
        starts_with_name = content.startswith('samer ') or \
                          content.startswith('samer,') or \
                          content.startswith('samer:') or \
                          content.startswith('samer?') or \
                          content.startswith('samer!')
        
        # Verifica se é uma resposta a uma mensagem do bot
        is_reply_to_bot = (
            message.reference and 
            message.reference.resolved and 
            message.reference.resolved.author.id == self.bot.user.id
        )
        
        # Só responde se for mencionado ou chamado pelo nome
        should_respond = is_mentioned or starts_with_name
        
        # Loga a decisão para debug
        if should_respond:
            self.logger.info(
                f"Respondendo mensagem | "
                f"Autor: {message.author} | "
                f"Conteúdo: {content} | "
                f"Mencionado: {is_mentioned} | "
                f"Nome: {starts_with_name}"
            )
        
        return should_respond

    @commands.Cog.listener()
    async def on_message(self, message):
        """Responde apenas quando explicitamente chamado"""
        if not self.should_respond(message):
            return

        try:
            # Remove menções e nome do bot
            content = message.content
            
            # Remove menções ao bot
            if self.bot.user in message.mentions:
                content = content.replace(f'<@{self.bot.user.id}>', '').strip()
            
            # Remove "samer" do início se presente
            if content.lower().startswith('samer'):
                words = content.split()
                content = ' '.join(words[1:]).strip()
            
            # Se não sobrou conteúdo após limpeza, não responde
            if not content:
                return
                
            channel_name = self.get_channel_name(message.channel)
            
            self.logger.info(
                f"Mensagem recebida | Canal: {channel_name} | "
                f"Usuário: {message.author.name} | ID: {message.author.id}"
            )
            
            async with message.channel.typing():
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
            self.logger.error(f"Erro no canal {channel_name}: {e}", e)
            await message.reply("Desculpe, ocorreu um erro. Pode tentar novamente?")

    @commands.command(name="config")
    async def configure(self, ctx, temperatura: float = None):
        """Configura a temperatura do modelo"""
        try:
            if temperatura is not None:
                if not 0 <= temperatura <= 1:
                    self.logger.warning(
                        f"Temperatura inválida: {temperatura} | "
                        f"Usuário: {ctx.author.name}"
                    )
                    await ctx.send("❌ Temperatura deve estar entre 0 e 1!")
                    return
                
                old_temp = self.generation_config["temperature"]
                self.generation_config["temperature"] = temperatura
                self.logger.info(
                    f"Temperatura alterada de {old_temp} para {temperatura} | "
                    f"Usuário: {ctx.author.name}"
                )
                await ctx.send(f"✅ Temperatura configurada para {temperatura}")
            else:
                current_temp = self.generation_config["temperature"]
                await ctx.send(f"A temperatura atual é {current_temp}")
                
        except Exception as e:
            self.logger.error("Erro ao configurar temperatura", e)
            await ctx.send("❌ Erro ao configurar temperatura")

    @commands.command(name="logs")
    @commands.has_permissions(administrator=True)
    async def show_logs(self, ctx, lines: int = 10):
        """Mostra as últimas linhas do log (apenas para administradores)"""
        try:
            latest_logs = self.logger.get_latest_logs(lines)
            log_text = "```\n" + "".join(latest_logs) + "\n```"
            
            if len(log_text) > 1900:
                chunks = [log_text[i:i+1900] for i in range(0, len(log_text), 1900)]
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(log_text)
                
            self.logger.info(f"Logs mostrados para {ctx.author.name}")
            
        except Exception as e:
            self.logger.error("Erro ao mostrar logs", e)
            await ctx.send("❌ Erro ao recuperar logs")

async def setup(bot):
    """Função de setup do cog"""
    await bot.add_cog(GeminiCog(bot))