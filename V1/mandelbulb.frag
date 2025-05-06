#version 430 core

uniform vec2  resolution;
uniform float time;
uniform float audio_low;       // controls power
uniform float audio_mid;       // coloring
uniform int   color_scheme;
uniform int   enable_shadows;

in  vec2 fragCoord;
out vec4 fragColor;

#include "color.glsl"

// distance estimate for a Mandelbulb
float mandelbulbDE(vec3 pos) {
    vec3 z = pos;
    float dr = 1.0;
    float r = 0.0;
    const int ITER = 8;
    // soften bass dynamics
    float bass = pow(audio_low, 0.4);
    // audio‐driven power with compressed bass
    float power = 8.0 + bass * 2.0;
    for (int i = 0; i < ITER; i++) {
        r = length(z);
        if (r > 2.0) break;
        // convert to polar
        float theta = acos(z.z / r);
        float phi   = atan(z.y, z.x);
        dr = pow(r, power - 1.0) * power * dr + 1.0;
        // scale & rotate the point
        float zr = pow(r, power);
        theta *= power;
        phi   *= power;
        z = zr * vec3(
            sin(theta) * cos(phi),
            sin(phi) * sin(theta),
            cos(theta)
        ) + pos;
    }
    return 0.5 * log(r) * r / dr;
}

void main() {
    // screen → ray
    vec2 uv = (fragCoord - 0.5) * 2.0;
    uv.x *= resolution.x / resolution.y;
    vec3 ro = vec3(0.0, 0.0, -4.0);
    vec3 rd = normalize(vec3(uv, 1.0));

    // march
    float t = 0.0;
    float d = 0.0;
    int steps;
    const int MAX_STEPS = 64;
    for (steps = 0; steps < MAX_STEPS; steps++) {
        vec3 p = ro + rd * t;
        d = mandelbulbDE(p);
        if (d < 0.001) break;
        t += d;
    }

    // shade
    float norm = 1.0 - float(steps) / float(MAX_STEPS);
    float hue  = fract(t * 0.05 + time * 0.1 + audio_mid * 0.0001);
    vec3  base = getColor(hue, norm, color_scheme);
    if (enable_shadows == 1) {
        base *= pow(norm, 0.5);
    }

    fragColor = vec4(base, 1.0);
}
