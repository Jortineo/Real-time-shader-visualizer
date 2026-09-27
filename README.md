Un visualizador de shaders en tiempo real para ponerle filtros a la pantalla.

Utiliza Dxcam para capturar la pantalla mediante la CPU, y la envía con Ctypes a un código que utiliza ModernGl para aplicarle el shader seleccionado. Además cuenta con una GUI hecha con PySide6.

Cuenta con una carpeta de shaders por defecto con varios efectos. Nota: Los shaders utilizan los colores BGRA.

A añadir en el futuro:
- Pestaña de postprocesado con módulos para seleccionar diferentes efectos (Corrección de color, filtrado anisotrópico...) [Hacer que los efectos seleccionados se ejecuten de arriba a abajo para poder controlarlo al máximo]
- Optimizar el rendimiento lo máximo posible.
- La posibilidad de editar los shaders en la interfaz y verlos en tiempo real sobre una imagen.

Actualizaciones:
  27/09/26:
    - Ahora el shader pasa por 2 draw passes, el segundo se encarga de downsamplearlo para mejorar el rendimiento.
    - Vuelta a usar el sistema síncrono de dxcam para mejor rendimiento de la cpu.
    - Añadido un FSR para mejorar la calidad del reescalado. Necesita más trabajo y mejor implementación.

  versión 0.1(Lanzamiento):
    - Resuelto un problema que gastaba mucha CPU para cambiar el color de la pantalla de BGRA a RGBA. Ahora simplemente no ocurre ese cambio. BGRA es el formato nativo de Dxcam.
    - Mejorado el rendimiento de la CPU al usar Dxcam en lugar de Mss como hacía previamente.
    - Creada la GUI

Licencia: Este proyecto se publica de forma abierta para su visualización y aprendizaje como un proyecto personal. Actualmente no cuenta con una licencia de uso libre, por lo que todos los derechos están reservados. No está permitida la copia, redistribución ni explotación comercial del código sin mi autorización. Si el proyecto crece, ¡se evaluará abrirlo a la comunidad bajo una licencia formal!
