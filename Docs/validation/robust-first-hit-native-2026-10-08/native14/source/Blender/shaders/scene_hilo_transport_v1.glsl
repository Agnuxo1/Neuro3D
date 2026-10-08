// Scene/query integer transport v1: native ALU diagnostics, no intersections.
// Storage: raw bytes in a 32 KiB std140 uvec4 UBO; R32UI output texels.
// Input scalar: [float32_hi_bits, float32_lo_bits, role, owner, element,
//                component, endpoint, reserved]. All texture channels are uint32.
// Output pair64: [hi_low_word, hi_high_word, lo_low_word, lo_high_word].
// This fixed operation graph is checked empirically against exact fractions.
// It is not a universal GLSL precision or physical uncertainty certificate.

const uint ABSENT = 0xffffffffu;
const uint INPUT_MAGIC = 0x4e33484cu;
const uint OUTPUT_MAGIC = 0x4e33484fu;
const uint HEADER = 32u;
const uint ROW_WORDS = 24u;
uint scalar_count_v, source_count_v, vertex_count_v, triangle_count_v;
uint scalar_offset_v, source_offset_v, vertex_offset_v, triangle_offset_v;
uint row_count_v;
bool bad_reference = false;

ivec2 texel_position(uint index) {
    return ivec2(int(index % 64u), int(index / 64u));
}

uint word_at(uint index) {
    if (index >= uint(input_word_count)) {
        bad_reference = true;
        return 0u;
    }
    return input_packet.words[index / 4u][index % 4u];
}

void output4(uint word_index, uvec4 value) {
    for (uint component = 0u; component < 4u; ++component)
        imageStore(delta_words, texel_position(word_index + component),
                   uvec4(value[component], 0u, 0u, 0u));
}

void write_header(uint status) {
    output4(0u, uvec4(OUTPUT_MAGIC, 1u, HEADER, uint(output_word_count)));
    output4(4u, uvec4(uint(input_word_count), row_count_v,
                      source_count_v, vertex_count_v));
    output4(8u, uvec4(triangle_count_v, scalar_count_v,
                      word_at(16u), uint(zero_low)));
    output4(12u, uvec4(status, 1u, uint(dispatch_nonce), ~uint(dispatch_nonce)));
    for (uint i = 16u; i < HEADER; i += 4u) output4(i, uvec4(0u));
}

dvec2 scalar_pair(uint index) {
    if (index >= scalar_count_v) {
        bad_reference = true;
        return dvec2(0.0lf);
    }
    uint offset = scalar_offset_v + index * 8u;
    float high_limb = uintBitsToFloat(word_at(offset));
    float low_limb = uintBitsToFloat(word_at(offset + 1u));
    if (isnan(high_limb) || isinf(high_limb) ||
        isnan(low_limb) || isinf(low_limb)) bad_reference = true;
    return dvec2(double(high_limb), zero_low == 0 ? double(low_limb) : 0.0lf);
}

dvec2 two_sum(double a, double b) {
    precise double sum = a + b;
    precise double b_virtual = sum - a;
    precise double a_virtual = sum - b_virtual;
    precise double b_error = b - b_virtual;
    precise double a_error = a - a_virtual;
    precise double error = a_error + b_error;
    return dvec2(sum, error);
}

dvec2 compensated_difference(dvec2 a, dvec2 b) {
    precise dvec2 primary = two_sum(a.x, -b.x);
    precise dvec2 secondary = two_sum(a.y, -b.y);
    precise double combined_error = primary.y + secondary.x;
    precise dvec2 corrected = two_sum(primary.x, combined_error);
    precise double tail = corrected.y + secondary.y;
    precise dvec2 result = two_sum(corrected.x, tail);
    return result;
}

uint vertex_scalar(uint vertex, uint axis) {
    if (vertex >= vertex_count_v) {
        bad_reference = true;
        return scalar_count_v;
    }
    return word_at(vertex_offset_v + vertex * 8u + 3u + axis);
}

void emit_row(uint row, uvec4 identity, uvec3 lhs, uvec3 rhs) {
    uint offset = HEADER + row * ROW_WORDS;
    output4(offset, identity);
    uvec2 naive[3];
    for (uint axis = 0u; axis < 3u; ++axis) {
        dvec2 a = scalar_pair(lhs[axis]);
        dvec2 b = scalar_pair(rhs[axis]);
        precise dvec2 result = compensated_difference(a, b);
        output4(offset + 4u + axis * 4u,
                uvec4(unpackDouble2x32(result.x), unpackDouble2x32(result.y)));
        // Deliberately collapse the input limbs for an explicit negative control.
        precise double collapsed_a = a.x + a.y;
        precise double collapsed_b = b.x + b.y;
        precise double collapsed_delta = collapsed_a - collapsed_b;
        naive[axis] = unpackDouble2x32(collapsed_delta);
    }
    output4(offset + 16u, uvec4(naive[0], naive[1]));
    output4(offset + 20u, uvec4(naive[2], 0u, 0u));
}

void main() {
    if (any(notEqual(gl_GlobalInvocationID, uvec3(0u)))) return;
    scalar_count_v = word_at(4u);
    scalar_offset_v = word_at(5u);
    source_count_v = word_at(7u);
    source_offset_v = word_at(8u);
    vertex_count_v = word_at(10u);
    vertex_offset_v = word_at(11u);
    triangle_count_v = word_at(13u);
    triangle_offset_v = word_at(14u);
    row_count_v = 0u;
    bool valid = input_word_count >= 32 && input_word_count <= 8192 &&
        output_word_count >= 32 && output_word_count <= 65536 &&
        (zero_low == 0 || zero_low == 1) &&
        word_at(0u) == INPUT_MAGIC && word_at(1u) == 1u &&
        word_at(2u) == HEADER && word_at(3u) == uint(input_word_count) &&
        scalar_count_v > 0u && scalar_count_v <= 4096u &&
        source_count_v > 0u && source_count_v <= 5u &&
        vertex_count_v > 0u && vertex_count_v <= 192u &&
        triangle_count_v > 0u && triangle_count_v <= 64u &&
        word_at(16u) > 0u && word_at(16u) <= 64u &&
        word_at(17u) < scalar_count_v &&
        word_at(6u) == 8u && word_at(9u) == 32u &&
        word_at(12u) == 8u && word_at(15u) == 8u;
    for (uint i = 18u; i < HEADER; ++i) valid = valid && word_at(i) == 0u;
    if (!valid || bad_reference) {
        write_header(1u);
        return;
    }
    valid = scalar_offset_v == HEADER &&
        source_offset_v == scalar_offset_v + scalar_count_v * 8u &&
        vertex_offset_v == source_offset_v + source_count_v * 32u &&
        triangle_offset_v == vertex_offset_v + vertex_count_v * 8u &&
        triangle_offset_v + triangle_count_v * 8u == uint(input_word_count);
    row_count_v = source_count_v * vertex_count_v + source_count_v +
                  2u * triangle_count_v;
    valid = valid && HEADER + row_count_v * ROW_WORDS == uint(output_word_count);
    if (!valid) {
        write_header(1u);
        return;
    }
    // Raw transport is independent of arithmetic and of the low-zero ablation.
    for (uint word = 0u; word < uint(input_word_count); ++word) {
        imageStore(echo_words, texel_position(word), uvec4(word_at(word), 0u, 0u, 0u));
    }
    uint row = 0u;
    for (uint source = 0u; source < source_count_v; ++source) {
        uint source_offset = source_offset_v + source * 32u;
        if (word_at(source_offset) != source ||
            word_at(source_offset + 1u) != ABSENT) bad_reference = true;
        uvec3 origin = uvec3(word_at(source_offset + 2u),
                            word_at(source_offset + 3u),
                            word_at(source_offset + 4u));
        for (uint vertex = 0u; vertex < vertex_count_v; ++vertex) {
            uint vo = vertex_offset_v + vertex * 8u;
            uint object_id = word_at(vo + 1u);
            if (word_at(vo) != vertex || object_id >= word_at(16u))
                bad_reference = true;
            uvec3 position = uvec3(vertex_scalar(vertex, 0u),
                                   vertex_scalar(vertex, 1u),
                                   vertex_scalar(vertex, 2u));
            emit_row(row++, uvec4(1u, source, vertex, object_id), position, origin);
        }
    }
    for (uint source = 0u; source < source_count_v; ++source) {
        uint so = source_offset_v + source * 32u;
        uvec3 lower = uvec3(word_at(so + 8u), word_at(so + 9u), word_at(so + 10u));
        uvec3 upper = uvec3(word_at(so + 11u), word_at(so + 12u), word_at(so + 13u));
        emit_row(row++, uvec4(2u, source, ABSENT, ABSENT), upper, lower);
    }
    // Both actual triangle edges consume connectivity on the GPU.
    // No host-derived hit, distance, intersection or selected primitive is input.
    for (uint edge = 1u; edge <= 2u; ++edge) {
        for (uint triangle = 0u; triangle < triangle_count_v; ++triangle) {
            uint to = triangle_offset_v + triangle * 8u;
            uint object_id = word_at(to + 1u);
            uint va = word_at(to + 3u);
            uint vb = word_at(to + 3u + edge);
            if (word_at(to) != triangle || object_id >= word_at(16u) ||
                va >= vertex_count_v || vb >= vertex_count_v ||
                word_at(to + 6u) > 3u || word_at(to + 7u) != 0u) {
                bad_reference = true;
            } else if (word_at(vertex_offset_v + va * 8u + 1u) != object_id ||
                       word_at(vertex_offset_v + vb * 8u + 1u) != object_id) {
                bad_reference = true;
            }
            uvec3 a = uvec3(vertex_scalar(va, 0u), vertex_scalar(va, 1u),
                            vertex_scalar(va, 2u));
            uvec3 b = uvec3(vertex_scalar(vb, 0u), vertex_scalar(vb, 1u),
                            vertex_scalar(vb, 2u));
            emit_row(row++, uvec4(2u + edge, ABSENT, triangle, object_id), b, a);
        }
    }
    write_header(bad_reference || row != row_count_v ? 2u : 0u);
}
