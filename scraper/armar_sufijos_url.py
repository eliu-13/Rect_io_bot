def armar_sufijos(envio, precio_min, precio_max, condicion, orden, reputacion):
    sufijo_filtros = ""
    
    if envio == "free_shipping":
        sufijo_filtros += "_CostoEnvio_Gratis"
        
    if precio_min and precio_max:
        sufijo_filtros += f"_PriceRange_{precio_min}USD-{precio_max}USD"
            
    if condicion == "new":
        sufijo_filtros += "_ITEM*CONDITION_2230284"
    elif condicion == "used":
        sufijo_filtros += "_ITEM*CONDITION_2230581"
    
    if orden == "price_asc":
        sufijo_filtros += "_OrderId_PRICE"
    elif orden == "price_desc":
        sufijo_filtros += "_OrderId_PRICE*DESC"
        
    if reputacion == "best_sellers":
        sufijo_filtros += "_BestSellers_YES"
        
    return sufijo_filtros