#UI
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QSlider, QHBoxLayout, QWidget, QVBoxLayout, QListWidget, QMenu, QLabel, QListWidgetItem, QLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImageReader

import sys
import subprocess
import os
import socket

import config

from pathlib import Path

from vista_previa import VistaPrevia

aplicacion = QApplication()

anchoMinimo = 800
altoMinimo = 600

class Ventana_base(QMainWindow):

    def __init__(self):
        super().__init__()

        # Estilo ----- Colores(+ a -oscuro):  #030303, #121212, #353535, #545454, #737373, #959595, #b9b9b9, #dedede
        self.setStyleSheet(""" 
        * {font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 12px; letter-spacing: -1px;}

        QMainWindow { background-color: #121212; }

        QPushButton { background-color: #353535; color: #dedede; border-radius: 5px; padding: 5px; }
        QPushButton:hover { background-color: #737373; color: #dedede; }
        QPushButton:pressed { background-color: #959595}

        QListWidget { background-color: #121212; color: #dedede; border: 1px solid #333; border-radius: 8px; outline: none }
        QListWidget::item {padding: 4px 12px}
        QListWidget::item:hover { background-color: #353535; border-radius: 8px; }
        QListWidget::item:selected {background-color: #737373; color: #dedede; border-radius: 8px; border-left: 3px solid #dedede;}

        QSlider::groove:horizontal { height: 5px; background-color: #545454; border-radius: 2px; margin: 0px 4 px;}
        QSlider::handle:horizontal { background-color: #dedede; border: 3px solid #545454; height: 10px; width: 12px; margin: -4px 0px; border-radius: 6px;}
        QSlider::sub-page:horizontal { background-color: #dedede; border-radius: 2px}

        QMenuBar {background-color: #121212; margin: 0px 4px;}
        QMenuBar::item:hover {background-color: #545454; border-radius: 12px;}
        QMenuBar::item:selected {background-color: #737373; border-radius: 12px;}
        """)

        self.sock_uniforms = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Para el socket de los valores en tiempo real

        self.RESOLUCION_FLOAT = 1000 #Para el slider, simula decimales

        self.mostrarCualidades = False

        self.setMinimumWidth(anchoMinimo)
        self.setMinimumHeight(altoMinimo)

        self.shaderActual : str = config.ruta_shader

        self.proceso_shader = None

        self.setWindowTitle("Visualizador de shaders")

        # ------- LAYOUT Y MENÚ -------
        layoutHoriz = QHBoxLayout()

        # Layout de la lsita de shaders
        panelDch = QWidget()
        layoutDch = QVBoxLayout()
        panelDch.setLayout(layoutDch)
        panelDch.setMinimumWidth(300) # tamaño
        panelDch.setMaximumWidth(600)

        layoutIzq = QVBoxLayout()

        menu = self.menuBar()
        menu_archivos = menu.addMenu("Archivos")
        menu_ayuda = menu.addMenu("Ayuda")

        # Layout de las cualidades
        self.panelCualidades = QWidget()
        self.layoutCualidades = QVBoxLayout()
        self.panelCualidades.setLayout(self.layoutCualidades) #Meto el panel en el hbox y no el layout
        self.panelCualidades.hide() #Lo escondo
        self.panelCualidades.setMinimumWidth(300)
        self.panelCualidades.setMaximumWidth(400)

        # ------- BOTONES Y WIDGETS -------

        self.botonEjecutar = QPushButton("Ejecutar")
        self.botonEjecutar.clicked.connect(self.ejecutar_shader)
        layoutIzq.addWidget(self.botonEjecutar)

        self.labelCentral = QLabel("Escuchimizar")

        self.vistaPrevia = VistaPrevia(config.ruta_shader, config.ruta_foto)
        sacar_tamaño = lambda r: QImageReader(r).size() #Saco el tamaño de la foto
        tamaño_maximo = QSize(800, 600) #Fijo un tamaño pa que no ocupe toda la pantalla
        tamaño_final = sacar_tamaño(config.ruta_foto).boundedTo(tamaño_maximo) #hago esto pa que no se deforme la foto y se ajuste bien
        self.vistaPrevia.setFixedSize(tamaño_final) #fijo el tamaño al de la foto
        self.vistaPrevia.setStyleSheet("""
            border: 1px solid #333;
            border-radius: 8px;
            background-color: #121212;
        """)

        self.listaShaders = QListWidget()
        self.listaShaders.addItems(self.buscar_shaders())
        layoutDch.addWidget(self.listaShaders)
        self.listaShaders.itemClicked.connect(self.itemListaClicao)

        # ------- CONTENEDOR Y PREPARAR LAYOUTS -------

        layoutHoriz.addLayout(layoutIzq)
        layoutHoriz.addWidget(self.labelCentral)
        layoutHoriz.addWidget(self.vistaPrevia)
        layoutHoriz.addWidget(self.panelCualidades)
        layoutHoriz.addWidget(panelDch)

        contenedor = QWidget()
        contenedor.setLayout(layoutHoriz)


        self.setCentralWidget(contenedor)

    def buscar_shaders(self):
        shaders = []

        ruta_shaders = Path(config.CARPETA_SHADERS)
        for archivo in ruta_shaders.glob('**/*.glsl'):
            shaders.append(str(archivo))

        return shaders

    def analizar_shader(self, ruta_shader:str):
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
        ruta_main_real = os.path.join(ruta_base, "main.py")

        if self.proceso_shader is not None and self.proceso_shader.poll() is None:
            self.proceso_shader.terminate()   # mata el anterior si seguía vivo

        self.proceso_shader = subprocess.Popen([sys.executable, ruta_main_real, ruta_glsl])

    def closeEvent(self, evento):
        if self.proceso_shader is not None and self.proceso_shader.poll() is None:
            self.proceso_shader.terminate()
        evento.accept()

    def itemListaClicao(self, item):
        self.shaderActual = item.text()
        print(self.shaderActual)
        self.vistaPrevia.cambiar_shader(self.shaderActual)

        if self.mostrarCualidades == True:
            while self.layoutCualidades.count():
                hijo = self.layoutCualidades.takeAt(0)
                if hijo.widget():
                    hijo.widget().deleteLater()

        self.mostrarCualidades = True
        self.panelCualidades.show()

        for info in self.analizar_shader(item.text()):
            etiqueta = QLabel(info["nombre"])
            slider = QSlider(Qt.Horizontal)

            if info["tipo"] == "int":
                slider.setMinimum(info["min"])
                slider.setMaximum(info["max"])
                slider.setValue(info["default"])
            else: # si es float basicamente
                slider.setMinimum(0)
                slider.setMaximum(self.RESOLUCION_FLOAT)
                proporcion = (info["default"] - info["min"]) / (info["max"] - info["min"]) #lo divido entre 1000 pq todos los sliders van por ints
                slider.setValue(round(proporcion * self.RESOLUCION_FLOAT)) #                así es como si fuera por decimales

            slider.valueChanged.connect(lambda valor, info=info: self.slider_cambiado(info, valor))

            self.layoutCualidades.addWidget(etiqueta)
            self.layoutCualidades.addWidget(slider)
            self.slider_cambiado(info, slider.value()) #aplica el default

    def slider_cambiado(self, info, valor_slider):
        if info["tipo"] == "int":
            valor_real = valor_slider
        else:
            proporcion = valor_slider / self.RESOLUCION_FLOAT
            valor_real = info["min"] + proporcion * (info["max"] - info["min"])

        self.vistaPrevia.establecer_uniform(info["nombre"], valor_real)

        mensaje = f"{info['nombre']}:{info['tipo']}:{valor_real}"
        self.sock_uniforms.sendto(mensaje.encode("utf-8"), ("127.0.0.1", config.PUERTO_UNIFORMS)) # Lo mando al socket




ventana = Ventana_base()

ventana.show()
aplicacion.exec()