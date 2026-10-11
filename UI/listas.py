from PySide6.QtWidgets import QSlider, QHBoxLayout, QWidget, QVBoxLayout, QListWidget, QMenu, QLabel, QListWidgetItem, QLayout, QDoubleSpinBox, QWidgetAction
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEvent
from PySide6.QtGui import QImageReader, QPainter, QLinearGradient, QColor, QPen, QAction

import config
import socket

class ListaPersonalizada(QListWidget):
    def __init__(self):
        super().__init__()

        self.viewport().installEventFilter(self) # pa interceptar el evento de pintar

    def eventFilter(self, objeto, evento):
        if objeto == self.viewport() and evento.type() == QEvent.Paint:
            resultado = super().eventFilter(objeto, evento) #se dibuja lo normal
            
            # Ahora pintamos de manera segura usando un pintor asociado al viewport
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.Antialiasing)

            degradado = QLinearGradient(0, 0, self.width(), self.height())
            degradado.setColorAt(0.0, QColor("#77ebce"))
            degradado.setColorAt(1.0, QColor("#d14dea"))

            grosor = 2
            pen = QPen(degradado, grosor)
            painter.setPen(pen)

            rectangulo = self.viewport().rect().adjusted(grosor // 2, grosor // 2, -(grosor // 2), -(grosor // 2))
            painter.drawRect(rectangulo)
            painter.end()
            
            return resultado
            
        return super().eventFilter(objeto, evento)


RESOLUCION_FLOAT = 1000 #Para el slider, simula decimales

def slider_cambiado(ventana, info, valor_slider):
    if info["tipo"] == "int":
        valor_real = valor_slider
    else:
        proporcion = valor_slider / RESOLUCION_FLOAT
        valor_real = info["min"] + proporcion * (info["max"] - info["min"])

    ventana.vistaPrevia.establecer_uniform(info["nombre"], valor_real)

    mensaje = f"{info['nombre']}:{info['tipo']}:{valor_real}"
    ventana.sock_uniforms.sendto(mensaje.encode("utf-8"), ("127.0.0.1", config.PUERTO_UNIFORMS)) # Lo mando al socket

def cambiar_factor_de_escala(ventana, nuevo_valor): # A MEJORAR: SI LO CAMBIAS MIENTRAS EJECUTAS, PETA.
        ventana.factor_escala = nuevo_valor

        ventana.vistaPrevia._recrear_render()
    
        #Loo mando al socket
        mensaje = f"factor_escala:float:{ventana.factor_escala}"
        ventana.sock_uniforms.sendto(mensaje.encode("utf-8"), ("127.0.0.1", config.PUERTO_UNIFORMS))
    
        print(f"nuevo valor de escala: {ventana.factor_escala}")