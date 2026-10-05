#version 330

// Recibido desde tu VERTEX_SHADER de ModernGL
in vec2 v_texcoord;
out vec4 f_color;

// Uniform configurado por tu clase Renderizador
uniform sampler2D u_screen_texture;

// --- [NUEVO] UNIFORMS PARA PERSONALIZAR EL EFECTO ASCII ---
uniform float u_font_size = 12.0;       // min=4.0 max=32.0 default=12.0
uniform float u_color_mode = 1.0;      // min=0.0 max=1.0 default=1.0
uniform float u_brightness_mod = 1.0;   // min=0.1 max=3.0 default=1.0

// Mapas de bits de 8x8 para caracteres ASCII reales ordenados por densidad de brillo:
// Contiene: [Espacio, Punto, Dos Puntos, I Latina, S, Cero, Letra A, Letra M, Bloque]
// Cada vec2 representa un entero de 64 bits (32 bits superiores y 32 inferiores)
const vec2 asciiCharacters[9] = vec2[9](
    vec2(0x00000000, 0x00000000), // ' ' Espacio
    vec2(0x00000000, 0x00181800), // '.' Punto
    vec2(0x00181800, 0x00181800), // ':' Dos puntos
    vec2(0x003c1818, 0x1818183c), // 'I' I latina
    vec2(0x003e603c, 0x0606623c), // 'S' S
    vec2(0x003c6666, 0x6e76663c), // '0' Cero
    vec2(0x001c3666, 0x7e666666), // 'A' Letra A
    vec2(0x0063777f, 0x6b636363), // 'M' Letra M
    vec2(0xffffffff, 0xffffffff)  // '█' Bloque sólido
);

// Función auxiliar para leer un bit específico de nuestro mapa de caracteres de 64 bits
bool getBit(vec2 charData, int bitIndex) {
    if (bitIndex >= 32) {
        return ((int(charData.x) >> (bitIndex - 32)) & 1) == 1;
    } else {
        return ((int(charData.y) >> bitIndex) & 1) == 1;
    }
}

void main() {
    // CORRECCIÓN DE INVERSIÓN VERTICAL:
    vec2 flippedTexcoord = vec2(v_texcoord.x, 1.0 - v_texcoord.y);

    // Detectar el tamaño del búfer de captura automáticamente
    ivec2 texSize = textureSize(u_screen_texture, 0);
    vec2 screenResolution = vec2(float(texSize.x), float(texSize.y));

    // Determinar el tamaño de la celda de la fuente (mínimo seguro de 4 píxeles)
    float fontSize = max(u_font_size, 4.0);

    // 1. Pixelar las coordenadas para agrupar la pantalla en celdas de texto
    vec2 virtualResolution = screenResolution / fontSize;
    vec2 cellCoord = floor(flippedTexcoord * virtualResolution) / virtualResolution;

    // 2. Obtener el color original muestreando el centro de la celda ASCII
    vec4 originalColor = texture(u_screen_texture, cellCoord + (0.5 / virtualResolution));

    // 3. Coordenadas de píxeles locales dentro de la celda actual (Rango de 0 a fontSize-1)
    int localX = int(fract(flippedTexcoord.x * virtualResolution.x) * 8.0);
    int localY = int(fract(flippedTexcoord.y * virtualResolution.y) * 8.0);
    
    // Inversión del eje Y interno para que las letras no salgan de cabeza
    localY = 7 - localY; 
    int bitIndex = clamp(localY * 8 + localX, 0, 63);

    // 4. Calcular el brillo (luminancia) de la celda y aplicar el modificador
    float brightness = dot(originalColor.rgb, vec3(0.2126, 0.7152, 0.0722));
    brightness = clamp(brightness * u_brightness_mod, 0.0, 1.0);

    // 5. Seleccionar el carácter ASCII real basándonos en el brillo (0 a 8)
    int charIndex = int(brightness * 8.0);
    vec2 characterData = asciiCharacters[clamp(charIndex, 0, 8)];

    // 6. Comprobar si el píxel de la letra está encendido o apagado
    bool isPixelOn = getBit(characterData, bitIndex);

    // 7. Modos de color: 0.0 = Monocromo fósforo verde Matrix, 1.0 = Color original de pantalla
    vec3 greenPhosphor = vec3(0.0, 1.0, 0.2) * brightness;
    vec3 baseColor = mix(greenPhosphor, originalColor.rgb, clamp(u_color_mode, 0.0, 1.0));

    // Si el bit de la fuente está encendido dibuja el color; si no, fondo negro puro
    vec3 finalColor = isPixelOn ? baseColor : vec3(0.0);

    // Retornar color final convertido a formato BGRA para tu pipeline de ModernGL
    f_color = vec4(finalColor.b, finalColor.g, finalColor.r, originalColor.a);
}
