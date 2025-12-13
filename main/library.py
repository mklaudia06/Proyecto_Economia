import folium as fm
import json
import matplotlib.pyplot as plt


def read_archive(ruta):
    with open(ruta,'r', encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return datos

def map (archivo):
    mapa = fm.Map(location = [23.075162, -82.358295],zoom_start=11)
    for dictionaries in archivo:
        name = dictionaries['name']
        if dictionaries['location']['coordinates_latitude_length'] is not None:
            latitud, longitud = dictionaries['location']['coordinates_latitude_length']
            icono = fm.CustomIcon(icon_image="icono.jpg",icon_size = (40,50))
            fm.Marker(location=[latitud,longitud],popup=name,icon=icono).add_to(mapa)
    return mapa

def porciento(parte,todo):
    return (parte/todo)*100

def take_name_price(dictionaries):
    names = []  
    prices = [] 
    
    for dictionary in dictionaries:
        productos = dictionary['products']
        for producto in productos:
            name = producto['name'].lower()
            price = producto['price']
            names.append(name)
            prices.append(price)
    
    return names, prices 

def precios_topados(dictionaries):
    dicccionario = {'pollo_ontop':0,'pollo_under':0,'aceite_ontop': 0,'aceite_under':0,'leche_ontop':0,'leche_under':0}
    for dictionary in dictionaries:
        dicionarios = dictionary['products']
        for i in dicionarios:
            name = i['name'].lower()
            price = i['price']
            if 'pollo' in name:
                if price <= 680:
                    dicccionario['pollo_under'] += 1
                else:
                    dicccionario['pollo_ontop'] += 1
            if 'aceite' in name:
                if price <= 990:
                    dicccionario['aceite_under'] += 1
                else:
                    dicccionario['aceite_ontop'] += 1
            if 'leche' in name:
                if price <= 1675:
                    dicccionario['leche_under'] += 1
                else:
                    dicccionario['leche_ontop'] += 1
    products = ['Pollo','Aceite','Leche']
    under = [dicccionario['pollo_under'], dicccionario['aceite_under'], dicccionario['leche_under']]
    ontop = [dicccionario['pollo_ontop'], dicccionario['aceite_ontop'], dicccionario['leche_ontop']]
    plt.figure(figsize=(10, 6))
    
    plt.figure(figsize=(10, 6))
    
    x = range(len(products))
    plt.bar(x, under, width=0.4, label='Por debajo del precio topado', color='green', alpha=0.7)
    plt.bar([i + 0.4 for i in x], ontop, width=0.4, label='Sobre el precio topado', color='red', alpha=0.7)
    
    plt.xlabel('Productos')
    plt.ylabel('Cantidad de Productos')
    plt.title('Comparación de Precios: Bajo vs Sobre el Tope')
    plt.xticks([i + 0.2 for i in x], products)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

def promedio (lista):
    n = len(lista)
    suma = sum(lista)
    return suma/n

def promedio_precios(diccionario):
    products_basic = ['arroz','frijoles','aceite','leche','azucar']
    suma = {}
    names,prices = take_name_price(diccionario)
    for product in products_basic:
        suma[product] = []
    for i in range(len(names)):
        producto = names[i]
        precio = prices[i]
        for product in products_basic:
            if product in producto:  
                suma[product].append(precio)
    promedios = []
    for _,value in suma.items():
        if value:
            promedios_calculados = promedio(value)
            promedios.append(promedios_calculados)
        else:
            promedios.append(0)
    
    plt.figure(figsize=(10, 6))
    plt.bar(products_basic, promedios, color='skyblue')
    plt.title('Promedio de Precios de Productos Básicos')
    plt.xlabel('Productos')
    plt.ylabel('Precio Promedio ($)')
    plt.xticks(rotation=0)
    plt.grid(axis='y', alpha=0.3)
    for i, v in enumerate(promedios):
        plt.text(i, v, f'${v:.1f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.show()

def promedio_precios_por_marca(diccionario_datos):
    """
    Calcula el precio promedio de cada producto de la canasta básica, 
    agrupado por la marca. Implementa robustez para precios y marcas nulas.
    """
    products_basic = ['arroz', 'frijoles', 'aceite', 'leche', 'azucar']
    
    # Estructura: {'producto': {'Marca X': {'total': X, 'count': Y}}}
    precios_totales_por_marca = {prod: {} for prod in products_basic}
    
    for i in diccionario_datos:
        productos_lista = i.get('products', []) 
        
        for producto in productos_lista:
            
            nombre_producto = producto.get('name', '').lower()
            precio_crudo = producto.get('price')
    
            marca_valor = producto.get('brand')
            if marca_valor is not None:
                marca = str(marca_valor) 


            precio = float(precio_crudo)
            producto_clave = None
            for p_basico in products_basic:
                if p_basico in nombre_producto:
                    producto_clave = p_basico
                    break
            
            if producto_clave:
                
                datos_del_producto = precios_totales_por_marca[producto_clave]
                
                if marca not in datos_del_producto:
                    datos_del_producto[marca] = {'total': 0, 'count': 0}
                
                datos_del_producto[marca]['total'] += precio
                datos_del_producto[marca]['count'] += 1

    promedios_finales = {}
    for producto, datos_marcas in precios_totales_por_marca.items():
        if datos_marcas: 
            producto_promedios = {}
            for marca, data in datos_marcas.items():
                if data['count'] > 0:
                    promedio = data['total'] / data['count']
                    producto_promedios[marca] = round(promedio, 2)
            
            if producto_promedios:
                 promedios_finales[producto] = producto_promedios
                    
    return promedios_finales

def generar_graficos_promedio(datos_promedios):  
    for producto, datos_marcas in datos_promedios.items():
        
        marcas = [m for m in datos_marcas.keys()]      
        precios = [p for p in datos_marcas.values()] 
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        barras = ax.bar(marcas, precios, color="#2ecc7a") 
        
        ax.set_title(f'Precio Promedio de {producto.capitalize()} por Marca', fontsize=16, pad=20)
        ax.set_ylabel('Precio Promedio ($)', fontsize=12)
        ax.set_xlabel('Marca del Producto', fontsize=12)
        
        plt.xticks(rotation=90, ha='right')
        
        # Añadir las etiquetas de precio encima de cada barra
        for bar in barras:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + (yval * 0.02), f'{yval:.2f}', 
                    ha='center', va='bottom', fontsize=8, weight='bold')
        
        ax.yaxis.grid(True, linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        plt.show() 


def origen_marcas (dicc):

    categorias = {
        "Internacionales": 0,
        "Nacionales": 0,
    }
    total = 0
    for dicts in dicc:
        products = dicts['products']
        for p_dict in products:
            if p_dict['brand'] is not None:
                total += 1
                if p_dict['nacional']:
                    categorias['Nacionales'] += 1
                else:
                    categorias['Internacionales'] += 1
    porcentaje = [porciento(categorias['Internacionales'],total), porciento(categorias['Nacionales'],total)]
    
    # Gráfico con porcentajes

    plt.figure(figsize=(8, 6))
    plt.pie(porcentaje, labels=categorias.keys(), autopct='%1.1f%%')
    plt.title('Distribución con porcentajes')
    plt.show()

def marcas_internacionales_nacionales(diccionario):
    #comparar los productos de la canasta basica de las marcas nacionales con la internacionales
    pass

def convertir_usd_a_cup(lista_productos_usd, eltoque):
    tasa_usd_compra = 0.0
    
    for tasa in eltoque.get("tasas_compra", []):
        if tasa.get("moneda") == "USD":
                tasa_usd_compra = float(tasa.get("compra", 0)) 
    
    productos_en_cup = []
    
    for producto_usd in lista_productos_usd:
        nombre_producto = producto_usd.get("name")
        precio_usd = producto_usd.get("price")
        
        if nombre_producto:
            precio_cup = round(precio_usd * tasa_usd_compra, 2)
            productos_en_cup.append({
                "name": nombre_producto,
                "price": precio_cup,
                "currency": "CUP"
            })

    return productos_en_cup

def comparar_dollar():
    #comparar los productos basicos de una tienda en dolar con los de las mipymes
    pass


def precio_canasta_basica():
    #hacer un recuento de los productos de la canasta basica y buscar los de menor precio y sumarlos
    #luego los de mayor precio y sumarlos

    pass
def salario():
    #comparar el precio total de la canasta basica en una mipyme con el salario promedio de un trabajador
    #incluso ver el tipo de trabajo del individuo y comparar el salario total de un pesquero por ejemplo
    #con la compra de la canasta
    #y luego con otra profesion
    pass