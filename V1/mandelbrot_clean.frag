/* mandelbrot_clean.frag (Double Precision, Color Schemes, Audio Warp, Optional Shadows) */
#version 430 core
#extension GL_ARB_gpu_shader_fp64 : enable

uniform double zoom;
uniform dvec2 offset;
uniform dvec2 resolution;
uniform int max_iterations;
uniform double rotation;
uniform double time;
uniform int color_scheme;
uniform int enable_shadows;  // 0 = off, 1 = on

uniform float audio_low;
uniform float audio_mid;
uniform float audio_high;

in vec2 fragCoord;
out vec4 fragColor;

// Float-based helpers for double ops
#define dcos(x)   (double(cos(float(x))))
#define dsin(x)   (double(sin(float(x))))
#define dlog(x)   (double(log(float(x))))
#define dpow(x,y) (double(pow(float(x), float(y))))

// Centralized color schemes
#include "color.glsl"

void main() {
    // 1. Normalize UV and apply aspect ratio
    dvec2 uv = dvec2(fragCoord);
    uv.x = (uv.x - 0.5) * (resolution.x / resolution.y) + 0.5;

    // 2. Audio-driven warp (based on low/mid freq)
    double wf = 0.0000025 * double(audio_low);
    uv.x += wf * dsin(uv.y * 20.0 + double(audio_mid) * 2.0);
    uv.y += wf * dcos(uv.x * 20.0 + double(audio_mid) * 2.0);

    // 3. Map to complex plane
    dvec2 c = dvec2((uv.x - 0.5) * zoom + offset.x,
                    (uv.y - 0.5) * zoom + offset.y);

    // 4. Rotate complex coordinate around offset
    dvec2 delta = c - offset;
    double cR = dcos(rotation);
    double sR = dsin(rotation);
    c = dvec2(delta.x * cR - delta.y * sR,
              delta.x * sR + delta.y * cR) + offset;

    // 5. Mandelbrot iteration
    dvec2 z = dvec2(0.0);
    int i;
    double smoothIter = 0.0;
    for (i = 0; i < max_iterations; i++) {
        vec2 zf = vec2(z.x, z.y);
        if (dot(zf, zf) > 4.0) {
            double log_zn = dlog(dot(zf, zf)) * 0.5;
            double nu = dlog(log_zn / dlog(2.0)) / dlog(2.0);
            smoothIter = double(i) + 1.0 - nu;
            break;
        }
        z = dvec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
    }

    // 6. Color output
    if (i == max_iterations) {
        fragColor = vec4(0.0);
    } else {
        double norm = smoothIter / double(max_iterations);
        double baseHue = 0.95 + 10.0 * norm;
        double hue_off = (1.0 - double(audio_low)) * 0.02;
        double hue = fract(baseHue + hue_off);

        // Use centralized palette logic
        vec3 color = getColor(float(hue), float(norm), color_scheme);

        // Optional shadowing based on escape speed
        if (enable_shadows == 1) {
            float brightness = pow(float(i) / float(max_iterations), 0.6);
            color *= brightness;
        }

        fragColor = vec4(color, 1.0);
    }
}
