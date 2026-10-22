#version 330 core

uniform sampler2D u_screen_texture; // la textura

in vec2 v_texcoord; // las uv de 0 a 1

out vec4 fragColor; //el output

uniform float steps = 4.0; // min=2.0 max=10.0 default=4.0
uniform float edgeThreshold = 0.3; // min=0.1 max=1.0 default=0.3

float getLuminance(vec3 color) { //esto lo convierte en escala de grises
    return dot(color, vec3(0.2126, 0.7152, 0.0722));
}

void main() {
    vec2 flipped_v_texcoord = vec2(v_texcoord.x, 1.0 - v_texcoord.y); //La giro pq viene al revés

    vec4 originalColor = texture(u_screen_texture, flipped_v_texcoord); //saco el color original

    vec3 celColor = floor(originalColor.rgb * steps) / steps; //reduzco la paleta a steps

    vec2 screenSize = vec2(textureSize(u_screen_texture, 0)); //saco el tamaño de la textura 

    vec2 texelSize = 1.0 / screenSize; //tamaño de texels

    //Muestras de vecinos alrededor:
    float tLeft  = getLuminance(texture(u_screen_texture, flipped_v_texcoord + vec2(-texelSize.x,  texelSize.y)).rgb);
    float tReg   = getLuminance(texture(u_screen_texture, flipped_v_texcoord + vec2(          0.0,  texelSize.y)).rgb);
    float tRight = getLuminance(texture(u_screen_texture, flipped_v_texcoord + vec2( texelSize.x,  texelSize.y)).rgb);
    
    float mLeft  = getLuminance(texture(u_screen_texture, flipped_v_texcoord + vec2(-texelSize.x,          0.0)).rgb);
    float mRight = getLuminance(texture(u_screen_texture, flipped_v_texcoord + vec2( texelSize.x,          0.0)).rgb);
    
    float bLeft  = getLuminance(texture(u_screen_texture, flipped_v_texcoord + vec2(-texelSize.x, -texelSize.y)).rgb);
    float bReg   = getLuminance(texture(u_screen_texture, flipped_v_texcoord + vec2(          0.0, -texelSize.y)).rgb);
    float bRight = getLuminance(texture(u_screen_texture, flipped_v_texcoord + vec2( texelSize.x, -texelSize.y)).rgb);

    // matrices de sobel para gradientes horizontales y verticales
    float gX = (-1.0 * tLeft) + (-2.0 * mLeft) + (-1.0 * bLeft) + (1.0 * tRight) + (2.0 * mRight) + (1.0 * bRight);
    float gY = (-1.0 * tLeft) + (-2.0 * tReg) + (-1.0 * tRight) + (1.0 * bLeft) + (2.0 * bReg) + (1.0 * bRight);

    // intensidad del borde
    float edge = sqrt(gX * gX + gY * gY);

    //si la intensidad es mayor que el umbral pinto, si no no
    if (edge > edgeThreshold) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0); //linea negra
    } else {
        fragColor = vec4(celColor.bgr, originalColor.a);
    }
}