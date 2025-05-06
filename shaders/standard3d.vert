#version 430 core
#extension GL_ARB_gpu_shader_fp64 : enable

uniform mat4 u_MVP;

in vec3 in_position;
in vec3 in_normal;

out vec3 v_normal;

void main() {
    // pass the normal to the fragment
    v_normal = normalize(in_normal);
    // transform position
    gl_Position = u_MVP * vec4(in_position, 1.0);
}
