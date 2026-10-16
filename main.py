import UI
from PySide6.QtWidgets import QApplication

aplicacion = QApplication()

ventana = UI.Ventana_base()

ventana.show()
aplicacion.exec()