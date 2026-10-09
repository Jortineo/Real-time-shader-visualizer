from PySide6.QtOpenGLWidgets import QOpenGLWidget
import numpy as np
from renderer import Renderizador
from PIL import Image
import config

class VistaPrevia(QOpenGLWidget):
    def __init__(self, ruta_shader_inicial, ruta_imagen, parent=None, editor = None):
        super().__init__(parent)
        self.ruta_shader = ruta_shader_inicial
        self.ruta_imagen = ruta_imagen
        self.render = None
        self.ruta_shader_pendiente = None

        self.editor = editor

        ancho, alto = Image.open(ruta_imagen).size
        self.setFixedSize(ancho, alto)

        self.valores_pendientes = {}

    def establecer_uniform(self, nombre, valor): #Actualizo la lista de cambios pendientes
        self.valores_pendientes[nombre] = valor
        self.update()

    def initializeGL(self):
        ancho, alto = self.width(), self.height()
        print(f"initializeGL: creando Renderizador a {ancho}x{alto}")

        factor = self.editor.factor_escala if self.editor else  1 #Si hay editor uso su factor y si no 1

        self.render = Renderizador(self.ruta_shader, ancho, alto, factor_escala=factor, editor_ui=self.editor)

    def paintGL(self):
        if self.render is None:
            return
        
        if self.ruta_shader_pendiente is not None:
            self.render.cambiar_shader(self.ruta_shader_pendiente)
            self.ruta_shader_pendiente = None

        for nombre, valor in self.valores_pendientes.items(): # Añado el cambio de uniform
            if nombre in self.render.pasada_efecto.prog:
                self.render.pasada_efecto.prog[nombre] = valor #Necesario pq si cambio de shader ya no sería lo mismo y pasaría algo raro
        self.valores_pendientes.clear() #Lo limpio

        #if not hasattr(self, "imagen"):
        img = Image.open(config.ruta_foto).convert("RGBA")
        datos = np.array(img, dtype=np.uint8) #fuerzo a usar 8 bits
        datos = np.array(img)
        datos = datos[..., [2, 1, 0, 3]]
        self.imagen = np.ascontiguousarray(datos)

        fbo_qt = self.render.ctx.detect_framebuffer()
        self.render.renderizar(self.imagen, 0.0, fbo_destino=fbo_qt)

    def cambiar_shader(self, ruta):
            self.ruta_shader_pendiente = ruta
            self.update()