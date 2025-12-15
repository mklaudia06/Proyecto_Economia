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
    dicccionario = {'pollo_ontop':0,'pollo_under':0,'aceite_ontop': 0,'aceite_under':0,'leche_ontop':0,'leche_under':0, 'salchichas_under':0, 'salchichas_ontop':0}
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
            if 'salchichas' in name:
                if price <= 1045:
                    dicccionario['salchichas_under'] += 1
                else:
                    dicccionario['salchichas_ontop'] += 1                    
    products = ['Pollo','Aceite','Leche','Salchichas']
    under = [dicccionario['pollo_under'], dicccionario['aceite_under'], dicccionario['leche_under'],dicccionario['salchichas_under']]
    ontop = [dicccionario['pollo_ontop'], dicccionario['aceite_ontop'], dicccionario['leche_ontop'],dicccionario['salchichas_ontop']]
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
    
    plt.figure(figsize=(8, 6))
    plt.pie(porcentaje, labels=categorias.keys(), autopct='%1.1f%%')
    plt.title('Distribución con porcentajes')
    plt.show()

def lista_productos (diccionario):
    products = []
    for dict in diccionario:
        for product in dict['products']:
            products.append(product)
    return products

def porciento_marcas_productos(diccionario):
    products_basic = ['arroz', 'frijoles', 'aceite', 'leche', 'azucar']
    products = lista_productos(diccionario)  
    conteo_productos = {}
    for producto in products_basic:
        conteo_productos[producto] = {
            'nacional': 0,
            'internacional': 0
        }
    
    for producto in products:
        nombre = producto['name'].lower()  
        for basico in products_basic:
            if basico in nombre:
                if producto['nacional'] is not None:
                    if producto['nacional']: 
                        conteo_productos[basico]['nacional'] += 1
                    else:  
                        conteo_productos[basico]['internacional'] += 1
                    break  
    
    productos_nombres = [p.capitalize() for p in products_basic]
    nacionales_counts = []
    internacionales_counts = []
    porcentajes_nacional = []
    porcentajes_inter = []
    
    for producto in products_basic:
        n = conteo_productos[producto]['nacional']
        i = conteo_productos[producto]['internacional']
        total = n + i
        
        nacionales_counts.append(n)
        internacionales_counts.append(i)
        
        if total > 0:
            porcentajes_nacional.append((n / total) * 100)
            porcentajes_inter.append((i / total) * 100)
        else:
            porcentajes_nacional.append(0)
            porcentajes_inter.append(0)
    
    # Crear gráfica con dos subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # ===== GRÁFICA 1: Barras agrupadas (cantidades absolutas) =====
    x_pos = list(range(len(productos_nombres)))
    width = 0.35
    
    # Barras nacionales
    bars_nac = ax1.bar([x - width/2 for x in x_pos], nacionales_counts, width,
                      label='Nacional', color='#1f77b4', alpha=0.8)
    
    # Barras internacionales
    bars_int = ax1.bar([x + width/2 for x in x_pos], internacionales_counts, width,
                      label='Internacional', color='#ff7f0e', alpha=0.8)
    
    ax1.set_xlabel('Productos', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Cantidad', fontsize=11, fontweight='bold')
    ax1.set_title('Cantidad de Marcas por Producto', fontsize=13, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(productos_nombres, fontsize=10)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Agregar valores en las barras
    for bars in [bars_nac, bars_int]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    #GRÁFICA 2: Barras apiladas (porcentajes)
    # Crear barras apiladas
    ax2.bar(productos_nombres, porcentajes_nacional, 
           label='Nacional', color='#1f77b4', alpha=0.8)
    
    ax2.bar(productos_nombres, porcentajes_inter, 
           bottom=porcentajes_nacional,
           label='Internacional', color='#ff7f0e', alpha=0.8)
    
    ax2.set_xlabel('Productos', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Porcentaje (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Distribución Porcentual', fontsize=13, fontweight='bold')
    ax2.set_xticklabels(productos_nombres, rotation=45, fontsize=10)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # Agregar porcentajes en la gráfica apilada
    for idx, (nacional, inter) in enumerate(zip(porcentajes_nacional, porcentajes_inter)):
        if nacional > 0:
            ax2.text(idx, nacional/2, f'{nacional:.1f}%', 
                    ha='center', va='center', color='white', fontweight='bold', fontsize=9)
        if inter > 0:
            ax2.text(idx, nacional + inter/2, f'{inter:.1f}%', 
                    ha='center', va='center', color='white', fontweight='bold', fontsize=9)
    
    plt.suptitle('Análisis de Marcas Nacionales vs Internacionales\nProductos de Canasta Básica', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.show()

def convertir_usd_a_cup(lista_productos_usd):
    eltoque = read_archive('../json/tasas_compra.json')
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
                "price": precio_cup
            })

    return productos_en_cup

def topes_dollar(precios_topados, tienda_dollar):
    precios_topados = read_archive(precios_topados)
    list_products = lista_productos(tienda_dollar)
    productos_cup = convertir_usd_a_cup(list_products)
    
    # Diccionario para almacenar resultados
    resultados = {}
    
    # Calcular excesos para cada producto topado
    for producto_key, precio_tope in precios_topados.items():
        # Buscar este producto en la tienda
        precio_tienda = 0
        for producto_tienda in productos_cup:
            nombre_tienda = producto_tienda.get('name', '').lower()
            
            # Verificar coincidencia simple (primera palabra del key)
            palabra_clave = producto_key.split('_')[0].lower()
            if palabra_clave in nombre_tienda:
                precio_tienda = producto_tienda.get('precio_cup', 0)
                break
        
        # Calcular exceso
        exceso = precio_tienda - precio_tope
        if exceso < 0:
            exceso = 0
            
        # Guardar resultado
        resultados[producto_key] = {
            'nombre': producto_key.replace('_', ' ').title(),
            'topado': precio_tope,
            'tienda': precio_tienda,
            'exceso': exceso
        }
    
    # Ordenar por exceso (mayor a menor)
    items_ordenados = sorted(
        resultados.items(),
        key=lambda x: x[1]['exceso'],
        reverse=True
    )
    
    # Preparar datos para gráfica
    nombres = [item[1]['nombre'] for item in items_ordenados]
    excesos = [item[1]['exceso'] for item in items_ordenados]
    precios_tienda = [item[1]['tienda'] for item in items_ordenados]
    precios_topado = [item[1]['topado'] for item in items_ordenados]
    
    # Crear gráfico
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # GRÁFICA 1: Barras horizontales de excesos
    bars = ax1.barh(nombres, excesos, color=['#ff6b6b', '#ffa726', '#42a5f5', '#66bb6a'][:len(nombres)])
    
    # Etiquetas en barras
    for bar, valor in zip(bars, excesos):
        if valor > 0:
            width = bar.get_width()
            ax1.text(width + 20, bar.get_y() + bar.get_height()/2,
                    f'+{int(valor):,} CUP', ha='left', va='center', fontweight='bold')
    
    ax1.set_xlabel('Exceso sobre precio topado (CUP)')
    ax1.set_title('EXTRA pagado en tienda en dólares')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Calcular y mostrar total
    total_exceso = sum(excesos)
    
    
    # Añadir información de total en gráfica
    fig.text(0.02, 0.02, f'Total exceso: {total_exceso:,} CUP', 
             fontsize=11, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
    
    plt.tight_layout()
    plt.show()
    
    return resultados


def precio_canasta_basica(diccionario):
    #hacer un recuento de los productos de la canasta basica y buscar los de menor precio y sumarlos
    products_basic = ['arroz', 'frijoles', 'aceite', 'leche', 'azucar']
    menor_precio = []
    productos = lista_productos(diccionario)
    precios = {"arroz":[], 'frijoles':[], 'aceite':[],'leche':[],'azucar':[]}
    for producto in productos:
        nombre = producto['name'].lower()  
        for basico in products_basic:
            if basico in nombre:
                precios[basico].append(producto['price'])
    for basico in products_basic:
        if precios[basico]: 
            menor_precio.append(min(precios[basico]))
        else:
            menor_precio.append(0)
    
    suma = sum(menor_precio)
    return suma

def salario(diccionario_salario,dicc_canasta):
    actividades = []
    salarios_promedio = []
    precio_canasta = precio_canasta_basica(dicc_canasta)
    for key,value in diccionario_salario.items():
        actividades.append(key)
        salarios_promedio.append(value)
    # Calcular cuántas canastas se pueden comprar con cada salario
    canastas_por_salario = [salario / precio_canasta for salario in salarios_promedio]

    # Crear índices para las posiciones de las barras
    num_actividades = len(actividades)
    indices = list(range(num_actividades))
    ancho_barra = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Gráfico 1: Comparación directa salario vs canasta
    for i in indices:
        ax1.bar(i - ancho_barra/2, salarios_promedio[i], ancho_barra, color='blue', alpha=0.7)
        ax1.bar(i + ancho_barra/2, precio_canasta, ancho_barra, color='red', alpha=0.7)

    # Solo agregar las etiquetas una vez
    ax1.bar(0, 0, color='blue', label='Salario mensual', alpha=0.7)
    ax1.bar(0, 0, color='red', label='Canasta básica', alpha=0.7)

    ax1.set_xlabel('Actividad Económica')
    ax1.set_ylabel('Monto ($)')
    ax1.set_title('Salario vs Precio Canasta Básica')
    ax1.set_xticks(indices)
    ax1.set_xticklabels(actividades, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Gráfico 2: Cuántas canastas se pueden comprar
    for i in indices:
        color = 'green' if canastas_por_salario[i] >= 1 else 'orange'
        ax2.bar(i, canastas_por_salario[i], color=color, alpha=0.7)

    ax2.axhline(y=1, color='r', linestyle='--', label='Límite 1 canasta')
    ax2.set_xlabel('Actividad Económica')
    ax2.set_ylabel('Número de canastas')
    ax2.set_title('Canastas Básicas que se pueden comprar')
    ax2.set_xticks(indices)
    ax2.set_xticklabels(actividades, rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

def salario_porcentaje(diccionario_salario,dicc_canasta):
    actividades = []
    salarios_promedio = []
    precio_canasta = precio_canasta_basica(dicc_canasta)
    for key,value in diccionario_salario.items():
        actividades.append(key)
        salarios_promedio.append(value)         
    porcentaje_gasto = [(precio_canasta / salario) * 100 for salario in salarios_promedio]
    restante = [100 - p for p in porcentaje_gasto]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Crear barras apiladas manualmente
    for i, actividad in enumerate(actividades):
        ax.bar(actividad, porcentaje_gasto[i], label='% para canasta' if i == 0 else "", 
            color='orange', alpha=0.7)
        ax.bar(actividad, restante[i], bottom=porcentaje_gasto[i], 
            label='% restante' if i == 0 else "", color='lightblue', alpha=0.7)

    ax.set_ylabel('Porcentaje del salario (%)')
    ax.set_title('Proporción del salario destinada a la canasta básica')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()    

def graf_lineas (diccionario_salario,dicc_canasta):
    actividades = []
    salarios_promedio = []
    precio_canasta = precio_canasta_basica(dicc_canasta)
    # Calcular cuántas canastas se pueden comprar con cada salario
    canastas_por_salario = [salario / precio_canasta for salario in salarios_promedio]
    for key,value in diccionario_salario.items():
        actividades.append(key)
        salarios_promedio.append(value) 
    fig, ax1 = plt.subplots(figsize=(12, 6))

    color1 = 'tab:blue'
    ax1.set_xlabel('Actividad Económica')
    ax1.set_ylabel('Salario ($)', color=color1)

    # Gráfico de línea para salarios
    ax1.plot(actividades, salarios_promedio, marker='o', color=color1, 
            linewidth=2, label='Salario')
    ax1.tick_params(axis='y', labelcolor=color1)

    # Segunda escala para la relación salario/canasta
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('Canastas que se pueden comprar', color=color2)
    ax2.plot(actividades, canastas_por_salario, marker='s', color=color2, 
            linestyle='--', linewidth=2, label='Canastas/salario')
    ax2.axhline(y=1, color='gray', linestyle=':', alpha=0.7, label='Línea de 1 canasta')
    ax2.tick_params(axis='y', labelcolor=color2)

    fig.tight_layout()
    plt.title('Salario y poder adquisitivo por actividad económica')
    plt.grid(True, alpha=0.3)
    plt.show()   