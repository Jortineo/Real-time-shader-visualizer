import array
import numpy as np
import moderngl
import config
from PIL import Image
from os import path
from texturas import crear_atlas_font


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
    def __init__(self, ruta_fragment_shader, ancho, alto, factor_escala=1, editor_ui=None):
        self.ctx = moderngl.create_context()
        self.ancho = ancho
        self.alto = alto
        self.ancho_bajo = max(1, int(ancho / factor_escala))
        self.alto_bajo = max(1, int(alto / factor_escala))

        self.idx_x = np.minimum((np.arange(self.ancho_bajo) * factor_escala).astype(int), ancho - 1) #Saco los decimales que quiero
        self.idx_y = np.minimum((np.arange(self.alto_bajo) * factor_escala).astype(int), alto - 1)

        self.editor = editor_ui
        self.factor_escala = factor_escala

        self.ctx.viewport = (0, 0, ancho, alto)

        self.vbo = self.ctx.buffer(array.array('f', VERTICES))

        self.textura_entrada = self.ctx.texture((self.ancho_bajo, self.alto_bajo), 4) #esta es la captura de pantalla a baja resolucion, 4 canales
        self.textura_efecto = self.ctx.texture((self.ancho_bajo, self.alto_bajo), 4) #mismo tamaño para el efecto
        self.fbo_efecto = self.ctx.framebuffer(color_attachments=[self.textura_efecto]) #dimensiones completas

        # fsr
        self.textura_fsr = self.ctx.texture((self.ancho, self.alto), 4) #lo mismo pal fsr
        self.fbo_fsr = self.ctx.framebuffer(color_attachments=[self.textura_fsr])
        self.pasada_fsr = Pasada(
            self.ctx,
            self.vbo,
            config.ruta_FSR
        )

        self.textura_anti_alias = self.ctx.texture((self.ancho, self.alto), 4)
        self.fbo_anti_alias = self.ctx.framebuffer(color_attachments=[self.textura_anti_alias])
        self.pasada_anti_alias = Pasada(
            self.ctx,
            self.vbo,
            config.ruta_anti_alias
        )

        self.pasada_salida = Pasada(
            self.ctx,
            self.vbo,
            config.ruta_salida
        )

        self.cache_texturas = {}

        self.pasada_efecto = None
        self.cambiar_shader(ruta_fragment_shader)

    def cambiar_factor(self, factor): #Pa cambiar el factor
        self.factor_escala = factor
        self.ancho_bajo = max(1, int(self.ancho / factor))
        self.alto_bajo = max(1, int(self.alto / factor))
        self.idx_x = np.minimum((np.arange(self.ancho_bajo) * factor).astype(int), self.ancho - 1)
        self.idx_y = np.minimum((np.arange(self.alto_bajo) * factor).astype(int), self.alto - 1)

        for recurso in (self.fbo_efecto, self.textura_entrada, self.textura_efecto):
            recurso.release()
        self.textura_entrada = self.ctx.texture((self.ancho_bajo, self.alto_bajo), 4)
        self.textura_efecto = self.ctx.texture((self.ancho_bajo, self.alto_bajo), 4)
        self.fbo_efecto = self.ctx.framebuffer(color_attachments=[self.textura_efecto])
    # ------------------------------------------------------------------

    def _texturas_del_shader(self):
        prog = self.pasada_efecto.prog

        for nombre, ruta in config.texturas_extra.items(): #cada textura en config
            if nombre in prog: #si no lo usa, se descarta solo
                if nombre not in self.cache_texturas:
                    self.cache_texturas[nombre] = crear_atlas_font(
                        self.ctx, ruta, config.caracteres_ascii
                    )
                yield nombre, self.cache_texturas[nombre]

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

        #Actualizo TODO
        if self.editor is not None and self.factor_escala != self.editor.factor_escala:
            self.cambiar_factor(self.editor.factor_escala) #esto recalcula tamaños y todo
        # bajo la resolucion de la captura

        factor = self.factor_escala

        if factor > 1:
            captura = captura[np.ix_(self.idx_y, self.idx_x)] #ix_ combina los dos indices

        # guardo la captura en la textura de entrada
        
        self.textura_entrada.write(captura) #bastante directo creo yo

        self.textura_entrada.use(0) # la pongo en el 0

        # EJECUTO
        extras = {}
        for unidad, (nombre, tex) in enumerate(self._texturas_del_shader(), start=1):
            tex.use(unidad) #la 0 es la captura
            extras[nombre] = unidad #paso el número, NO la textura

        # Pase 1, efecto
        self.pasada_efecto.ejecutar(
            self.fbo_efecto,
            u_screen_texture=0, #uso la 0, es decir, la entrada
            u_resolution=(self.ancho_bajo, self.alto_bajo), #estos dos se ignoran si no los hay en el shader
            u_time = tiempo,
            **extras #extras también
        )

        # Pase 2, FSR

        self.textura_efecto.use(0)

        self.pasada_fsr.ejecutar(
            self.fbo_fsr,
            u_baja_res=0
        )

        # Pase 3, AA

        self.textura_fsr.use(0)

        self.pasada_anti_alias.ejecutar(
            self.fbo_anti_alias,
            u_resolution=(self.ancho, self.alto),
            u_screen_texture=0
        )

        #Pase 4, salida

        destino = fbo_destino if fbo_destino is not None else self.ctx.screen #saco el destino

        self.textura_anti_alias.use(0)

        self.pasada_salida.ejecutar(
            destino,
            u_screen_texture=0
        )
