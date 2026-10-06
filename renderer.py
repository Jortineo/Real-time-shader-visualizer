import array
import numpy as np
import moderngl
import config

VERTEX_SHADER = """
#version 330
in vec2 in_vert;
out vec2 v_texcoord;

void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    v_texcoord = in_vert * 0.5 + 0.5;
}
"""

VERTICES = [
    -1.0, -1.0,   1.0, -1.0,  -1.0,  1.0,
    -1.0,  1.0,   1.0, -1.0,   1.0,  1.0,
]


class Pasada:
    def __init__(self, ctx, vbo, ruta_o_codigo_fragment, vertex_shader_codigo=VERTEX_SHADER, es_ruta=True):
        codigo = open(ruta_o_codigo_fragment).read() if es_ruta else ruta_o_codigo_fragment
        self.prog = ctx.program(vertex_shader=vertex_shader_codigo, fragment_shader=codigo)
        self.vao = ctx.vertex_array(self.prog, [(vbo, '2f', 'in_vert')])

    def ejecutar(self, destino, **uniforms):
        for nombre, valor in uniforms.items():
            if nombre in self.prog:
                self.prog[nombre] = valor
        destino.use()
        self.vao.render()

    def liberar(self):
        self.prog.release()
        self.vao.release()

class Renderizador:
    def __init__(self, ruta_fragment_shader, ancho, alto, factor_escala=1):
        self.ctx = moderngl.create_context()
        self.ancho = ancho
        self.alto = alto
        self.factor_escala = factor_escala
        self.ancho_bajo = max(1, ancho // factor_escala)
        self.alto_bajo = max(1, alto // factor_escala)

        self.ctx.viewport = (0, 0, ancho, alto)

        self.vbo = self.ctx.buffer(array.array('f', VERTICES))

        self.textura_entrada = self.ctx.texture((self.ancho_bajo, self.alto_bajo), 4) #esta es la captura de pantalla a baja resolucion, 4 canales
        self.textura_efecto = self.ctx.texture((self.ancho_bajo, self.alto_bajo), 4) #mismo tamaño para el efecto
        self.fbo_efecto = self.ctx.framebuffer(color_attachments=[self.textura_efecto]) #dimensiones completas

        # fsr
        self.textura_fsr = self.ctx.texture((self.ancho_bajo, self.alto_bajo), 4) #lo mismo pal fsr
        self.fbo_fsr = self.ctx.framebuffer(color_attachments=[self.textura_fsr])
        self.pasada_fsr = Pasada(
            self.ctx,
            self.vbo,
            config.ruta_FSR
        )

        self.pasada_salida = Pasada(
            self.ctx,
            self.vbo,
            config.ruta_salida
        )

        self.pasada_efecto = None
        self.cambiar_shader(ruta_fragment_shader)

    # ------------------------------------------------------------------

    def cambiar_shader(self, ruta_fragment_shader):
        #Compila or recompila el programa
        try:
            nueva_pasada = Pasada(
                self.ctx,
                self.vbo,
                ruta_fragment_shader
            )
        except Exception as e:
            print(f"error cargando el shader broder: {ruta_fragment_shader}: \n{e}")
            return False

        if self.pasada_efecto is not None:
            self.pasada_efecto.liberar()

        self.pasada_efecto = nueva_pasada
    # ------------------------------------------------------------------

    def renderizar(self, captura, tiempo, fbo_destino = None):
        if self.pasada_efecto is None:
            return

        # bajo la resolucion de la captura

        factor = self.factor_escala

        if factor > 1:
            captura = captura[::factor, ::factor]
            captura = captura[:self.alto_bajo, :self.ancho_bajo]
            captura = np.ascontiguousarray(captura)

        # guardo la captura en la textura de entrada
        
        self.textura_entrada.write(captura) #bastante directo creo yo

        self.textura_entrada.use(0) # la pongo en el 0

        # EJECUTO

        # Pase 1, efecto

        self.pasada_efecto.ejecutar(
            self.fbo_efecto,
            u_screen_texture=0, #uso la 0, es decir, la entrada
            u_resolution=(self.ancho_bajo, self.alto_bajo), #estos dos se ignoran si no los hay en el shader
            u_time = tiempo
        )

        # Pase 2, FSR

        self.textura_efecto.use(0)

        self.pasada_fsr.ejecutar(
            self.fbo_fsr,
            u_baja_res=0
        )

        #Pase 3, salida

        destino = fbo_destino if fbo_destino is not None else self.ctx.screen #saco el destino

        self.textura_fsr.use(0)

        self.pasada_salida.ejecutar(
            destino,
            u_screen_texture=0
        )
