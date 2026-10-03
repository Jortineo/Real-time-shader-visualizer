#version 330

// Recibido desde tu VERTEX_SHADER de ModernGL
in vec2 v_texcoord;
out vec4 f_color;

// Uniform configurado por tu clase Renderizador
uniform sampler2D u_screen_texture;

// --- [NUEVO] UNIFORMS PARA PERSONALIZAR EL EFECTO ---
uniform float u_color_levels = 4.0;     // min=1.0 max=15.0 default=4.0
uniform float u_pixel_size = 1.0;       // min=1.0 max=20.0 default=1.0
uniform float u_dither_intensity = 1.0; // min=0.0 max=1.0 default=1.0

// Sintaxis explícita float[16] que ya te funcionaba perfectamente
const float bayerMatrix[16] = float[16](
     0.0 / 16.0,  8.0 / 16.0,  2.0 / 16.0, 10.0 / 16.0,
    12.0 / 16.0,  4.0 / 16.0, 14.0 / 16.0,  6.0 / 16.0,
     3.0 / 16.0, 11.0 / 16.0,  1.0 / 16.0,  9.0 / 16.0,
    15.0 / 16.0,  7.0 / 16.0, 13.0 / 16.0,  5.0 / 16.0
);

void main() {
    // CORRECCIÓN DE INVERSIÓN VERTICAL:
    vec2 flippedTexcoord = vec2(v_texcoord.x, 1.0 - v_texcoord.y);

    // Asegurar valores mínimos seguros para evitar crasheos por división por cero
    float levels = max(u_color_levels, 2.0);

    // Detectar el tamaño del búfer de captura automáticamente
    ivec2 texSize = textureSize(u_screen_texture, 0);
    vec2 screenResolution = vec2(float(texSize.x), float(texSize.y));

    // [NUEVO] Aplicamos pixelación usando el uniform u_pixel_size si es mayor que 1.0
    vec2 pixelatedCoord = flippedTexcoord;
    if (u_pixel_size > 1.05) {
        vec2 virtualResolution = screenResolution / u_pixel_size;
        pixelatedCoord = (floor(flippedTexcoord * virtualResolution) + 0.5) / virtualResolution;
    }

    // 1. Obtener el color original usando la coordenada (con o sin pixelación)
    vec4 originalColor = texture(u_screen_texture, pixelatedCoord);
    
    // 2. Obtener la posición del píxel basándonos en la coordenada calculada
    // (Usa pixelatedCoord para que el dithering se adapte al tamaño del píxel retro)
    int px = int(pixelatedCoord.x * screenResolution.x);
    int py = int(pixelatedCoord.y * screenResolution.y);
    
    // Operación módulo asegurada con enteros positivos
    int x = px % 4;
    int y = py % 4;
    
    // 3. Obtener el valor de dispersión de la matriz
    float threshold = bayerMatrix[y * 4 + x];
    
    // 4. Aplicar el dithering usando tus nuevos uniforms personalizados
    vec3 ditheredColor = originalColor.rgb + (vec3(threshold) - 0.5) * (u_dither_intensity / levels);
    
    // Evitamos valores negativos antes del floor clamping para que no colapse a negro puro
    ditheredColor = clamp(ditheredColor, 0.0, 1.0);
    
    // 5. Cuantización usando el uniform u_color_levels
    ditheredColor = floor(ditheredColor * levels) / levels;
    
    // Retornar color final convertido a formato BGRA exactamente como lo tenías tú
    f_color = vec4(ditheredColor.b, ditheredColor.g, ditheredColor.r, originalColor.a);
}
