import folium as fm
import json


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
            icono = fm.CustomIcon(icon_image="icono.jpg",icon_size = (30,40))
            fm.Marker(location=[latitud,longitud],popup=name,icon=icono).add_to(mapa)
    return mapa