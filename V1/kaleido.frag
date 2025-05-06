#version 430 core

uniform vec2  resolution;
uniform float time;
uniform float audio_low;       // bass warp
uniform float audio_mid;       // color shift
uniform int   color_scheme;
uniform int   enable_shadows;  // 0 = off, 1 = on

in  vec2 fragCoord;            // from vertex shader
out vec4 fragColor;

#include "color.glsl"
const float PI = 3.14159265359;

void main() {
    // 1) normalized UV in (–1→+1), aspect‐corrected
    vec2 uv = (fragCoord - 0.5) * 2.0;
    uv.x *= resolution.x / resolution.y;

    // 2) convert to polar coords
    float theta = atan(uv.y, uv.x);
    float r     = length(uv);

    // 3) fold theta into mirrored wedges
    const float NUM_SLICES = 144.0;
    float sector = 2.0 * PI / NUM_SLICES;
    // shift to [0,sector), then mirror about center
    theta = mod(theta + sector * 0.5, sector) - sector * 0.5;
    theta = abs(theta);

    // 4) compress bass so it isn’t overpowering
    float bass = pow(audio_low, 0.4);
    // warp radius by bass
    r += bass * 0.1;

    // 5) build a “tunnel” coordinate v along the wedge’s depth
    float v = fract(r * 4.0 - time * 0.6);

    // 6) build a wedge coordinate u ∈ [0,1] across each slice
    float u = theta / sector;  

    // 7) hue from u + audio_mid for subtle shift
    float hue = fract(u + time * 0.1 + audio_mid * 0.0001);

    // 8) get your color from shared palettes
    vec3 col = getColor(hue, v, color_scheme);

    // 9) optional “shadow” darkening toward wedge edges and troughs
    if (enable_shadows == 1) {
        // darker near the walls (u→0 or u→1) and in stripe troughs (v<0.5)
        float edgeFalloff = 1.0 - smoothstep(0.0, 0.2, u) * smoothstep(0.0, 0.2, 1.0 - u);
        float stripeShade = mix(0.8, 1.0, smoothstep(0.4, 0.6, v));
        col *= edgeFalloff * stripeShade;
    }

    fragColor = vec4(col, 1.0);
}
