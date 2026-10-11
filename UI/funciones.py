#funciones de analizar carpetas y cosas así
from pathlib import Path

import config
import subprocess
import sys
import os

def buscar_shaders():
        shaders = []

        ruta_shaders = Path(config.CARPETA_SHADERS)
        for archivo in ruta_shaders.glob('**/*.glsl'):
            shaders.append(str(archivo))

        return shaders

def buscar_imagenes():
        imagenes = []

        formatos = ["*.png", "*.jpg", "*.jpeg"]

        ruta_imagenes = Path(config.CARPETA_FOTOS)
        for extension in formatos:
            for archivo in ruta_imagenes.glob(f'**/{extension}'):
                imagenes.append(str(archivo))

        return imagenes

def analizar_shader(ruta_shader:str):
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

def ejecutar_shader(self):
        shaderActual = self.listaShaders.currentItem()

        if not shaderActual:
            print("Nah primero selecciona uno")
            return

        ruta_glsl = shaderActual.text()
        print(f"preparando para ejecutar {ruta_glsl}")

        ruta_base = os.path.dirname(os.path.abspath(config.__file__))
        ruta_main_real = os.path.join(ruta_base, "capturer.py")

        parar_shader(self)

        self.proceso_shader = subprocess.Popen([sys.executable, ruta_main_real, ruta_glsl])

def parar_shader(self):
    if self.proceso_shader is not None and self.proceso_shader.poll() is None:
        self.proceso_shader.terminate()
        self.proceso_shader = None
        print("Shader parao")