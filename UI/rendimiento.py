from PySide6.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QProgressBar
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtNetwork import QUdpSocket, QHostAddress

import capturer

import GPUtil

tiempo_refresco = 1000 # ms

class VentanaRendimiento(QMainWindow):
    def __init__(self):
        super().__init__()

        ancho = 400
        alto = 400
        ancho_min = 400
        alto_min = 400

        self.resize(ancho, alto)
        self.setMinimumSize(ancho_min, alto_min)

        self.setWindowTitle("Performance")

        # Scroll
        self.scrollVert = QScrollArea()
        self.scrollVert.setWidgetResizable(True)

        # widget
        self.widget_rendimiento = WidgetRendimiento()
        self.setCentralWidget(self.scrollVert)

        # layouts principales
        self.layoutVert = QVBoxLayout()

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)

        #Temporizador
        self.temporizador = QTimer(self)
        self.temporizador.timeout.connect(self.al_actualizarse)
        self.temporizador.start(tiempo_refresco)

        #tiempos
        self.contenedor_tiempos = QWidget()
        self.layout_tiempos = QVBoxLayout(self.contenedor_tiempos)
        self.titulo_tiempos = QLabel("Time")
        self.label_tiempos = QLabel("Time will be displayed here")

        self.contenedor_tiempos.setMaximumHeight(100)

        self.layout_tiempos.addWidget(self.titulo_tiempos)
        self.layout_tiempos.addWidget(self.label_tiempos)

        #GPU
        self.contenedor_gpu = QWidget()
        self.layout_gpu = QVBoxLayout(self.contenedor_gpu)

        self.label_gpu = QLabel("GPU:")
        self.barra_gpu = QProgressBar()
        self.barra_gpu.setMinimum(0)
        self.label_temperatura_gpu = QLabel("GPU temperature: ")

        self.contenedor_gpu.setMaximumHeight(300)

        self.layout_gpu.addWidget(self.label_gpu)
        self.layout_gpu.addWidget(self.barra_gpu)
        self.layout_gpu.addWidget(self.label_temperatura_gpu)

        #VRAM
        self.contenedor_vram = QWidget()
        self.layout_vram = QVBoxLayout(self.contenedor_vram)

        self.barra_vram = QProgressBar()
        self.barra_vram.setMinimum(0)
        self.label_vram = QLabel("VRAM usage:")

        self.contenedor_vram.setMaximumHeight(200)

        self.layout_vram.addWidget(self.label_vram)
        self.layout_vram.addWidget(self.barra_vram)


        # Juntarlo todo
        self.layoutVert.addWidget(self.contenedor_tiempos)
        self.layoutVert.addWidget(self.contenedor_vram)
        self.layoutVert.addWidget(self.contenedor_gpu)

        self.widget_rendimiento.setLayout(self.layoutVert)

        self.scrollVert.setWidget(self.widget_rendimiento)

        # receptor udp 
        self.socket_receptor = QUdpSocket(self)
        self.socket_receptor.bind(QHostAddress.LocalHost, 9999) #escucho en el puerto 9999
        self.socket_receptor.readyRead.connect(self.actualizar_tiempos)

    def al_actualizarse(self):
        print("actualizao")
        self.sacar_datos_gpu()

    def actualizar_tiempos(self):
        while self.socket_receptor.hasPendingDatagrams():
            datagrama = self.socket_receptor.receiveDatagram() #saco los datos
            datos_texto = datagrama.data().toStdString() #lo paso a string

            try:
                tiempo_cpu, tiempo_gpu, fps = datos_texto.split() #separo el string

                self.label_tiempos.setText(f"CPU: {tiempo_cpu}ms, GPU: {tiempo_gpu}ms, FPS: {fps}")

            except ValueError:
                pass

    def sacar_datos_gpu(self):
        self.gpu = GPUtil.getGPUs()

        if not self.gpu:
            return
        
        print(self.gpu[0])
        gpu = self.gpu[0] #La gpu principal

        porcentaje_de_gpu = gpu.load * 100
        print(porcentaje_de_gpu)

        vram_usado = gpu.memoryUsed #En mb
        vram_total = gpu.memoryTotal #en mb tambien

        temperatura_gpu = gpu.temperature

        print(vram_usado, vram_total)

        self.barra_vram.setMaximum(int(vram_total))
        self.barra_vram.setValue(int(vram_usado)) #en int

        self.barra_gpu.setValue(int(porcentaje_de_gpu))
        self.barra_gpu.setMaximum(100)
        self.label_temperatura_gpu.setText(f"GPU temperature: {temperatura_gpu}")

class WidgetRendimiento(QWidget):
    def __init__(self):
        super().__init__()

