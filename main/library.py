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

def take_name (dictionaries):
    for dictionary in dictionaries:
        dicionarios = dictionary['products']
        for i in dicionarios:
            name = i['name'].lower()
    return name

def take_price(dictionaries):
    for dictionary in dictionaries:
        dicionarios = dictionary['products']
        for i in dicionarios:
            price = i['price']
    return price


def precios_topados(dictionaries):
    dicccionario = {'pollo_ontop':0,'pollo_under':0,'aceite_ontop': 0,'aceite_under':0,'leche_ontop':0,'leche_under':0}
    name = take_name(dictionaries)
    price = take_price(dictionaries)
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
    
    return dicccionario

def promedio_precios(diccionario):
    products_basic = ['arroz','sal','frijoles','aceite','leche']
    name = take_name(diccionario)
    price = take_price(diccionario)
    for product in products_basic:

    