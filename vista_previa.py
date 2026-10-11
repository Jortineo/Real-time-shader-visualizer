from PySide6.QtOpenGLWidgets import QOpenGLWidget
import numpy as np
from renderer import Renderizador
from PIL import Image

ANCHO_MAX, ALTO_MAX = 800, 600

class VistaPrevia(QOpenGLWidget):
    def __init__(self, ruta_shader_inicial, ruta_imagen, parent=None, editor = None):
        super().__init__(parent)
        self.ruta_shader = ruta_shader_inicial
        self.ruta_imagen = ruta_imagen
        self.render = None
        self.ruta_shader_pendiente = None

        self.editor = editor

        self.recrear_pendiente = False
        self.valores = {}
        self._preparar_imagen()

        self.valores_pendientes = {}

    def _preparar_imagen(self): # la preparo fuera del paintgl
        with Image.open(self.ruta_imagen) as original:
            ancho, alto = original.size
            escala = min(ANCHO_MAX / ancho, ALTO_MAX / alto, 1.0)
            ancho, alto = int(ancho * escala), int(alto * escala)
            img = original.convert("RGBA").resize((ancho, alto))
        self.imagen = np.ascontiguousarray(np.array(img)[..., [2, 1, 0, 3]]) # a BGRA
        self.setFixedSize(ancho, alto)

    def _crear_render(self):
        alto, ancho = self.imagen.shape[:2]
        factor = self.editor.factor_escala if self.editor else  1
        self.render = Renderizador(self.ruta_shader, ancho, alto, factor_escala=factor, editor_ui=self.editor)
        self.valores_pendientes.update(self.valores) #vuevle a aplicar los shaders

    def _recrear_render(self):
        self.recrear_pendiente = True
        self.update()

    def establecer_uniform(self, nombre, valor): #Actualizo la lista de cambios pendientes
        self.valores[nombre] = valor
        self.valores_pendientes[nombre] = valor
        self.update()

    def initializeGL(self):
        self._crear_render() #simplemente lo crea

    def paintGL(self):
        if self.recrear_pendiente:
            self._crear_render()
            self.recrear_pendiente = False
        
        if self.render is None:
            return
        
        if self.ruta_shader_pendiente is not None:
            self.ruta_shader = self.ruta_shader_pendiente
            self.render.cambiar_shader(self.ruta_shader_pendiente)
            self.ruta_shader_pendiente = None

        for nombre, valor in self.valores_pendientes.items(): # Añado el cambio de uniform
            if nombre in self.render.pasada_efecto.prog:
                self.render.pasada_efecto.prog[nombre] = valor #Necesario pq si cambio de shader ya no sería lo mismo y pasaría algo raro
        self.valores_pendientes.clear() #Lo limpio

        fbo_qt = self.render.ctx.detect_framebuffer()
        self.render.renderizar(self.imagen, 0.0, fbo_destino=fbo_qt)

    def cambiar_shader(self, ruta):
        self.ruta_shader_pendiente = ruta
        self.update()

    def cambiar_foto(self, foto):
        self.ruta_imagen = foto

        self.recrear_pendiente = True

        self._preparar_imagen()

        self.update()