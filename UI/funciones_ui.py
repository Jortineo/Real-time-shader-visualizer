from PySide6.QtWidgets import QLabel, QSlider
from PySide6.QtCore import Qt

from UI import listas, funciones


class funcionesUI():
    def __init__(self):
        pass

    def itemListaClicao(ventana, item):
        ventana.shaderActual = item.text()
        print(ventana.shaderActual)
        ventana.vistaPrevia.cambiar_shader(ventana.shaderActual)

        
        while ventana.layoutCualidades.count():
            hijo = ventana.layoutCualidades.takeAt(0)
            if hijo.widget():
                hijo.widget().deleteLater()

        ventana.panelCualidades.show()

        for info in funciones.analizar_shader(item.text()):
            etiqueta = QLabel(info["nombre"])
            slider = QSlider(Qt.Horizontal)

            if info["tipo"] == "int":
                slider.setMinimum(info["min"])
                slider.setMaximum(info["max"])
                slider.setValue(info["default"])
            else: # si es float basicamente
                slider.setMinimum(0)
                slider.setMaximum(listas.RESOLUCION_FLOAT)
                proporcion = (info["default"] - info["min"]) / (info["max"] - info["min"]) #lo divido entre 1000 pq todos los sliders van por ints
                slider.setValue(round(proporcion * listas.RESOLUCION_FLOAT)) #                así es como si fuera por decimales

            slider.valueChanged.connect(lambda valor, info=info: listas.slider_cambiado(ventana, info, valor))

            ventana.layoutCualidades.addWidget(etiqueta)
            ventana.layoutCualidades.addWidget(slider)
            listas.slider_cambiado(ventana, info, slider.value()) #aplica el default