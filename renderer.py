import array
import numpy as np
import moderngl

VERTEX_SHADER = """
#version 330
in vec2 in_vert;
out vec2 v_texcoord;

void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    v_texcoord = in_vert * 0.5 + 0.5;
}
"""

PASSTHROUGH_FRAGMENT = """
#version 330
uniform sampler2D u_baja_res; // Tu textura de origen (baja resolución)
in vec2 v_texcoord;
out vec4 f_color;

// Función matemática de AMD FSR para ponderar la luminancia
float FsrLuma(vec3 rgb) {
    return rgb.g * 0.5 + (rgb.r + rgb.b) * 0.25;
}

// Núcleo de interpolación adaptativo oficial de AMD FSR (Aproximación Lanczos2)
void FsrEasuTap(
    inout vec3 accumColor, 
    inout float accumWeight, 
    vec2 pos, vec2 off, 
    vec2 dir, vec2 stretch, 
    float lob, float clp, vec2 texel
) {
    // Proyectar el offset en la dirección del gradiente del borde
    vec2 v = vec2(dot(off, dir), dot(off, vec2(-dir.y, dir.x))) * stretch;
    float d2 = dot(v, v);
    
    if (d2 < clp) {
        // Forzamos un muestreo limpio simulando Nearest en coordenadas continuas
        vec2 sampleUV = (pos + off) * texel;
        vec3 rgb = texture(u_baja_res, sampleUV).rgb;
        
        // Ventana matemática polinómica de FSR para evitar artefactos (ringing)
        float wX = d2 * lob + 1.0;
        float wY = d2 * 2.0 + 1.0;
        float w = (wX * wX) * wY;
        w = max(0.0, w);
        
        accumColor += rgb * w;
        accumWeight += w;
    }
}

void main() {
    // 1. Obtener la resolución del búfer de baja resolución automáticamente
    vec2 tex_size = vec2(textureSize(u_baja_res, 0));
    vec2 texel = 1.0 / tex_size;

    // 2. Encontrar la celda del píxel físico exacto en el espacio de origen
    vec2 pp = v_texcoord * tex_size - vec2(0.5);
    vec2 fp = floor(pp);
    vec2 pos = fp + vec2(0.5);

    // 3. Muestrear el vecindario nativo de 12 puntos requerido por EASU
    vec3 cA = texture(u_baja_res, (pos + vec2(-1.0, -1.0)) * texel).rgb;
    vec3 cB = texture(u_baja_res, (pos + vec2( 0.0, -1.0)) * texel).rgb;
    vec3 cC = texture(u_baja_res, (pos + vec2( 1.0, -1.0)) * texel).rgb;
    vec3 cD = texture(u_baja_res, (pos + vec2(-1.0,  0.0)) * texel).rgb;
    vec3 cE = texture(u_baja_res, (pos + vec2( 0.0,  0.0)) * texel).rgb;
    vec3 cF = texture(u_baja_res, (pos + vec2( 1.0,  0.0)) * texel).rgb;
    vec3 cG = texture(u_baja_res, (pos + vec2(-1.0,  1.0)) * texel).rgb;
    vec3 cH = texture(u_baja_res, (pos + vec2( 0.0,  1.0)) * texel).rgb;
    vec3 cI = texture(u_baja_res, (pos + vec2( 1.0,  1.0)) * texel).rgb;
    vec3 cJ = texture(u_baja_res, (pos + vec2( 0.0,  2.0)) * texel).rgb;
    vec3 cK = texture(u_baja_res, (pos + vec2(-1.0,  2.0)) * texel).rgb;
    vec3 cL = texture(u_baja_res, (pos + vec2( 1.0,  2.0)) * texel).rgb;

    // 4. Convertir muestras a luminancia para procesar gradientes
    float lA = FsrLuma(cA); float lB = FsrLuma(cB); float lC = FsrLuma(cC);
    float lD = FsrLuma(cD); float lE = FsrLuma(cE); float lF = FsrLuma(cF);
    float lG = FsrLuma(cG); float lH = FsrLuma(cH); float lI = FsrLuma(cI);
    float lJ = FsrLuma(cJ); float lK = FsrLuma(cK); float lL = FsrLuma(cL);

    // 5. Detectar la dirección del borde (Lógica de filtrado adaptativo AMD)
    float dc = lB - lE; float de = lD - lE; float df = lF - lE; float dh = lH - lE;
    vec2 dir = vec2(de + df, dc + dh);
    
    float dAC = lA - lE; float dCC = lC - lE; float dGC = lG - lE; float dIC = lI - lE;
    dir.x += (dAC + dCC + dGC + dIC) * 0.5;
    dir.y += (dAC - dCC - dGC + dIC) * 0.5;

    float len = length(dir);
    if (len > 0.0) {
        dir /= len;
    }

    // Calcular estiramiento y suavizado de ventana
    float edgeIntensity = clamp(len, 0.0, 1.0);
    vec2 stretch = vec2(1.0 + edgeIntensity, 1.0 - edgeIntensity * 0.5);
    float lob = 0.5 - 0.25 * edgeIntensity;
    float clp = 1.0 / (1.0 + lob);

    // 6. Acumular los 9 Taps espaciales aplicando el peso adaptativo FSR
    vec3 accumColor = vec3(0.0);
    float accumWeight = 0.0;

    FsrEasuTap(accumColor, accumWeight, pos, vec2(-1.0, -1.0), dir, stretch, lob, clp, texel);
    FsrEasuTap(accumColor, accumWeight, pos, vec2( 0.0, -1.0), dir, stretch, lob, clp, texel);
    FsrEasuTap(accumColor, accumWeight, pos, vec2( 1.0, -1.0), dir, stretch, lob, clp, texel);
    FsrEasuTap(accumColor, accumWeight, pos, vec2(-1.0,  0.0), dir, stretch, lob, clp, texel);
    FsrEasuTap(accumColor, accumWeight, pos, vec2( 0.0,  0.0), dir, stretch, lob, clp, texel);
    FsrEasuTap(accumColor, accumWeight, pos, vec2( 1.0,  0.0), dir, stretch, lob, clp, texel);
    FsrEasuTap(accumColor, accumWeight, pos, vec2(-1.0,  1.0), dir, stretch, lob, clp, texel);
    FsrEasuTap(accumColor, accumWeight, pos, vec2( 0.0,  1.0), dir, stretch, lob, clp, texel);
    FsrEasuTap(accumColor, accumWeight, pos, vec2( 1.0,  1.0), dir, stretch, lob, clp, texel);

    // 7. Salida con interpolación suavizada e inteligente de bordes
    vec3 final_rgb = accumColor / max(accumWeight, 0.0001);
    f_color = vec4(final_rgb, 1.0);
}
"""



VERTICES = [
    -1.0, -1.0,   1.0, -1.0,  -1.0,  1.0,
    -1.0,  1.0,   1.0, -1.0,   1.0,  1.0,
]


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

        # Programa principal: tu shader real, corre a baja resolución
        self.prog = None
        self.vao = None
        self.cambiar_shader(ruta_fragment_shader)

        # Programa de la 2ª pasada: solo estira la imagen ya procesada
        self.prog_upscale = self.ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=PASSTHROUGH_FRAGMENT,
        )
        self.vao_upscale = self.ctx.vertex_array(self.prog_upscale, [(self.vbo, '2f', 'in_vert')])

        # Textura de ENTRADA (la captura de pantalla), ya a baja resolución
        self.textura = self.ctx.texture((self.ancho_bajo, self.alto_bajo), 4)

        # Textura de SALIDA del shader real, con filtrado suave para cuando la estiremos
        self.textura_baja = self.ctx.texture((self.ancho_bajo, self.alto_bajo), 4)
        self.textura_baja.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.fbo_bajo = self.ctx.framebuffer(color_attachments=[self.textura_baja])

    # ------------------------------------------------------------------

    def cambiar_shader(self, ruta_fragment_shader):
        #Compila or recompila el programa
        try:
            with open(ruta_fragment_shader, "r") as archivo:
                codigo = archivo.read()
            nuevo_prog = self.ctx.program(
                vertex_shader=VERTEX_SHADER,
                fragment_shader=codigo,
            )
        except Exception as e:
            print(f"No se pudo cargar el shader '{ruta_fragment_shader}':\n{e}")
            return False

        if self.prog is not None:
            self.prog.release()
        if self.vao is not None:
            self.vao.release()

        self.prog = nuevo_prog
        self.vao = self.ctx.vertex_array(self.prog, [(self.vbo, '2f', 'in_vert')])
        return True

    #def _crear_textura(self):
        #self.textura = self.ctx.texture((self.ancho, self.alto), 4)

    # ------------------------------------------------------------------

    def renderizar(self, captura, tiempo):
        if self.prog is None:
            return

        factor = self.factor_escala
        if factor > 1:
            captura = captura[::factor, ::factor][:self.alto_bajo, :self.ancho_bajo]
            captura = np.ascontiguousarray(captura)

        if "u_resolution" in self.prog:
            self.prog["u_resolution"] = (self.ancho_bajo, self.alto_bajo)
        if "u_time" in self.prog:
            self.prog["u_time"] = tiempo

        self.textura.write(captura)
        self.textura.use(0)
        if "u_screen_texture" in self.prog:
            self.prog["u_screen_texture"] = 0

        # --- Pasada 1: tu shader real, dentro del framebuffer pequeño ---
        self.fbo_bajo.use()
        self.ctx.clear()
        self.vao.render()

        # --- Pasada 2: estiramos el resultado a toda la ventana ---
        self.ctx.screen.use()
        self.ctx.clear()
        self.textura_baja.use(0)
        self.prog_upscale["u_baja_res"] = 0
        self.vao_upscale.render()
