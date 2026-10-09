"""Pure opt-in CPU rational -> binary32 hi/lo plus exact audit residual. No native admission."""
from fractions import Fraction as F
import struct

SCHEMA = "EXACT_SCALAR_HILO32_CPU_AUDIT_V1"


def rational(value):
    if type(value) is not list or len(value) != 2 or any(type(x) is not int for x in value):
        raise ValueError("canonical [numerator, denominator] integers required")
    n, d = value
    if d <= 0 or max(abs(n).bit_length(), d.bit_length()) > 4096:
        raise ValueError("positive denominator and bounded integers required")
    x = F(n, d)
    if [x.numerator, x.denominator] != value or abs(x) > 1000000:
        raise ValueError("noncanonical rational or outside opt-in scalar domain")
    return x


def pair(x):
    return [x.numerator, x.denominator]


def decode32(word):
    if type(word) is not int or not 0 <= word <= 0xffffffff:
        raise ValueError("uint32 required")
    e, m, s = (word >> 23) & 255, word & 0x7fffff, word >> 31
    if e == 255 or (e == 0 and m == 0 and s):
        raise ValueError("nonfinite or noncanonical negative zero")
    power = (e-150) if e else -149
    significand = ((1<<23)+m) if e else m
    value = F((-1 if s else 1)*significand)
    return value*(1<<power) if power >= 0 else value/(1<<-power)


def rounded_integer(n, d):
    q, r = divmod(n, d)
    return q + int(2*r > d or (2*r == d and q & 1))


def rn32(x):
    """Integer-only nearest/ties-even including subnormal controls; canonical +0."""
    if not x:
        return 0
    sign = 0x80000000 if x < 0 else 0
    n, d = abs(x.numerator), x.denominator
    e = n.bit_length()-d.bit_length()
    if (n < (d << e)) if e >= 0 else ((n << -e) < d):
        e -= 1
    shift = 149 if e < -126 else 23-e
    m = rounded_integer(n<<shift, d) if shift >= 0 else rounded_integer(n, d<<-shift)
    if e < -126:
        return 0 if not m else sign | m
    if m == 1<<24:
        m >>= 1
        e += 1
    if e > 127:
        raise ValueError("float32 overflow")
    return sign | ((e+127)<<23) | (m-(1<<23))


def subnormal(word):
    return (word & 0x7f800000) == 0 and (word & 0x7fffff) != 0


def encode_scalar(value):
    """8-byte little-endian hi/lo wire. Residual is separate exact CPU metadata, NOT wire."""
    x = rational(value)
    hi = rn32(x)
    lo = rn32(x-decode32(hi))
    total = decode32(hi)+decode32(lo)
    residual = x-total
    status = ("STOP_SUBNORMAL_COMPONENT" if subnormal(hi) or subnormal(lo)
              else "STOP_NONZERO_RESIDUAL" if residual
              else "EXACT_PAIR_CPU_ONLY")
    return {"schema":SCHEMA, "exact_input":pair(x), "hi_word":hi, "lo_word":lo,
            "wire_hex":struct.pack("<II",hi,lo).hex(), "pair_sum_exact":pair(total),
            "residual_exact":pair(residual), "status":status,
            "GPU_launch_allowed":False, "launch_exclusion_allowed":False,
            "native_precision_certified":False, "phase_certified":False,
            "native_origin_box_bound":None, "phase_error_bound":None,
            "full_costs":"UNKNOWN_NOT_ZERO"}


def audit_packet(packet):
    """Untrusted audit metadata is consistency checked, not authenticated as scene evidence."""
    if type(packet) is not dict or "exact_input" not in packet:
        raise ValueError("audit packet required")
    expected = encode_scalar(packet["exact_input"])
    if set(packet) != set(expected):
        raise ValueError("unexpected or missing fields")
    decode32(packet["hi_word"]); decode32(packet["lo_word"])
    for key in ("pair_sum_exact","residual_exact"):
        rational(packet[key])
    for key in ("GPU_launch_allowed","launch_exclusion_allowed","native_precision_certified","phase_certified"):
        if packet[key] is not False:
            raise ValueError("CPU audit cannot grant admission")
    if packet != expected:
        raise ValueError("wire/RNE/residual metadata inconsistent")
    return expected
