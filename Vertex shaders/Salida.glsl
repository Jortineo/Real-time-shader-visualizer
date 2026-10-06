#version 330

uniform sampler2D u_screen_texture;

in vec2 v_texcoord;
out vec4 f_color;

void main() {
    f_color = texture(u_screen_texture, v_texcoord);
}
