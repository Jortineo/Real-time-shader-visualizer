Un visualizador de shaders en tiempo real para ponerle filtros a la pantalla.

Utiliza Dxcam para capturar la pantalla mediante la CPU, y la envía con Ctypes a un código que utiliza ModernGl para aplicarle el shader seleccionado. Además cuenta con una GUI hecha con PySide6.

Cuenta con una carpeta de shaders por defecto con varios efectos.

Notas sobre los shaders:
 - Todos deben utilizar el formato de color nativo de dxcam: BGRA
 - Todos deben declarar explícitamente como comentario los valores mínimos, máximos, y por defecto del shader, Ejemplo: // min=1.0 max=2.0 default=1.5
 - Las variables de u_screen_texture, u_time y similares se saltan automáticamente.

Licencia: Este proyecto se publica de forma abierta para su visualización y aprendizaje como un proyecto personal. Actualmente no cuenta con una licencia de uso libre, por lo que todos los derechos están reservados. No está permitida la copia, redistribución ni explotación comercial del código sin mi autorización. Si el proyecto crece, ¡se evaluará abrirlo a la comunidad bajo una licencia formal!
