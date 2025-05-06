// color.glsl

vec3 hsv2rgb(vec3 c) {
    vec3 rgb = clamp(
        abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0,
        0.0, 1.0
    );
    return c.z * mix(vec3(1.0), rgb, c.y);
}

vec3 getColor(float hue, float normalized, int scheme) {
    if (scheme == 0) {
        // Default HSV
        return hsv2rgb(vec3(hue, 0.7, 1.0));
    } else if (scheme == 1) {
        // Grayscale
        return vec3(normalized);
    } else if (scheme == 2) {
        // Pastel
        return hsv2rgb(vec3(hue * 0.8 + 0.2, 0.3, 1.0));
    } else if (scheme == 3) {
        // Thermal (blue to red)
        float r = smoothstep(0.5, 1.0, normalized);
        float b = 1.0 - smoothstep(0.0, 0.5, normalized);
        return vec3(r, 0.0, b);
    } else if (scheme == 4) {
        // Neon pulse (hue wraps, bright banding)
        float pulse = abs(sin(normalized * 20.0));
        return hsv2rgb(vec3(mod(hue + pulse * 0.2, 1.0), 1.0, 1.0));
    } else if (scheme == 5) {
        // Rainbow stripes
        float banded = mod(normalized * 10.0, 1.0);
        return hsv2rgb(vec3(banded, 1.0, 1.0));
    } else if (scheme == 6) {
        // Luma-mapped gold
        float luma = smoothstep(0.0, 1.0, normalized);
        return vec3(1.0, 0.84 * luma, 0.25 * luma);
    } else if (scheme == 7) {
        // Cyan/magenta duotone
        return mix(vec3(0.0, 1.0, 1.0), vec3(1.0, 0.0, 1.0), normalized);
    }

    // Fallback: grayscale
    return vec3(normalized);
}
