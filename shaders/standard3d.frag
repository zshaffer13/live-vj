#version 430 core
#extension GL_ARB_gpu_shader_fp64 : enable


uniform vec3 u_light_dir;       // world‑space light direction
uniform float audio_low;        // from your audio.py

in vec3 v_normal;
out vec4 fragColor;

void main() {
    // simple Lambertian
    float NdotL = max(dot(v_normal, normalize(u_light_dir)), 0.0);
    // emissive “pulse” from low frequencies
    float pulse = audio_low * 2.0;
    vec3 color = vec3(0.2) + NdotL * vec3(0.8) + pulse;
    fragColor = vec4(color, 1.0);
}
