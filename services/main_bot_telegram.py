from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from config import TOKEN_TELEGRAM
from services.meli_busqueda_filtros import conversacion_meli, condicion
from services.conversacion_ia import conversacion_ia


# Funciones iniciales básicas

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aquí tienes una lista de comandos que te servirán:\n"
                                    "/start - Iniciar el bot\n"
                                    "/help - Ver este mensaje de ayuda\n"
                                    "/meli - Inicia búsqueda en Mercado Libre\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola!\n\nBienvenido a tu buscador de precios de confianza 👋✨\n"
                                    "Encontrar las mejores ofertas y cuidar tu bolsillo nunca fue tan fácil."
                                    " ¡Olvídate de dar mil vueltas y comparar en decenas de páginas!"
                                    " Yo hago el trabajo pesado por ti."
                                    " 🦾💰\n\n¿Qué compra inteligente haremos hoy?\n👇"
                                    " Escribe /meli para empezar a buscar tu producto y sigue los pasos:")

def iniciar_bot():
    application = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(conversacion_meli)
    application.add_handler(conversacion_ia)
    
    print("Running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)