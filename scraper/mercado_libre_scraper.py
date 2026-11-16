import os
from curl_cffi import requests
from bs4 import BeautifulSoup
from seleniumbase import Driver
import urllib.parse
from scraper.armar_sufijos_url import armar_sufijos


def scraper_meli(filtros_busqueda: dict):
    
    # Definir componentes de la url
    articulo_base = filtros_busqueda.get("nombre_articulo", "").replace(" ", "-")
    articulo = urllib.parse.quote(articulo_base)
    pais = filtros_busqueda.get("pais_seleccionado", "ve")
    condicion = filtros_busqueda.get("condicion_seleccionada")
    orden = filtros_busqueda.get("orden_seleccionado")
    precio_min = filtros_busqueda.get("precio_min_seleccionado")
    precio_max = filtros_busqueda.get("precio_max_seleccionado")
    envio = filtros_busqueda.get("envio_seleccionado")
    reputacion = filtros_busqueda.get("reputacion_seleccionada")
    
    url = f"https://listado.mercadolibre.com.{pais}/{articulo}{armar_sufijos(envio, precio_min, precio_max, condicion, orden, reputacion)}"
    
    es_servidor = os.getenv("ENTORNO") == "PRODUCCION"
    
    try:

        if es_servidor:
            from pyvirtualdisplay import Display
            display = Display(visible=0, size=(1920, 1080))
            display.start()
        
        driver = Driver(uc=True, headless=False, binary_location= r"D:\Program Files\Google\Chrome\Application\chrome.exe")
        
        driver.get(url)
        driver.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # 1. Nueva clase del contenedor principal
        contenedores = soup.find_all('li', class_='ui-search-layout__item')
        
        
        productos_extraidos = []
        for item in contenedores[:15]: # Cambiar (o quitar) número para scrapear más o menos
            
            # 2. Nuevas clases para título y enlace (están juntos)
            titulo_link_elem = item.find('a', class_='poly-component__title')
            
            # 3. Nueva clase para el precio final
            precio_elem = item.find('span', class_='poly-price__amount')

            if titulo_link_elem and precio_elem:
                
                # Extracción del texto del precio omitiendo centavos (si aplica)
                precio_moneda = precio_elem.find('span', class_='andes-money-amount__currency-symbol')
                precio_entero = precio_elem.find('span', class_='andes-money-amount__fraction')
                precio_centavos = precio_elem.find('span', class_='andes-money-amount__cents')
                
                precio_texto = ""
                if precio_moneda and precio_entero:
                    precio_texto = f"{precio_moneda.text.strip()} {precio_entero.text.strip()}"
                    if precio_centavos:
                        precio_texto += f",{precio_centavos.text.strip()}"
            
            
                link_original = titulo_link_elem.get('href')
                link_limpio = link_original.split('#')[0].split('?')[0]
                

                
                review_box = item.find(class_="poly-component__review-compacted")
                if review_box:
                    # Extrae todo el texto visible del bloque ignorando la estructura HTML interna
                    estrellas_texto = review_box.text.strip()
                else:
                    estrellas_texto = "Sin calificación"
                
                productos_extraidos.append({
                    "titulo": titulo_link_elem.text.strip(),
                    "precio": precio_texto,
                    "link": link_limpio,
                    "estrellas": estrellas_texto
                })
                
        driver.quit()
        
        if productos_extraidos == []:
            return "No se han encontrado resultados..."
        
        return productos_extraidos
    
    except Exception as e:
        if "driver" in locals():
            driver.quit()
        return f"Error en la extracción: {e}"
        
