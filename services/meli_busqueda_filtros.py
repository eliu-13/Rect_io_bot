from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler, CallbackContext, CallbackQueryHandler
from services.estados_meli import OBTENER_NOMBRE, FILTRO_PAIS, FILTRO_CONDICION, FILTRO_ORDEN, FILTRO_PRECIO_MIN, FILTRO_PRECIO_MAX, FILTRO_ENVIO, FILTRO_REPUTACION
import asyncio
from scraper.mercado_libre_scraper import scraper_meli

async def saludo_y_pedir_nombre_articulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Empecemos a buscar tu producto en \"Mercado Libre 📦\"\n"
                                    "Escribeme el producto que deseas buscar")
    return OBTENER_NOMBRE
    

async def pais_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # capta el nombre
    context.user_data["nombre_articulo"] = update.message.text
    
    # Mostrar botones para seleccionar filtros
    teclado_filtro_pais = InlineKeyboardMarkup(
        inline_keyboard= [[InlineKeyboardButton(text="🇻🇪 Venezuela", callback_data= "ve"),
        InlineKeyboardButton(text="🇦🇷 Argentina", callback_data= "ar"),
         ],
        [InlineKeyboardButton(text="🇨🇴 Colombia", callback_data= "co"),
        InlineKeyboardButton(text="🇲🇽 México", callback_data= "mx"),
         ],
        [InlineKeyboardButton(text="🌐 Otro", callback_data="None")]]
    )
    await update.message.reply_text("Escoge el país", reply_markup=teclado_filtro_pais)
    return FILTRO_PAIS



async def condicion(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    # guardar info presionada
    context.user_data["pais_seleccionado"] = update.callback_query.data
    
        # Mostrar botones para seleccionar filtros
    teclado_filtro_condicion = InlineKeyboardMarkup(
        inline_keyboard = [
        [InlineKeyboardButton(text="✨ ​Nuevo", callback_data= "new"),
        InlineKeyboardButton(text="♻️ Usado", callback_data= "used"),
        ],
        [InlineKeyboardButton(text="❌ No aplicar​", callback_data= "None"),],
    ]
    )
    
    await update.callback_query.edit_message_text("Escoge el estado del articulo", reply_markup=teclado_filtro_condicion)
    return FILTRO_CONDICION

async def orden(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    context.user_data["condicion_seleccionada"] = update.callback_query.data
    
    teclado_filtro_ordenamiento = InlineKeyboardMarkup(
        inline_keyboard = [
        [InlineKeyboardButton(text="↗️ Menor a mayor precio​", callback_data= "price_asc"),
        InlineKeyboardButton(text="↘️ Mayor a menor precio​", callback_data= "price_desc"),
        ],
        [InlineKeyboardButton(text="🔝 Más relevantes​", callback_data= "relevance")]
    ])
    await update.callback_query.edit_message_text("Escoge el orden de búsqueda", reply_markup=teclado_filtro_ordenamiento)
    return FILTRO_ORDEN

async def pedir_precio_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    context.user_data["orden_seleccionado"] = update.callback_query.data
    
    await update.callback_query.edit_message_text("Ingresa el precio mínimo en tu moneda local (\"0\" si no hay minimo)")
    return FILTRO_PRECIO_MIN

async def validar_precio_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["precio_min_seleccionado"] = update.message.text
    texto = update.message.text
    if not texto.isdigit():
        await update.message.reply_text("Ingresa un número positivo")
        return FILTRO_PRECIO_MIN
    
    context.user_data["precio_min_seleccionado"] = texto
    await update.message.reply_text("Genial, ingresa el precio máximo")
    return FILTRO_PRECIO_MAX
    
async def validar_precio_max(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["precio_max_seleccionado"] = update.message.text
    texto = update.message.text
    
    if not texto.isdigit():
        await update.message.reply_text("Ingresa un número positivo")
        return FILTRO_PRECIO_MAX
    
    if context.user_data["precio_min_seleccionado"] > context.user_data["precio_max_seleccionado"]:
        await update.message.reply_text("El precio máximo debe ser mayor que el mínimo")
        return FILTRO_PRECIO_MAX

    
    teclado_filtro_envio = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📮✅ Envío gratis​​", callback_data="free_shipping")],
            [InlineKeyboardButton(text="❌ No aplicar ", callback_data="None")]
        ]
    )
    await update.message.reply_text("¿Te gustaría envío gratis?", reply_markup=teclado_filtro_envio)
    return FILTRO_ENVIO

async def reputacion(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    context.user_data["envio_seleccionado"] = update.callback_query.data
    
    teclado_filtro_reputacion = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="​​​​👨🏻‍💼​✅​ Mejores vendedores", callback_data="best_sellers")],
            [InlineKeyboardButton(text="​​​​👨🏻‍💼​​​💼​ Todos los vendedores", callback_data="None")]
        ]
    )
    await update.callback_query.edit_message_text("Selecciona los vendedores", reply_markup=teclado_filtro_reputacion)
    return FILTRO_REPUTACION
        
        

async def scraping(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    context.user_data["reputacion_seleccionada"] = update.callback_query.data
    
    await update.callback_query.edit_message_text("Buscando los mejores resultados, esto puede tomar unos segundos...")
    
    # Llamar scraper
    resultados = await asyncio.to_thread(scraper_meli, context.user_data)
    
    if isinstance(resultados, str):
        await update.callback_query.message.reply_text(f"Ocurrió un error:\n{resultados}")
        return ConversationHandler.END
    
    context.user_data["ultimos_resultados"] = resultados
    
    
    teclado_ia = InlineKeyboardMarkup(
    inline_keyboard= [
        [InlineKeyboardButton(text= "🤖 ¿Cuál es la mejor opción? (IA)", callback_data="IA")]]
    )
    
    for item in resultados:
        respuesta = f"{item['titulo']}\n💰 {item['precio']}\n🔗 {item['link']}\n⭐ {item["estrellas"]}\n\n"
        await update.callback_query.message.reply_text(respuesta)

    await update.callback_query.message.reply_text(f"Aquí tienes los resultados ({len(resultados)}).\n\n", reply_markup= teclado_ia)
    return ConversationHandler.END


# Función para cancelar operaciones
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Proceso cancelado")
    return ConversationHandler.END
 

conversacion_meli = ConversationHandler(
    entry_points = [
        CommandHandler("meli", saludo_y_pedir_nombre_articulo),
        CallbackQueryHandler(saludo_y_pedir_nombre_articulo, pattern= "^meli_buscar$")     
    ],
    states = {
        OBTENER_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pais_usuario)],
        FILTRO_PAIS: [CallbackQueryHandler(condicion)],
        FILTRO_CONDICION: [CallbackQueryHandler(orden)],
        FILTRO_ORDEN: [CallbackQueryHandler(pedir_precio_min)],
        FILTRO_PRECIO_MIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, validar_precio_min)],
        FILTRO_PRECIO_MAX: [MessageHandler(filters.TEXT & ~filters.COMMAND, validar_precio_max)],
        FILTRO_ENVIO: [CallbackQueryHandler(reputacion)],
        FILTRO_REPUTACION: [CallbackQueryHandler(scraping)]
        
    },
    fallbacks= [CommandHandler("cancel", cancel)]
    )