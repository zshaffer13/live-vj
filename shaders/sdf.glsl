#ifndef SDF_GLSL
#define SDF_GLSL

// ——— Primitives ———

// Sphere of radius r at the origin
float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

// Axis‑aligned box (half‑extents b)
float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, max(d.y, d.z)), 0.0);
}

// Plane with normal n, offset h: distance to plane dot(p,n)+h
float sdPlane(vec3 p, vec3 n, float h) {
    return dot(p, n) + h;
}

// ——— Boolean operations ———

float opUnion(float d1, float d2) {
    return min(d1, d2);
}
float opIntersection(float d1, float d2) {
    return max(d1, d2);
}
float opSubtract(float d1, float d2) {
    return max(d1, -d2);
}

// ——— Scene definition ———
//
// Raymarching shaders will call `map(p)` to find the closest
// surface distance at point p.  Edit this to build your scene.
//
float sceneSDF(vec3 p) {
    // example: a sphere at origin
    float d = sdSphere(p, 1.0);

    // example: a box shifted to the right
    float boxD = sdBox(p - vec3(2.0, 0.0, 0.0), vec3(0.5));
    // union them
    d = opUnion(d, boxD);

    return d;
}

#endif // SDF_GLSL
