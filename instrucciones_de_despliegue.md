# Scraper de Mercado Libre (SeleniumBase) - Guía de Ejecución

Este documento detalla las instrucciones necesarias para ejecutar el scraper de Mercado Libre tanto en entornos de desarrollo local (con interfaz gráfica) como en servidores de producción (modo headless con pantalla virtual).

## 1. Requisitos Generales (Ambos entornos)
Asegúrate de tener instaladas las librerías base de Python en tu entorno virtual:
```bash
pip install seleniumbase beautifulsoup4 curl_cffi
```

---

## 2. Ejecución Local (Desarrollo en Laptop)
En tu entorno local (Windows/Mac), el script abrirá automáticamente la ventana de Chrome para que puedas ver cómo el bot supera el muro de seguridad (Captcha Wall) de Mercado Libre.

**Pasos:**
1. No necesitas configurar ninguna variable de entorno.
2. Ejecuta tu script o el bot de Telegram normalmente:
```bash
python -m src.main
```
*Nota: La variable `es_servidor` en el código será `False` por defecto.*

---

## 3. Ejecución en Producción (Servidor Linux / VPS)
Para que SeleniumBase mantenga su modo indetectable (`uc=True`) sin ser bloqueado en un servidor sin monitor (GUI), utilizamos `Xvfb` (X virtual framebuffer) para emular una pantalla en la memoria RAM.

### A. Dependencias del Sistema (Linux)
Instala el emulador de pantalla en la terminal de tu servidor Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y xvfb
```

### B. Dependencias de Python adicionales
Instala la librería que permite a SeleniumBase comunicarse con Xvfb:
```bash
pip install pyvirtualdisplay
```

### C. Ejecución del Script
Para que el código sepa que está en el servidor y active la pantalla virtual, debes pasar la variable de entorno `ENTORNO=PRODUCCION`.

**Opción 1: Desde la terminal del servidor**
```bash
ENTORNO=PRODUCCION python main_bot_telegram.py
```

**Opción 2: Usando Docker (Recomendado)**
Si usas `docker-compose.yml`, añade la variable en la sección de environment:
```yaml
services:
  bot_meli:
    build: .
    environment:
      - ENTORNO=PRODUCCION
```
Y en tu `Dockerfile`, asegúrate de incluir la instalación de Xvfb:
```dockerfile
RUN apt-get update && apt-get install -y xvfb
```

## Notas Finales
*   **Gestión de Memoria:** Nunca elimines la instrucción `driver.quit()` del código, ni siquiera en los bloques `except`. Es vital para liberar la memoria RAM del servidor.
*   **Recursos:** El servidor debe contar con al menos 4 GB de RAM disponibles para evitar bloqueos por falta de memoria al inicializar el navegador oculto.