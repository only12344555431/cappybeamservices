from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
import io
import re
import asyncio
from aiohttp import web
import os

API_BASE_URL = "https://mesutv44.pythonanywhere.com/log?ara="

# ----------------- LOG ÇEKME KOMUTU -----------------
async def logcek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir URL girin. Örnek: /logcek example.com")
        return

    url = context.args[0]

    if not re.match(r'^https?://', url):
        url = 'https://' + url

    await update.message.reply_text("Loglarınız çekiliyor, lütfen bekleyiniz...")

    async with aiohttp.ClientSession() as session:
        api_url = f"{API_BASE_URL}{url}"
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.text()
                lines = [line.strip() for line in data.splitlines() if line.strip()]
                formatted_data = '\n'.join(lines)

                txt_file = io.BytesIO(formatted_data.encode())
                txt_file.name = f"log_{url.replace('https://','').replace('/', '_')}.txt"

                await update.message.reply_document(document=txt_file, caption=f"{url} için log verileri:")
            else:
                await update.message.reply_text(f"API'den veri alınamadı. Hata kodu: {response.status}")

# ----------------- BASİT HTTP SERVER -----------------
async def handle(request):
    return web.Response(text="Bot çalışıyor!")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))  # Render otomatik PORT verir
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# ----------------- BOT BAŞLATMA -----------------
async def main():
    bot_app = ApplicationBuilder().token(os.environ.get("7664476297:AAHscWHgcIKMcGyQzXfpTMw_zOUtFyPPcqE")).build()
    bot_app.add_handler(CommandHandler("logcek", logcek))

    # HTTP serverı başlat
    asyncio.create_task(start_server())

    print("Bot çalışıyor...")
    await bot_app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
