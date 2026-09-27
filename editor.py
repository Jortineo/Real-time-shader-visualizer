#UI
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QSlider, QHBoxLayout, QWidget, QVBoxLayout, QListWidget, QMenu, QLabel, QListWidgetItem
from PySide6.QtCore import Qt

import sys
import subprocess
import os

import config

from pathlib import Path

aplicacion = QApplication()

anchoMinimo = 800
altoMinimo = 600

class Ventana_base(QMainWindow):

    def __init__(self):
        super().__init__()

        self.mostrarCualidades = False

        self.setMinimumWidth(anchoMinimo)
        self.setMinimumHeight(altoMinimo)

        self.proceso_shader = None

        self.setWindowTitle("Visualizador de shaders")

        # ------- LAYOUT Y MENÚ -------

        layoutHoriz = QHBoxLayout()
        layoutDch = QVBoxLayout()
        self.layoutCualidades = QVBoxLayout()
        layoutIzq = QVBoxLayout()

        menu = self.menuBar()
        menu_archivos = menu.addMenu("Archivos")
        menu_ayuda = menu.addMenu("Ayuda")

        # ------- BOTONES Y WIDGETS -------

        self.botonEjecutar = QPushButton("Ejecutar")
        self.botonEjecutar.clicked.connect(self.ejecutar_shader)
        layoutIzq.addWidget(self.botonEjecutar)

        self.labelCentral = QLabel("Escuchimizar")

        self.listaShaders = QListWidget()
        self.listaShaders.addItems(self.buscar_shaders())
        layoutDch.addWidget(self.listaShaders)
        self.listaShaders.itemClicked.connect(self.itemListaClicao)

        self.panelCualidades = QWidget()

        # ------- CONTENEDOR Y PREPARAR LAYOUTS -------

        layoutHoriz.addLayout(layoutIzq)
        layoutHoriz.addWidget(self.labelCentral)
        layoutHoriz.addLayout(self.layoutCualidades)
        layoutHoriz.addLayout(layoutDch)
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
        self.listaUniforms = []

        with open(ruta_shader, "r", encoding='utf-8') as archivo:
            for linea in archivo:
                linea_limpia = linea.strip()

                if linea_limpia.startswith("uniform") and linea_limpia != "uniform sampler2D u_screen_texture;":
                    linea_sin_punto_y_coma = linea_limpia.replace(";", "")

                    partes = linea_sin_punto_y_coma.split()

                    nombreUniform = partes[2]

                    self.listaUniforms.append(nombreUniform)
        
        return self.listaUniforms

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
        if self.mostrarCualidades == True:
            while self.layoutCualidades.count():
                hijo = self.layoutCualidades.takeAt(0)
                if hijo.widget():
                    hijo.widget().deleteLater()

        self.mostrarCualidades = True

        lista = self.analizar_shader(item.text())

        for uniform in lista:
            etiqueta = QLabel(uniform)

            slider = QSlider(Qt.Horizontal)
            slider.setObjectName(uniform)

            self.layoutCualidades.addWidget(etiqueta)
            self.layoutCualidades.addWidget(slider)
            print(f"añadido {slider.objectName()}")

        



ventana = Ventana_base()

ventana.show()
aplicacion.exec()