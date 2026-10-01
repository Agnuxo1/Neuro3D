"""16xuint32 signed512 CPU mirror and restricted input X enclosures.

No Fraction/float/big-signed arithmetic in the limb core. This is not
compiled GLSL, YZ coverage, an event tree, phase, inference or GPU admission.
"""
import base64
import hashlib
import json
import struct

MASK = 0xffffffff
MODEL = 'axial-16limb-signed512-X-enclosures-CPU-mirror-v1'
ZERO = [0]*16


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def valid(words):
    require(type(words) is list and len(words) == 16 and
            all(type(w) is int and 0 <= w <= MASK for w in words), '16 uint32 limbs')
    return words


def negative(a):
    return bool(valid(a)[15] & 0x80000000)


def negate_mod(a):
    valid(a)
    out, carry = [], 1
    for word in a:
        total = (word ^ MASK) + carry
        out.append(total & MASK)
        carry = total >> 32
    return out


def compare(a,b):
    valid(a); valid(b)
    na, nb = negative(a), negative(b)
    if na != nb:
        return -1 if na else 1
    for i in range(15,-1,-1):
        if a[i] != b[i]:
            return -1 if a[i] < b[i] else 1
    return 0


def add(a,b):
    valid(a); valid(b)
    out, carry = [], 0
    for x,y in zip(a,b):
        low = (x+y) & MASK
        first = int(low < x)
        value = (low+carry) & MASK
        second = int(value < low)
        carry = first | second
        out.append(value)
    require(negative(a) != negative(b) or negative(out) == negative(a), 'signed512 add overflow')
    return out


def sub(a,b):
    valid(a); valid(b)
    out, borrow = [], 0
    for x,y in zip(a,b):
        low = (x-y) & MASK
        first = int(x < y)
        value = (low-borrow) & MASK
        second = int(low < borrow)
        borrow = first | second
        out.append(value)
    require(negative(a) == negative(b) or negative(out) == negative(a), 'signed512 sub overflow')
    return out


def negate(a):
    return sub(list(ZERO),a)


def mul(a,b):
    valid(a); valid(b)
    na,nb = negative(a),negative(b)
    ua,ub = negate_mod(a) if na else a, negate_mod(b) if nb else b
    full = [0]*32
    def accumulate(position,value):
        # Mirrors uint32 carry propagation after umulExtended, not int512 multiplication.
        carry = value
        for k in range(position,32):
            if carry == 0:
                break
            old = full[k]
            full[k] = (old+carry) & MASK
            carry = int(full[k] < old)
        require(carry == 0, 'unsigned1024 internal overflow')
    for i,x in enumerate(ua):
        for j,y in enumerate(ub):
            product = x*y  # only 32x32 -> 64, as GLSL umulExtended
            accumulate(i+j,product & MASK)
            accumulate(i+j+1,product >> 32)
    require(not any(full[16:]), 'signed512 multiply wide overflow')
    magnitude = full[:16]
    isnegative = na != nb
    require(magnitude[15] < 0x80000000 or
            (isnegative and magnitude[15] == 0x80000000 and not any(magnitude[:15])),
            'signed512 multiply sign overflow')
    return negate_mod(magnitude) if isnegative else magnitude


def decode32_scaled(word):
    require(type(word) is int and 0 <= word <= MASK, 'uint32 scalar')
    exponent, mantissa = (word >> 23) & 255, word & 0x7fffff
    require(exponent != 255 and (exponent != 0 or mantissa == 0), 'normal-or-zero finite limb; no FTZ')
    if exponent == 0:
        return list(ZERO)
    significand = mantissa | 0x800000
    shift = exponent-1  # decoded value * 2^149
    slot, offset = divmod(shift,32)
    out = list(ZERO)
    out[slot] = (significand << offset) & MASK
    if offset:
        out[slot+1] = significand >> (32-offset)
    return negate_mod(out) if word & 0x80000000 else out


def decode_hilo(pair):
    require(type(pair) is list and len(pair) == 2, 'two geometry hi-lo words')
    return add(decode32_scaled(pair[0]),decode32_scaled(pair[1]))


def initial_plane_clearance(first, other):
    """Conservative two-owner plane gate; ignores YZ coverage, never geometry PASS."""
    require(type(first) is list and len(first) == 2 and type(other) is list and len(other) == 2,
            'two ordered plane intervals')
    require(compare(first[0],first[1]) <= 0 and compare(other[0],other[1]) <= 0,
            'ordered plane intervals')
    mirror_forward = compare(first[0],ZERO) > 0
    other_behind = compare(other[1],ZERO) < 0
    other_after_mirror = compare(other[0],first[1]) > 0
    return mirror_forward and (other_behind or other_after_mirror)


def x_enclosures(name, packet, expected_packet_sha256):
    """New X-distance arithmetic from input-only packed words, not supplied lengths.

    Two-owner initial plane clearance is conservative, not a YZ/interior test.
    Neither positive X intervals nor this gate certify complete geometry.
    """
    canonical = json.dumps(packet,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    require(hashlib.sha256(canonical).hexdigest() == expected_packet_sha256, 'pinned input packet SHA')
    manifest = packet['manifest']
    require(manifest['case_name'] == name, 'case identity')
    buffers = {k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for key, raw in buffers.items():
        require(manifest['buffers'][key] == {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}, 'input receipt')
    meta = json.loads(buffers['input_metadata_json'])
    require(meta['object_ids'] == ['M','D'] and meta['kinds'] == ['mirror','det'], 'restricted M-D owner profile')
    tw = list(struct.unpack('<'+'I'*(len(buffers['triangles'])//4),buffers['triangles']))
    require(len(tw) % 35 == 0, 'triangle stride')
    planes = {}
    for start in range(0,len(tw),35):
        row = tw[start:start+35]
        owner = row[0]
        require(owner in (0,1), 'owner slot')
        xs = [decode_hilo(row[i:i+2]) for i in (1,7,13)]
        radius = valid(row[19:35])
        require(not negative(radius) and xs[0] == xs[1] == xs[2], 'shared nonnegative X enclosure')
        plane = {'center':xs[0],'lo':sub(xs[0],radius),'hi':add(xs[0],radius),'radius':radius}
        require(owner not in planes or planes[owner] == plane, 'same-owner shared plane')
        planes[owner] = plane
    require(set(planes) == {0,1}, 'both scene owners')
    sw = list(struct.unpack('<'+'I'*(len(buffers['sources'])//4),buffers['sources']))
    ids = meta['source_order']
    require(len(sw) == 32*len(ids), 'ordered source stride')
    rows = []
    unit = decode32_scaled(0x3f800000)
    two = [2]+[0]*15
    mirror, detector = planes[0], planes[1]
    for i,sid in enumerate(ids):
        row = sw[32*i:32*(i+1)]
        origin, direction = decode_hilo(row[:2]),decode_hilo(row[6:8])
        require(decode_hilo(row[8:10]) == ZERO and decode_hilo(row[10:12]) == ZERO, 'axial direction YZ zero')
        require(direction in (unit,negate(unit)), 'unit signed X direction')
        radius = valid(row[12:28])
        require(not negative(radius), 'nonnegative source radius')
        slo,shi = sub(origin,radius),add(origin,radius)
        sign = -1 if negative(direction) else 1
        first = [sub(mirror['lo'],shi),sub(mirror['hi'],slo)]
        other_initial = [sub(detector['lo'],shi),sub(detector['hi'],slo)]
        second = [sub(mirror['lo'],detector['hi']),sub(mirror['hi'],detector['lo'])]
        length = [sub(sub(mul(two,mirror['lo']),shi),detector['hi']),
                  sub(sub(mul(two,mirror['hi']),slo),detector['lo'])]
        if sign < 0:
            first,second,length = [[negate(values[1]),negate(values[0])] for values in (first,second,length)]
            other_initial = [negate(other_initial[1]),negate(other_initial[0])]
        positive = all(compare(values[0],ZERO)>0 for values in (first,second,length))
        clearance = initial_plane_clearance(first,other_initial)
        rows.append({'source_id':sid,'direction_sign':sign,'source_X_interval_words':[slo,shi],
            'first_X_distance_words':first,'second_X_distance_words':second,'geometric_length_words':length,
            'X_distances_strictly_positive_CPU_only':positive,
            'initial_other_owner_X_distance_words':other_initial,
            'initial_plane_clearance_and_competition_CPU_only':clearance,
            'conservative_X_plane_profile_pass_CPU_only':positive and clearance,
            'accepted_complete_geometry':False,'YZ_competition_tree_implemented':False})
    return {'model':MODEL,'case_name':name,'input_packet_sha256':expected_packet_sha256,
            'scene_binding_sha256':meta['scene_binding_sha256'],'word_ABI_sha256':meta['word_ABI_sha256'],
            'source_order':ids,'planes':planes,'sources':rows,
            'accepted_complete_geometry':False,'accepted_full_field_pipeline':False,
            'GLSL_compiled':False,'GPU_executed':False,'GPU_job_admission':False,
            'phase_evaluated':False,'reference_length_not_geometric_length':True}
