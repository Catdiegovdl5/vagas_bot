import asyncio
import os
from aiohttp import web
import logging

# Configuração de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rota para o Render "bater" e ver se o servidor está vivo
async def health_check(request):
    return web.Response(text="Bot is running! 🚀")

async def start_web_server():
    """Inicia um mini-servidor web do aiohttp na porta configurada pelo Render."""
    app = web.Application()
    app.router.add_get('/', health_check)
    
    # O Render define a variável de ambiente PORT. 
    # Se rodar local, usa 8080 por padrão.
    port = int(os.environ.get('PORT', 8080))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    try:
        await site.start()
        logger.info(f"🌐 Servidor Web iniciado na porta {port}")
    except OSError:
        logger.warning(f"⚠️ Porta {port} já está em uso (Erro 10048). Ignorando Web Server e rodando apenas o Bot!")
    
    # Mantém o servidor rodando para sempre
    while True:
        await asyncio.sleep(3600)

async def main():
    # Importa o bot apenas aqui para não travar o carregamento do servidor web
    import bot
    
    # Roda o servidor web e o bot do Telegram ao mesmo tempo
    logger.info("🤖 Iniciando o Vagas Bot em paralelo com o Web Server...")
    
    # Cria a tarefa do servidor web
    web_task = asyncio.create_task(start_web_server())
    
    # Cria a tarefa do bot do Telegram
    bot_task = asyncio.create_task(bot.dp.start_polling(bot.bot))
    
    # Aguarda ambas as tarefas e encerra se uma falhar
    done, pending = await asyncio.wait(
        [web_task, bot_task],
        return_when=asyncio.FIRST_COMPLETED
    )
    
    for task in pending:
        task.cancel()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Processo encerrado pelo usuário.")
