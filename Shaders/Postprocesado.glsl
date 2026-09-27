#version 330

// Recibido desde tu VERTEX_SHADER de ModernGL
in vec2 v_texcoord;
out vec4 f_color;

// Uniform configurado por tu clase Renderizador
uniform sampler2D u_screen_texture;

// --- UNIFORMS DE POSTPROCESADO (Estructurados como tu dithering) ---
uniform float u_brightness;             // Si es 0.0, no suma nada. Rango en UI: -1.0 a 1.0
uniform float u_contrast_amount;        // Si es 0.0, no aplica contraste. Rango en UI: 0.0 a 1.0
uniform float u_saturation_amount;      // Si es 0.0, no quita saturación. Rango en UI: -1.0 a 1.0
uniform float u_vignette_amount;        // Si es 0.0, no oscurece bordes. Rango en UI: 0.0 a 1.0
uniform float u_grain_amount;           // Si es 0.0, no añade ruido. Rango en UI: 0.0 a 1.0
uniform float u_time;                   // Tiempo para animar el grano

void main() {
    // CORRECCIÓN DE INVERSIÓN VERTICAL (La tuya de siempre)
    vec2 flippedTexcoord = vec2(v_texcoord.x, 1.0 - v_texcoord.y);

    // 1. ÚNICA LECTURA DE TEXTURA (Idéntica a tu dithering)
    vec4 originalColor = texture(u_screen_texture, flippedTexcoord);
    vec3 color = originalColor.rgb;

    // 2. CORRECCIÓN DE COLOR (Diseñada para que el 0.0 sea el estado neutro)
    
    // Brillo: Suma directa. Si u_brightness es 0.0, el color no cambia.
    color += vec3(u_brightness);

    // Contraste: Calculamos el contraste por separado y lo mezclamos según el slider
    vec3 contrastColor = (color - vec3(0.5)) * 1.5 + vec3(0.5); 
    color = mix(color, contrastColor, u_contrast_amount); // Si el uniform es 0.0, se queda el color original

    // Saturación: Calculamos la escala de grises y la mezclamos según el slider
    float luma = dot(color, vec3(0.2126, 0.7152, 0.0722));
    vec3 grayColor = vec3(luma);
    // Si u_saturation_amount es 0.0, se queda igual. Si se mueve, satura o desatura.
    color = mix(color, grayColor, u_saturation_amount);

    // 3. EFECTOS AVANZADOS (Si el uniform es 0.0, el efecto es invisible pero la pantalla NO se apaga)
    
    // Viñeta pura basada en la posición del píxel
    vec2 uvVignette = flippedTexcoord * (1.0 - flippedTexcoord.yx);
    float vignetteFactor = uvVignette.x * uvVignette.y * 15.0;
    vignetteFactor = clamp(pow(max(vignetteFactor, 0.0), 0.75), 0.0, 1.0);
    // Mezclamos el color original con el oscurecido por la viñeta
    color = mix(color, color * vignetteFactor, u_vignette_amount);

    // Grano de película animado inline
    float pseudoNoise = fract(sin(dot(flippedTexcoord + vec2(u_time), vec2(12.9898, 78.233))) * 43758.5453);
    // Si u_grain_amount es 0.0, sumamos cero y no altera nada
    color += vec3(pseudoNoise - 0.5) * u_grain_amount;

    // 4. EVITAMOS VALORES NEGATIVOS (Tu misma línea exacta del dithering)
    color = clamp(color, 0.0, 1.0);

    // 5. RETORNAR COLOR FINAL EN FORMATO BGRA (Tu salida nativa de ModernGL)
    f_color = vec4(color.b, color.g, color.r, originalColor.a);
}
