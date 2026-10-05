"""
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