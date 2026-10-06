import os



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CARPETA_FOTOS = os.path.join(BASE_DIR, "Imágenes")
ruta_foto = os.path.join(CARPETA_FOTOS, "Calle.jpg")

CARPETA_SHADERS = os.path.join(BASE_DIR, "Shaders")
ruta_shader = os.path.join(CARPETA_SHADERS, "Dithering.glsl")

CARPETA_VERTEX = os.path.join(BASE_DIR, "Vertex shaders")
ruta_FSR = os.path.join(CARPETA_VERTEX, "FSR.glsl")
ruta_salida = os.path.join(CARPETA_VERTEX, "Salida.glsl")

PUERTO_UNIFORMS = 50123
 
FPS = 60
 
# Flag de SetWindowDisplayAffinity para excluir la ventana de las capturas.
WDA_EXCLUDEFROMCAPTURE = 0x00000011