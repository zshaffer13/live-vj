#version 430 core

uniform vec2  resolution;
uniform float time;
uniform float audio_low;
uniform float audio_mid;
uniform int   color_scheme;
uniform int   enable_shadows;

in  vec2 fragCoord;  // [0–1]
out vec4 fragColor;

#include "color.glsl"

//—— 1) Menger SDF ——  
float sdMenger(vec3 p) {
    float d = length(max(abs(p) - 1.0, 0.0));
    float scale = 1.0;
    float m = d;
    for (int i = 0; i < 5; i++) {
        p = abs(p);
        if (p.x < p.y) p.xy = p.yx;
        if (p.x < p.z) p.xz = p.zx;
        p = p * 3.0 - 2.0;
        scale *= 3.0;
        d = length(max(p - 1.0, 0.0)) / scale;
        m = min(m, d);
    }
    return m;
}

//—— 2) Normal ——  
vec3 calcNormal(vec3 p) {
    const float e = 0.001;
    return normalize(vec3(
      sdMenger(p + vec3(e,0,0)) - sdMenger(p - vec3(e,0,0)),
      sdMenger(p + vec3(0,e,0)) - sdMenger(p - vec3(0,e,0)),
      sdMenger(p + vec3(0,0,e)) - sdMenger(p - vec3(0,0,e))
    ));
}

//—— 3) Lighting ——  
vec3 phongShade(vec3 pos, vec3 n, vec3 base) {
    vec3 L = normalize(vec3(0.5,0.8,0.3));
    float diff = max(dot(n,L), 0.0);
    vec3 R = reflect(-L,n);
    float spec = pow(max(dot(R, -normalize(pos)), 0.0), 32.0);
    return base*diff + vec3(spec);
}

void main() {
    // A) uv → ray
    vec2 uv = (fragCoord - 0.5)*2.0;
    uv.x *= resolution.x/resolution.y;
    vec3 ro = vec3(0,0,3.0);
    vec3 rd = normalize(vec3(uv, -1.0));

    // B) fractalScale: *shrink* sponge so it spans more of your FOV
    const float fractalScale = 0.4;

    // C) Ray‐march in *world* space
    float t = 0.0, dW;
    for (int i = 0; i < 120; i++) {
        vec3 worldP = ro + rd*t;                     // world‐space point
        vec3 fractalP = worldP * fractalScale;       // map into fractal coords
        float dS = sdMenger(fractalP);               // distance in fractal space
        dW = dS / fractalScale;                      // convert back to world
        if (dW < 0.0005 || t > 20.0) break;
        t += dW;
    }
    if (dW > 0.0005 || t > 20.0) {
        fragColor = vec4(0.0);
        return;
    }

    // D) Hit shading
    vec3 hitW = ro + rd*t;
    vec3 hitF = hitW * fractalScale;                // fractal-space hit
    vec3 N    = calcNormal(hitF);

    // E) Color & audio drive
    float bass = pow(audio_low, 0.4);
    float depthNorm = smoothstep(0.0, 10.0, t);
    float hue = fract(depthNorm*4.0 + time*0.1 + audio_mid*1e-4);
    vec3 baseCol = getColor(hue, depthNorm, color_scheme);

    vec3 col = baseCol;
    if (enable_shadows == 1) {
        col = phongShade(hitW, N, baseCol);
    }
    col *= mix(1.0, 1.5, bass);

    fragColor = vec4(col, 1.0);
}
