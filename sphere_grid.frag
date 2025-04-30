#version 430 core

uniform vec2  resolution;
uniform float time;
uniform float audio_low;      
uniform float audio_mid;      
uniform int   color_scheme;
uniform int   enable_shadows;

in  vec2 fragCoord;
out vec4 fragColor;

#include "color.glsl"

// DE for a sphere at the grid point
float sphereDE(vec3 p, float r) {
    return length(p) - r;
}

// repeated grid with compressed bass
float mapScene(vec3 p) {
    float bass = pow(audio_low, 0.2);
    vec3 q = mod(p, 2.0) - 1.0;
    return sphereDE(q, 0.3 + 0.1 * bass);
}

void main() {
    vec2 uv = (fragCoord - 0.5)*2.0;
    uv.x *= resolution.x / resolution.y;
    vec3 ro = vec3(0.0, 0.0, -5.0);
    // orbit camera
    float angle = time * 0.2;
    mat2 rot = mat2(cos(angle), -sin(angle),
                    sin(angle),  cos(angle));
    vec3 rd = normalize(vec3(rot * uv, 1.0));

    float t = 0.0, d;
    int steps;
    const int MAX_STEPS = 80;
    for (steps = 0; steps < MAX_STEPS; steps++) {
        vec3 p = ro + rd * t;
        d = mapScene(p);
        if (d < 0.001) break;
        t += d * 0.9;
    }

    float norm = 1.0 - float(steps)/MAX_STEPS;
    float hue  = fract(time * 0.1 + audio_mid*0.0001 + t*0.02);
    vec3  base = getColor(hue, norm, color_scheme);
    if (enable_shadows == 1) {
        base *= pow(norm, 0.7);
    }

    fragColor = vec4(base,1.0);
}
