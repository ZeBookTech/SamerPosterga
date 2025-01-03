# Samélio - Bot Discord com Gemini AI

Samélio é um bot Discord especializado em suporte jurídico, utilizando a API do Google Gemini para fornecer respostas precisas e educativas sobre temas do Direito.

## 🤖 Características

- **Assistente Jurídico**: Responde perguntas sobre diversas áreas do Direito
- **Personalidade Única**: Age como um ex-juiz aposentado dedicado ao ensino
- **Respostas Detalhadas**: Fornece explicações claras e fundamentadas
- **Sistema de Logs**: Monitoramento completo das interações
- **Configurável**: Permite ajustes na temperatura do modelo

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/ZeBookTech/SamerPosterga.git
cd SamerPosterga
```

2. Crie um ambiente virtual:
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente no arquivo `.env`:
```env
DISCORD_TOKEN=seu_token_do_discord
GOOGLE_API_KEY=sua_chave_api_do_gemini
```

## 💻 Uso

1. Inicie o bot:
```bash
python bot.py
```

2. Comandos disponíveis:
- Responde automaticamente a todas as mensagens no canal
- `!config [temperatura]` - Configura a temperatura do modelo (0-1)
- `!logs [linhas]` - Mostra os últimos logs (apenas administradores)

## 🛠️ Configuração

O bot utiliza as seguintes configurações padrão:
- Temperatura: 0.9
- Top P: 1
- Top K: 32
- Máximo de tokens: 4096

## 📝 Logs

O sistema mantém logs detalhados de:
- Inicialização do bot
- Mensagens recebidas
- Respostas geradas
- Erros e exceções
- Alterações de configuração

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ✨ Créditos

Desenvolvido por [ZeBookTech](https://github.com/ZeBookTech)

## 📞 Suporte

Para suporte, entre em contato através das Issues do GitHub ou pelo Discord.
