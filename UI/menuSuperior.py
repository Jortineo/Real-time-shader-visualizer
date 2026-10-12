from PySide6.QtWidgets import QDoubleSpinBox, QWidgetAction, QLabel, QMenu, QPushButton
from PySide6.QtGui import QAction

from UI import listas, funciones, rendimiento


def ready(ventana):
    menu = ventana.menuBar()
    menu_archivos = menu.addMenu("File")
    menu_ayuda = menu.addMenu("Help")
    menu_opciones = menu.addMenu("Options")
    menu_rendimiento = menu.addMenu("Performance")

    # ------- APARTADOS DEL MENU -------
    # factor
    ventana.input_factor = QDoubleSpinBox()
    ventana.input_factor.setRange(1.0, 4.0)
    ventana.input_factor.setValue(ventana.factor_escala)
    ventana.input_factor.setSingleStep(0.5)
    ventana.input_factor.setDecimals(1)
    ventana.input_factor.valueChanged.connect(lambda valor: listas.cambiar_factor_de_escala(ventana, valor))
    acc_input = QWidgetAction(ventana)
    acc_input.setDefaultWidget(ventana.input_factor)
    ventana.label_input = QLabel("Resolution scaling")
    acc_label_factor = QWidgetAction(ventana)
    acc_label_factor.setDefaultWidget(ventana.label_input)

    menu_opciones.addAction(acc_label_factor)
    menu_opciones.addAction(acc_input)

    #menu rendimiento
    acc_boton_rendimiento = menu_rendimiento.addAction("See performance")
    acc_boton_rendimiento.triggered.connect(funciones.ejecutar_rendimiento)

    # cambiar imagen
    ventana.menu_imagenes = QMenu("Change image", ventana)

    rutas_fotos = funciones.buscar_imagenes()
    acciones_imagenes = []

    for r in rutas_fotos:
        accion = QAction(r, ventana)

        accion.triggered.connect(lambda checked=False, ruta=r: ventana.vistaPrevia.cambiar_foto(ruta)) #conecto con lambda pa pasar la ruta

        acciones_imagenes.append(accion)

    ventana.menu_imagenes.addActions(acciones_imagenes)

    menu_opciones.addMenu(ventana.menu_imagenes)