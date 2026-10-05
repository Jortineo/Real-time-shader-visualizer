Actualizaciones:
  05/10/26:
    - Añadido el botón de detener el proceso que irónicamente no estaba aún.
    - Añadidos issues en github, para apuntar las ideas futuras que tenía guardadas en otro software.

  04/10/26:
    - Mejorada la UI añadiendo una styleSheet con PySide6. Cambiados los colores y la fuente del proyecto.
    - Ahora el tamaño del widget de la foto central se ajusta a la foto sin deformarla.
    - Ahora los widgets como la lista de shaders y la de las cualidades de los shaders tienen un tamaño máximo.

  03/10/26:
    - Añadida una vista previa con una imagen en al que se pone el efecto del shader seleccionado
    - Los sliders ya funcionan, tanto en la vista previa como en el efecto final (Nota: para que se actualize el efecto final, por ahora hay que modificarl los sldiers una vez ya esté siendo ejecutado, no antes)

  27/09/26:
    - Ahora el shader pasa por 2 draw passes, el segundo se encarga de downsamplearlo para mejorar el rendimiento.
    - Vuelta a usar el sistema síncrono de dxcam para mejor rendimiento de la cpu.
    - Añadido un FSR para mejorar la calidad del reescalado. Necesita más trabajo y mejor implementación.

  versión 0.1(Lanzamiento):
    - Resuelto un problema que gastaba mucha CPU para cambiar el color de la pantalla de BGRA a RGBA. Ahora simplemente no ocurre ese cambio. BGRA es el formato nativo de Dxcam.
    - Mejorado el rendimiento de la CPU al usar Dxcam en lugar de Mss como hacía previamente.
    - Creada la GUI
