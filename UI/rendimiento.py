from PySide6.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Slot
from PySide6.QtNetwork import QUdpSocket, QHostAddress

import capturer


class VentanaRendimiento(QMainWindow):
    def __init__(self):
        super().__init__()

        ancho = 800
        alto = 800
        ancho_min = 400
        alto_min = 400

        self.resize(ancho, alto)
        self.setMinimumSize(ancho_min, alto_min)

        self.setWindowTitle("Performance")

        # widget
        self.widget_rendimiento = WidgetRendimiento()
        self.setCentralWidget(self.widget_rendimiento)

        # layouts principales
        self.layoutHoriz = QHBoxLayout()

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)

        #labels
        self.label_tiempos = QLabel("AAAA")

        self.layoutHoriz.addWidget(self.label_tiempos)
        self.widget_rendimiento.setLayout(self.layoutHoriz)

        # receptor udp 
        self.socket_receptor = QUdpSocket(self)
        self.socket_receptor.bind(QHostAddress.LocalHost, 9999) #escucho en el puerto 9999
        self.socket_receptor.readyRead.connect(self.actualizar_tiempos)

    def actualizar_tiempos(self):
        while self.socket_receptor.hasPendingDatagrams():
            datagrama = self.socket_receptor.receiveDatagram() #saco los datos
            datos_texto = datagrama.data().toStdString() #lo paso a string

            try:
                tiempo_cpu, tiempo_gpu, fps = datos_texto.split() #separo el string

                self.label_tiempos.setText(f"CPU: {tiempo_cpu}, GPU: {tiempo_gpu}, FPS: {fps}")

            except ValueError:
                pass


class WidgetRendimiento(QWidget):
    def __init__(self):
        super().__init__()

