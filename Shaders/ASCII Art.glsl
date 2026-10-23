#version 330

// Recibido desde tu VERTEX_SHADER de ModernGL
in vec2 v_texcoord;
out vec4 f_color;

// Uniform configurado por tu clase Renderizador
uniform sampler2D u_screen_texture;
uniform sampler2D u_font_atlas;

// --- [NUEVO] UNIFORMS PARA PERSONALIZAR EL EFECTO ASCII ---
uniform float u_font_size = 12.0;       // min=4.0 max=32.0 default=12.0
uniform float u_color_mode = 1.0;      // min=0.0 max=1.0 default=1.0
uniform float u_brightness_mod = 1.0;   // min=0.1 max=3.0 default=1.0

const float CELL_ASPECT = 1; //la relacion de aspecto



void main() {
    // CORRECCIÓN DE INVERSIÓN VERTICAL:
    vec2 flippedTexcoord = vec2(v_texcoord.x, 1.0 - v_texcoord.y);

    // Detectar el tamaño del búfer de captura automáticamente
    ivec2 texSize = textureSize(u_screen_texture, 0);
    vec2 screenResolution = vec2(float(texSize.x), float(texSize.y));

    // Determinar el tamaño de la celda de la fuente (mínimo seguro de 4 píxeles)
    float fontSize = max(u_font_size, 4.0);

    // 1. Pixelar las coordenadas para agrupar la pantalla en celdas de texto
    vec2 cellSize = vec2(fontSize * CELL_ASPECT, fontSize);
    vec2 virtualResolution = screenResolution / cellSize;
    vec2 cellCoord = floor(flippedTexcoord * virtualResolution) / virtualResolution;

    // 2. Obtener el color original muestreando el centro de la celda ASCII
    vec4 originalColor = texture(u_screen_texture, cellCoord + (0.5 / virtualResolution));

    // 4. Calcular el brillo (luminancia) de la celda y aplicar el modificador
    float brightness = dot(originalColor.rgb, vec3(0.2126, 0.7152, 0.0722));
    brightness = clamp(brightness * u_brightness_mod, 0.0, 1.0);

    // Manejo la font, saco ss caracteres, textura y tal
    ivec2 atlasSize = textureSize(u_font_atlas, 0);
    float nChars = float(atlasSize.x) / float(atlasSize.y) * CELL_ASPECT;
    float idx = min(floor(brightness * nChars), nChars - 1.0);

    vec2 local = fract(flippedTexcoord * virtualResolution);
    float glyph = texture(u_font_atlas, vec2((idx + local.x) / nChars, local.y)).r;

    // 7. Modos de color: 0.0 = Monocromo fósforo verde Matrix, 1.0 = Color original de pantalla
    vec3 greenPhosphor = vec3(0.0, 1.0, 0.2) * brightness;
    vec3 baseColor = mix(greenPhosphor, originalColor.rgb, clamp(u_color_mode, 0.0, 1.0));

    vec3 finalColor = baseColor * glyph;


    // Retornar color final convertido a formato BGRA para tu pipeline de ModernGL
    f_color = vec4(finalColor.b, finalColor.g, finalColor.r, originalColor.a);
}
