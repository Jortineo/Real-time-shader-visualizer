#version 330

// Recibido desde el vertex
in vec2 v_texcoord;
out vec4 f_color;

// pantalla
uniform sampler2D u_screen_texture;

// uniforms
uniform float u_color_levels = 4.0;     // min=1.0 max=15.0 default=4.0
uniform float u_pixel_size = 1.0;       // min=1.0 max=20.0 default=1.0
uniform float u_dither_intensity = 1.0; // min=0.0 max=1.0 default=1.0

// matriz de bayer
const float bayerMatrix[16] = float[16](
     0.0 / 16.0,  8.0 / 16.0,  2.0 / 16.0, 10.0 / 16.0,
    12.0 / 16.0,  4.0 / 16.0, 14.0 / 16.0,  6.0 / 16.0,
     3.0 / 16.0, 11.0 / 16.0,  1.0 / 16.0,  9.0 / 16.0,
    15.0 / 16.0,  7.0 / 16.0, 13.0 / 16.0,  5.0 / 16.0
);


/*
const float bayerMatrix[16] = float[16](
    0.0,  8.0,  2.0, 10.0,
    12.0, 4.0, 14.0, 6.0,
    3.0, 11.0, 1.0,  9.0,
    15.0, 7.0, 13.0, 5.0
);
*/

void main() {
    // CORRECCIÓN DE INVERSIÓN VERTICAL:
    vec2 flippedTexcoord = vec2(v_texcoord.x, 1.0 - v_texcoord.y);

    // asegurar minimo pa no dividir entre 0
    float levels = max(u_color_levels, 2.0);

    // Detectar el tamaño del búfer de captura automáticamente
    ivec2 texSize = textureSize(u_screen_texture, 0);
    vec2 screenResolution = vec2(float(texSize.x), float(texSize.y));

    // si el pixel size es mayor que 1 aplico pixelacion
    vec2 pixelatedCoord = flippedTexcoord;
    if (u_pixel_size > 1.05) {
        vec2 virtualResolution = screenResolution / u_pixel_size; // aqui divido pa bajar la resolucion
        pixelatedCoord = (floor(flippedTexcoord * virtualResolution) + 0.5) / virtualResolution; // el +0.5 te mueve al centro del bloque
    }

    vec4 originalColor = texture(u_screen_texture, pixelatedCoord);

    int px = int(pixelatedCoord.x * screenResolution.x);
    int py = int(pixelatedCoord.y * screenResolution.y);
    
    
    int x = px % 4;
    int y = py % 4;
    
    
    float threshold = bayerMatrix[y * 4 + x];
    
    // color original rgb + el threshold en vec3 pa sumarlo Y -0.5 pa que en vez de estar de 0 a 1 esté de -0.5 a 0.5, alrededor de 0
    vec3 ditheredColor = originalColor.rgb + (vec3(threshold) - 0.5) * (u_dither_intensity / levels);
    
   
    ditheredColor = clamp(ditheredColor, 0.0, 1.0);
    
   
    ditheredColor = floor(ditheredColor * levels) / levels;
    
    
    f_color = vec4(ditheredColor.b, ditheredColor.g, ditheredColor.r, originalColor.a);
}
