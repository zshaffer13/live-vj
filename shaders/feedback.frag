#version 430 core

in vec2 v_uv;
out vec4 fragColor;

uniform sampler2D u_current;   // newly rendered fractal
uniform sampler2D u_previous;  // last frame’s feedback
uniform float     fade;        // trail persistence [0–1]
uniform float     time;        // global time
uniform float     audio_low;   // low-freq energy for color shift

// simple HSV↔RGB you already have
vec3 hsv2rgb(vec3 c) { … }
vec3 rgb2hsv(vec3 c) { … } 

void main() {
    // 1) swirl distortion on the previous frame’s UV
    vec2 center = vec2(0.5);
    vec2 dir = v_uv - center;
    float radius = length(dir);
    float angle  = 0.3 * sin( time*0.5 + radius*12.0 );
    float s = sin(angle), c = cos(angle);
    vec2 swirled = center + mat2(c,-s,s,c) * dir;

    // 2) fetch previous & current
    vec4 prev = texture(u_previous, swirled);
    vec4 curr = texture(u_current,  v_uv);

    // 3) hue-shift the previous frame by audio_low
    vec3 hsv = rgb2hsv(prev.rgb);
    hsv.x = fract( hsv.x + audio_low * 0.1 );
    prev.rgb = hsv2rgb(hsv);

    // 4) additive blend to get that blazing glow
    vec3 blend = prev.rgb * fade + curr.rgb;
    fragColor = vec4(blend, 1.0);
}
