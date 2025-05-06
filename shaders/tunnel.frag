#version 430 core

uniform vec2  resolution;
uniform float time;
uniform float audio_low;       // low-freq warp
uniform float audio_mid;       // mid-freq color
uniform int   color_scheme;    // which palette to use
uniform int   enable_shadows;  // 0 = off, 1 = on

in  vec2 fragCoord; 
out vec4 fragColor;

// pull in your shared palettes & hsv2rgb/getColor
#include "color.glsl"

// Distance-estimate for a repeating cylindrical tunnel
float mapScene(vec3 p) {
    // tile every 2 units along Z
    p.z = mod(p.z + 1.0, 2.0) - 1.0;
    // radius warps with audio_low
    float r = 0.3 + 0.2 * audio_low * 0.0075;
    // return positive distance to the wall
    return abs(length(p.xy) - r);
}

void main() {
    // 1) screen→uv in (−1→+1), aspect-corrected
    vec2 uv = (fragCoord - 0.5) * 2.0;
    uv.x *= resolution.x / resolution.y;

    // 2) place ray origin just behind entrance and march “forward”
    vec3 ro = vec3(0.0, 0.0, -1.0 - time * 1.5);
    vec3 rd = normalize(vec3(uv, 1.0));

    // 3) ray-march loop
    float t = 0.0;
    float d = 0.0;
    int steps = 0;
    const int MAX_STEPS = 100;
    for (steps = 0; steps < MAX_STEPS; steps++) {
        vec3 pos = ro + rd * t;
        d = mapScene(pos);
        if (d < 0.0005) {
            break;
        }
        t += d * 0.8;
    }

    // 4) compute a normalized “iteration” for coloring & brightness
    float norm = 1.0 - float(steps) / float(MAX_STEPS);

    // 5) pick a hue that slides with travel + audio_mid
    float hue = fract(t * 0.1 + time * 0.05 + audio_mid * 0.0001);

    // 6) get base color from your shared getColor(...)
    vec3 base = getColor(hue, norm, color_scheme);

    // 7) optional shadows: darken according to how deep we went
    if (enable_shadows == 1) {
        // darker if we needed more steps (i.e. close-up on wall)
        base *= pow(norm, 0.6);
    }

    fragColor = vec4(base, 1.0);
}
