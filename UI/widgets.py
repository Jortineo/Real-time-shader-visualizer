from PySide6.QtWidgets import QPushButton

from UI import funciones

def ready(self):
    self.botonEjecutar = QPushButton("Execute real-time")
    self.botonEjecutar.clicked.connect(lambda checked=False: funciones.ejecutar_shader(self))

    self.botonDetener = QPushButton("Stop real-time")
    self.botonDetener.clicked.connect(lambda checked=False: funciones.parar_shader(self))

    botones = {
        "ejecutar": self.botonEjecutar,
        "detener": self.botonDetener
    }

    return botones