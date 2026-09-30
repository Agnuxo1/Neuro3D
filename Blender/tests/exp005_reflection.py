"""Scalar reflection robust to the non-unit norm of a float32 bpy hit normal.

Uses the actual reported normal, without replacing it with a designed axis.
"""
import math


def reflect_direction(direction,normal):
    d=tuple(float(v) for v in direction); n=tuple(float(v) for v in normal)
    if len(d)!=3 or len(n)!=3 or any(not math.isfinite(v) for v in d+n):
        raise ValueError('finite three-component directions required')
    norm2=sum(v*v for v in n)
    if norm2<=0 or not math.isfinite(norm2): raise ValueError('nonzero finite normal required')
    factor=2*sum(a*b for a,b in zip(d,n))/norm2
    reflected=tuple(a-factor*b for a,b in zip(d,n))
    length=math.hypot(*reflected)
    if length<=0 or not math.isfinite(length): raise ValueError('nonzero finite incoming direction required')
    return tuple(v/length for v in reflected)
