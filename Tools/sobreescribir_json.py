import os
from pathlib import Path
import json
import config

ruta_propia = Path(__file__).resolve()
carpeta_raiz = ruta_propia.parent.parent

ruta_carpeta = carpeta_raiz/"Shaders"

rutas_archivos = [archivo.resolve() for archivo in ruta_carpeta.rglob("*") if archivo.is_file()] #@busco en la carpeta con rglob

ruta_json = config.ruta_json

diccionario = {}

def analizar_shader(ruta_shader:str): #la funcion de funciones.py
        IGNORADOS = {"u_screen_texture", "u_resolution", "u_time"}
        listaUniforms = []

        with open(ruta_shader, "r", encoding='utf-8') as archivo:
            for linea in archivo:
                linea_limpia = linea.strip()

                if not linea_limpia.startswith("uniform"): #Solo si es uniform
                    continue

                codigo, _, comentario = linea_limpia.partition("//") #A partir dl comentario lo que ponga
                partes = codigo.replace(";", "").split() #Lo separo y le quito el ;

                if len(partes) < 3: #solo si hay más de 3 cosas
                    continue

                tipo, nombre = partes[1], partes[2]
                if nombre in IGNORADOS: #solo si no es un ignoardo
                    continue

                info = {"nombre" : nombre, "tipo" : tipo, "min": 0.0, "max": 1.0, "default": 0.0} #meto valores por si no los hay basicos
                for token in comentario.split(): #Pillo los que puse si los hay
                    clave, _, valor = token.partition("=")
                    if clave in ("min", "max", "default"):
                        info[clave] = float(valor)

                if tipo == "int": #Lo convierto todo en ints claramente
                    info["min"], info["max"], info["default"] = (
                    int(info["min"]), int(info["max"]), int(info["default"])
                )

                listaUniforms.append(info) #y por fin lo meto todo
        
        return listaUniforms

for shader in rutas_archivos:
    diccionario_shader = {
        "ruta": str(shader),
        "uniforms": analizar_shader(shader)
    }

    diccionario.update({shader.name: diccionario_shader})


print(diccionario)

with open(ruta_json, "w") as archivo_json: #abro y la "w" pa escribir
    json.dump(diccionario, archivo_json, indent= 4)