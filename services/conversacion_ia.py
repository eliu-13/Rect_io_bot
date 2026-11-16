from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler, CallbackContext, CallbackQueryHandler
import telegramify_markdown
from services.estados_meli import CONVERSANDO_IA, OTRO
from config import GEMINI
from google import genai
from services.meli_busqueda_filtros import cancel
import json

cliente = genai.Client(api_key=GEMINI)

async def iniciar_conversacion_ia(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    
    resultados_scrap = context.user_data.get("ultimos_resultados")
    
    if not resultados_scrap:
        boton_regreso = InlineKeyboardMarkup(
                inline_keyboard= [
                    [InlineKeyboardButton(text= "Regresar a la búsqueda", callback_data="meli_buscar")]]
                )
        await update.callback_query.message.reply_text("No hay resultados que analizar, presione el botón abajo para buscar en MeLi", reply_markup= boton_regreso)
        return ConversationHandler.END
    
    
    productos_texto = json.dumps(resultados_scrap, ensure_ascii=False, indent=2)
    
    instrucciones_sistema = (
        "Eres un asistente experto en compras de Mercado Libre. "
        "Analiza únicamente los siguientes resultados de búsqueda para responder al usuario de forma clara, concisa y útil. "
        "Si te preguntan por algo que no está en la lista, indícalo amablemente. "
        "Si no tienes información sobre un producto dilo abiertamente, sin inventar nada.\n\n"
        f"Resultados disponibles:\n{productos_texto}"
    )
    
    configuracion = {
        "system_instruction": instrucciones_sistema
    }
    
    context.user_data["historial_chat_ia"] = cliente.aio.chats.create(
        model="gemini-3.8-flash",
        config=configuracion
    )
    
    
    
    context.user_data["ia_resultados"] = resultados_scrap
    texto = (
        "🤖 *Análisis de resultados con IA*\n\n"
        f"Se recibieron {len(resultados_scrap)} productos. "
        "¿Qué te gustaría saber?\n"
        "Ejemplos:\n"
        "• ¿Cuál es la mejor opción calidad/precio?\n"
        "• Compara los 3 más baratos\n"
        "• ¿Hay algún producto con envío gratis y buena reputación?"
    )
    await update.callback_query.message.reply_text(texto, parse_mode="Markdown")
    return CONVERSANDO_IA



async def responder_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    consulta = update.message.text
    chat = context.user_data["historial_chat_ia"]
    
    if not chat:
        await update.message.reply_text("La sesión expiró. Busque nuevamente")
        return ConversationHandler.END
    
    await update.message.chat.send_action(action="typing")
    
    try:
        respuesta_gemini = await chat.send_message(consulta)
        
        texto_respuesta = respuesta_gemini.text
        response = telegramify_markdown.markdownify(texto_respuesta)
        await update.message.reply_text(response.text if hasattr(response, 'text') else response, parse_mode="MarkdownV2")
    
    except Exception as e:
        await update.message.reply_text(f"Ha ocurrido un error: {e}")
        
    return CONVERSANDO_IA


conversacion_ia = ConversationHandler(
    entry_points=[CallbackQueryHandler(iniciar_conversacion_ia, pattern="^IA$")],
    states={
        CONVERSANDO_IA: [MessageHandler(filters.TEXT & ~filters.COMMAND, responder_ia)],
        },
    fallbacks=[CommandHandler("cancel", cancel)]
)

