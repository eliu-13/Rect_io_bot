# 🛒 Bot de Precios - Mercado Libre con IA

Bot de Telegram que permite buscar productos en Mercado Libre aplicando filtros personalizados y analizar los resultados con inteligencia artificial (Google Gemini).

## ¿Qué hace este bot?

1. **Búsqueda filtrada**: El usuario puede buscar un producto en Mercado Libre aplicando filtros de país, condición (nuevo/usado), ordenamiento, rango de precios, envío gratis y reputación del vendedor.
2. **Análisis con IA**: Tras obtener los resultados, el usuario puede iniciar una conversación con un asistente de IA especializado en compras para comparar productos, identificar la mejor opción calidad/precio, o hacer preguntas específicas sobre los artículos encontrados.
3. Más adelante buscaré añadir más contexto al modelo, porque actualmente solo tiene la información de los productos que se le envia al usuario (Nombre de publicación, link, precio y valoración)
---

## 🚀 Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.x | Lenguaje principal |
| python-telegram-bot | 22.8 | Framework del bot de Telegram |
| seleniumbase | 4.58.1 | Automatización de navegador (scraper) |
| beautifulsoup4 | 4.15.0 | Parsing de HTML |
| curl_cffi | 0.17.0 | Peticiones HTTP |
| google-genai | 3.3.0 | Integración con Google Gemini |
| telegramify_markdown | 1.4.2 | Conversión de Markdown a MarkdownV2 de Telegram |
| python-dotenv | 1.2.4 | Gestión de variables de entorno |
| pyvirtualdisplay | 3.0 | Pantalla virtual para servidores Linux (headless) |

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener:

- Python 3.8 o superior instalado
- Un token de bot de Telegram (obtenido a través de [@BotFather](https://t.me/botfather))
- Una API key de [Google Gemini](https://makersuite.google.com/app/apikey)
- Google Chrome instalado en el sistema (requerido por SeleniumBase)
- (Para producción en Linux) `xvfb` instalado en el sistema

---

## ⚙️ Instalación y Configuración

### 1. Crear y activar entorno virtual

```bash
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido (guiate de `.env.example`):

```env
TOKEN_TELEGRAM=tu_token_de_telegram_aqui
GEMINI=tu_api_key_de_gemini_aqui
ENTORNO=LOCAL  # Opcional. Usa "PRODUCCION" en servidores Linux sin GUI
```

| Variable | Descripción | Obligatoria |
|----------|-------------|-------------|
| `TOKEN_TELEGRAM` | Token del bot proporcionado por @BotFather | ✅ Sí |
| `GEMINI` | API key de Google Gemini | ✅ Sí |
| `ENTORNO` | `"PRODUCCION"` activa modo headless con `pyvirtualdisplay`. En desarrollo se omite o se deja como `DESARROLLO` | ❌ No |

---

## 🏗️ Estructura del Proyecto

```
bot_precios_telegram/
├── .env                            # Variables de entorno (ignorado por git)
├── requirements.txt                # Dependencias de Python
├── config.py                       # Carga de variables de entorno (.env)
├── instrucciones_de_despliegue.md  # Guía detallada de ejecución local y producción
├── README.md                       # Este archivo
├── src/
│   └── main.py                     # Punto de entrada. Ejecuta iniciar_bot()
├── services/
│   ├── main_bot_telegram.py        # Inicialización del bot, comandos /start y /help
│   ├── meli_busqueda_filtros.py    # Conversación de búsqueda MELI (filtros + scraping)
│   ├── conversacion_ia.py          # Conversación de IA con Google Gemini
│   └── estados_meli.py             # Definición de estados de ConversationHandler
└── scraper/
    ├── mercado_libre_scraper.py    # Scraper de Mercado Libre (SeleniumBase + BeautifulSoup)
    └── armar_sufijos_url.py        # Construcción de sufijos de URL para filtros de MELI
```

### Descripción de módulos clave

| Archivo | Función |
|---------|---------|
| `src/main.py` | Punto de entrada. Llama a `iniciar_bot()` |
| `services/main_bot_telegram.py` | Configura la `Application` de Telegram, registra handlers y comandos básicos (`/start`, `/help`) |
| `services/meli_busqueda_filtros.py` | Implementa `conversacion_meli`: un `ConversationHandler` de 8 estados que guía al usuario por el flujo de búsqueda y filtros, y ejecuta el scraper |
| `services/conversacion_ia.py` | Implementa `conversacion_ia`: un `ConversationHandler` independiente que se activa con el botón "IA" y permite conversar con Gemini sobre los resultados scrapeados |
| `services/estados_meli.py` | Define los estados enteros usados por ambos `ConversationHandler` |
| `scraper/mercado_libre_scraper.py` | Navega a Mercado Libre con SeleniumBase, extrae hasta 15 productos con título, precio, enlace y calificación |
| `scraper/armar_sufijos_url.py` | Construye los sufijos de URL para aplicar los filtros seleccionados en Mercado Libre |

---

## ▶️ Uso y Ejecución

### Ejecutar en desarrollo (local)

```bash
python -m src.main
```

O directamente:

```bash
python src/main.py
```

El bot iniciará en modo polling y responderá a los comandos:

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida e instrucciones iniciales |
| `/help` | Lista de comandos disponibles |
| `/meli` | Inicia el flujo de búsqueda de productos en Mercado Libre |
| `/cancel` | Cancela la conversación en curso (en cualquier estado) |

### Flujo de uso

1. Escribe `/meli` para comenzar.
2. Ingresa el nombre del producto que deseas buscar.
3. Selecciona el país (Venezuela, Argentina, Colombia, México u Otro).
4. Elige la condición del artículo (Nuevo, Usado, No aplicar).
5. Selecciona el orden de los resultados (Menor a mayor precio, Mayor a menor precio, Más relevantes).
6. Ingresa el precio mínimo (o `"0"` si no hay mínimo).
7. Ingresa el precio máximo.
8. Selecciona si deseas envío gratis.
9. Selecciona la reputación del vendedor (Mejores vendedores o Todos).
10. El bot ejecutará el scraper y mostrará los resultados encontrados.
11. Pulsa el botón **"🤖 ¿Cuál es la mejor opción? (IA)"** para iniciar un análisis con Inteligencia Artificial.
12. Haz tus preguntas sobre los productos (ej: "¿Cuál es la mejor opción calidad/precio?").
13. Escribe `/cancel` en cualquier momento para salir de la conversación actual.

### Ejecutar en producción (servidor Linux / VPS)

Según `instrucciones_de_despliegue.md`:

1. Instala dependencias del sistema:
   ```bash
   sudo apt-get update
   sudo apt-get install -y xvfb
   ```

2. Ejecuta con la variable de entorno `ENTORNO=PRODUCCION`:
   ```bash
   ENTORNO=PRODUCCION python src/main.py
   ```

3. O usando Docker, añade la variable en `docker-compose.yml`:
   ```yaml
   services:
     bot_meli:
       build: .
       environment:
         - ENTORNO=PRODUCCION
   ```

   Y en el `Dockerfile`:
   ```dockerfile
   RUN apt-get update && apt-get install -y xvfb
   ```

> **Nota importante**: Nunca elimines la instrucción `driver.quit()` del scraper, incluso en bloques `except`, para evitar fugas de memoria RAM en el servidor. Se recomiendan al menos 4 GB de RAM disponibles.

---

## 🤖 Flujo de Conversación (IA)

Después de obtener los resultados de búsqueda, el usuario puede iniciar una conversación con el asistente de IA:

- El sistema crea una sesión de Google Gemini con `system_instruction` que incluye todos los productos scrapeados.
- El usuario puede hacer preguntas ilimitadas sobre los resultados.
- Las respuestas se formatean con `MarkdownV2` para un mejor renderizado en Telegram.
- Escribe `/cancel` para finalizar la sesión de IA.

---

## ⚠️ Notas y Limitaciones

- El scraper extrae un máximo de **15 productos** por búsqueda (configurable en `mercado_libre_scraper.py`).
- El modelo de IA configurado es `gemini-3.8-flash` (verificar disponibilidad en tu región).
- El bot no persiste historial entre reinicios; `context.user_data` se mantiene solo durante la sesión activa del usuario.
- En servidores Linux sin interfaz gráfica, es obligatorio definir `ENTORNO=PRODUCCION` e instalar `xvfb`.


>  **IMPORTANTE:** Este es un proyecto personal para portafolio. El flujo de las conversaciones está hecho por mi pero me apoyé de [Gemini](https://gemini.google.com/) para el scraping sobre todo.