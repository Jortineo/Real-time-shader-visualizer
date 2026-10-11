#Aqui lo junto todo
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QVBoxLayout

import socket

import config
from UI import funciones, listas, widgets, funciones_ui, menuSuperior

from vista_previa import VistaPrevia

anchoMinimo = 800
altoMinimo = 600

class Ventana_base(QMainWindow):
    def __init__(self):
        super().__init__()
        # Variables de configuración
        self.factor_escala = 2
        self.proceso_shader = None

        # Estilo ----- Colores(+ a -oscuro):  #030303, #1c1621, #353535, #545454, #737373, #959595, #b9b9b9, #dedede
        self.setStyleSheet(""" 
        * {font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 12px; }

        QMainWindow { background-color: #1c1621; }

        QPushButton { background-color: #1c1621; color: #c9c9ca; border-radius: 5px; padding: 5px; }
        QPushButton:hover { background-color: #1c1621; color: #c9c9ca; border: 1px solid #d5c382 }
        QPushButton:pressed { background-color: #1c1621; border: 1px solid #77ebce}

        QListWidget { background-color: #1c1621; color: #c9c9ca; border-radius: 8px; outline: none }
        QListWidget::item {padding: 4px 12px}
        QListWidget::item:hover { color: #d5c382;}
        QListWidget::item:selected { color: #77ebce; border-radius: 4px; border-left: 3px solid #d5c382;}

        QSlider::groove:horizontal { height: 5px; background-color: #545454; border-radius: 2px; margin: 0px 4 px;}
        QSlider::handle:horizontal { background-color: #c9c9ca; border: 3px solid #545454; height: 10px; width: 12px; margin: -4px 0px; border-radius: 6px;}
        QSlider::sub-page:horizontal { background-color: #c9c9ca; border-radius: 2px}

        QMenuBar {background-color: #1c1621; margin: 0px 4px;}
        QMenuBar::item:hover {background-color: #545454; border-radius: 12px;}
        QMenuBar::item:selected {background-color: #737373; border-radius: 12px;}
        """)

        self.sock_uniforms = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Para el socket de los valores en tiempo real

        self.setMinimumWidth(anchoMinimo)
        self.setMinimumHeight(altoMinimo)

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

        # Layout de las cualidades
        self.panelCualidades = QWidget()
        self.layoutCualidades = QVBoxLayout()
        self.panelCualidades.setLayout(self.layoutCualidades) #Meto el panel en el hbox y no el layout
        self.panelCualidades.hide() #Lo escondo
        self.panelCualidades.setMinimumWidth(300)
        self.panelCualidades.setMaximumWidth(400)

        # ------- BOTONES Y WIDGETS -------
        self.botones = widgets.ready(self)

        menuSuperior.ready(self)

        self.botonEjecutar = self.botones["ejecutar"]
        layoutIzq.addWidget(self.botonEjecutar)

        self.botonDetener = self.botones["detener"]
        layoutIzq.addWidget(self.botonDetener)

        self.ruta_foto = config.ruta_foto
        self.vistaPrevia = VistaPrevia(config.ruta_shader, self.ruta_foto, editor=self)
        self.vistaPrevia.setStyleSheet("""
            border: 1px solid #333;
            border-radius: 8px;
            background-color: #121212;
        """)

        self.listaShaders = listas.ListaPersonalizada()
        self.listaShaders.addItems(funciones.buscar_shaders())
        layoutDch.addWidget(self.listaShaders)
        self.listaShaders.itemClicked.connect(lambda item: funciones_ui.funcionesUI.itemListaClicao(self, item)) #paso ventana e item

        # ------- CONTENEDOR Y PREPARAR LAYOUTS -------

        layoutHoriz.addLayout(layoutIzq)
        layoutHoriz.addWidget(self.vistaPrevia)
        layoutHoriz.addWidget(self.panelCualidades)
        layoutHoriz.addWidget(panelDch)

        contenedor = QWidget()
        contenedor.setLayout(layoutHoriz)


        self.setCentralWidget(contenedor)

    def closeEvent(self, evento): # pa cerrar
        funciones.parar_shader(self)
        evento.accept()
