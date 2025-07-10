#version 430 core
#extension GL_ARB_gpu_shader_fp64 : enable

// — uniforms from your Python side —
uniform vec3   cameraPos;        // world‑space camera origin
uniform vec3   cameraDir;        // forward direction
uniform vec2   resolution;       // screen size in pixels
uniform float  time;             // global time
uniform int    maxSteps;         // ray‑march step limit
uniform float  maxDist;          // far plane
uniform float  surfDist;         // hit threshold
uniform float  fogDensity;       // controls volumetric falloff

out vec4 fragColor;

// — include your SDF primitives + combinations —
#include "sdf.glsl"


// Evaluate scene SDF at p
float map(vec3 p) {
    // example: a Mandelbulb…
    return mandelbulbSDF(p);
}

// Estimate surface normal by central differences
vec3 getNormal(vec3 p) {
    float e = 1e-3;
    return normalize(vec3(
        map(p + vec3( e, 0, 0)) - map(p - vec3( e, 0, 0)),
        map(p + vec3( 0, e, 0)) - map(p - vec3( 0, e, 0)),
        map(p + vec3( 0, 0, e)) - map(p - vec3( 0, 0, e))
    ));
}

void main() {
    // — build ray —
    vec2 uv = (gl_FragCoord.xy / resolution) * 2.0 - 1.0;
    uv.x *= resolution.x / resolution.y;
    vec3 ro = cameraPos;
    vec3 rd = normalize(cameraDir + vec3(uv, 0.0));

    // — ray‑march loop —
    float t = 0.0;
    for (int i = 0; i < maxSteps; i++) {
        vec3 p = ro + rd * t;
        float d = map(p);
        if (d < surfDist || t > maxDist) break;
        t += d;
    }

    // — shading hit or fog only —
    vec3 col = vec3(0.0);
    if (t < maxDist) {
        vec3 p = ro + rd * t;
        vec3 n = getNormal(p);

        // simple Phong diffuse
        vec3 L = normalize(vec3(0.5, 0.8, 0.6));
        float diff = max(dot(n, L), 0.0);

        col = vec3(diff);
    }
    // volumetric fog
    float fog = exp(-t * fogDensity);
    col = mix(vec3(0.0), col, fog);

    fragColor = vec4(col, 1.0);
}
