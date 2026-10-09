#version 330 core

out vec4 fragColor;
in vec2 v_texcoord;

uniform sampler2D u_screen_texture;

uniform vec2 u_resolution;

void main(){
    vec2 inverseVP = 1.0 / u_resolution.xy; // calculo el tamaño de un pixel

    // muestras de 4 pixeles en diagonal y el central
    vec3 rgbNW = texture(u_screen_texture, v_texcoord + vec2(-1.0, -1.0) * inverseVP).rgb;
    vec3 rgbNE = texture(u_screen_texture, v_texcoord + vec2(1.0, -1.0) * inverseVP).rgb;
    vec3 rgbSW = texture(u_screen_texture, v_texcoord + vec2(-1.0, 1.0) * inverseVP).rgb;
    vec3 rgbSE = texture(u_screen_texture, v_texcoord + vec2(1.0, 1.0) * inverseVP).rgb;
    vec3 rgbM = texture(u_screen_texture, v_texcoord).rgb;

    // convierto a luminancia
    vec3 luma = vec3(0.299, 0.587, 0.114);
    float lumaNW = dot(rgbNW, luma);
    float lumaNE = dot(rgbNE, luma);
    float lumaSW = dot(rgbSW, luma);
    float lumaSE = dot(rgbSE, luma);
    float lumaM = dot(rgbM, luma);

    // encuentro direccion del borde con gradiente
    vec2 dir;
    dir.x = -((lumaNW + lumaNE) - (lumaSW + lumaSE));
    dir.y = ((lumaNW + lumaSW) - (lumaNE + lumaSE));

    // si hay poco contraste evito dividir por 0
    float dirReduce = max((lumaNW + lumaNE + lumaSW + lumaSE) * (0.25 * 0.125), 0.0078125);
    float rcpDirMin = 1.0 / (min(abs(dir.x), abs(dir.y)) + dirReduce);

    //limito pa no pasarme
    dir = min(vec2(8.0, 8.0), max(vec2(-8.0, -8.0), dir * rcpDirMin)) * inverseVP;

    // difuminado inteligente con 2 submuestras
    vec3 bgrA = 0.5 * (
        texture(u_screen_texture, v_texcoord + dir * (1.0/3.0 - 0.5)).rgb +
        texture(u_screen_texture, v_texcoord + dir * (2.0/3.0 - 0.5)).rgb);
        
    vec3 bgrB = bgrA * 0.5 + 0.25 * (
        texture(u_screen_texture, v_texcoord + dir * (0.0/3.0 - 0.5)).rgb +
        texture(u_screen_texture, v_texcoord + dir * (3.0/3.0 - 0.5)).rgb);

    // comporbar si me pasé
    float lumaB = dot(bgrB, luma);
    float lumaMin = min(lumaM, min(min(lumaNW, lumaNE), min(lumaSW, lumaSE)));
    float lumaMax = max(lumaM, max(max(lumaNW, lumaNE), max(lumaSW, lumaSE)));

    // desenfoque moderado o amplio
    if ((lumaB < lumaMin) || (lumaB > lumaMax)) {
        fragColor = vec4(bgrA, 1.0); // Usar el desenfoque moderado
    } else {
        fragColor = vec4(bgrB, 1.0); // Usar el desenfoque más amplio
    }
}