"""Outward rational intervals; proof-bearing elementary functions, stdlib only."""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
import math

BITS = 128
GRID = 1 << BITS


def down(value):
    value = F(value)
    return F((value.numerator*GRID)//value.denominator, GRID)


def up(value): return -down(-F(value))


@dataclass(frozen=True)
class Interval:
    lo: F
    hi: F

    def __init__(self, lo, hi=None):
        lo, hi = F(lo), F(lo if hi is None else hi)
        if lo > hi: raise ValueError('ordered interval required')
        object.__setattr__(self, 'lo', lo); object.__setattr__(self, 'hi', hi)

    @staticmethod
    def rounded(lo, hi): return Interval(down(lo), up(hi))
    def __neg__(self): return Interval(-self.hi, -self.lo)
    def __add__(self, other):
        other = interval(other)
        return Interval.rounded(self.lo+other.lo, self.hi+other.hi)
    __radd__ = __add__
    def __sub__(self, other): return self + (-interval(other))
    def __rsub__(self, other): return interval(other) - self
    def __mul__(self, other):
        other = interval(other)
        products = [a*b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return Interval.rounded(min(products), max(products))
    __rmul__ = __mul__
    def __truediv__(self, other):
        other = interval(other)
        if other.lo <= 0 <= other.hi: raise ZeroDivisionError('interval denominator contains zero')
        inverse = Interval.rounded(1/other.hi, 1/other.lo)
        return self*inverse
    def __rtruediv__(self, other): return interval(other)/self
    def contains(self, value): return self.lo <= F(value) <= self.hi
    def square(self):
        values = (self.lo*self.lo, self.hi*self.hi)
        return Interval.rounded(0 if self.lo <= 0 <= self.hi else min(values), max(values))
    def sqrt(self):
        if self.lo < 0: raise ValueError('nonnegative sqrt interval required')
        def endpoint(value, upper):
            shifted = value.numerator << (2*BITS)
            root = math.isqrt(shifted//value.denominator)
            if upper and root*root*value.denominator != shifted: root += 1
            return F(root, GRID)
        return Interval(endpoint(self.lo, False), endpoint(self.hi, True))
    def max_abs(self): return max(abs(self.lo), abs(self.hi))
    def width(self): return self.hi-self.lo
    def wire(self): return {'lo': [self.lo.numerator, self.lo.denominator], 'hi': [self.hi.numerator, self.hi.denominator]}


def interval(value): return value if isinstance(value, Interval) else Interval(value)


def arctan_reciprocal(denominator, terms=64):
    if type(denominator) is not int or denominator < 2 or type(terms) is not int or terms < 1:
        raise ValueError('positive convergent reciprocal arctan required')
    value = sum((F((-1)**i, (2*i+1)*denominator**(2*i+1)) for i in range(terms)), F(0))
    remainder = F((-1)**terms, (2*terms+1)*denominator**(2*terms+1))
    return Interval.rounded(min(value, value+remainder), max(value, value+remainder))


@lru_cache(maxsize=1)
def pi_interval():
    # tan(4 atan(1/5)-atan(1/239))=1 in the first quadrant.
    return 16*arctan_reciprocal(5)-4*arctan_reciprocal(239)


def sincos(value, terms=32):
    if type(terms) is not int or not 1 <= terms <= 64: raise ValueError('bounded Taylor order required')
    value = interval(value)
    pi = pi_interval()
    midpoint = (value.lo+value.hi)/2
    pi_midpoint = (pi.lo+pi.hi)/2
    cycles = (midpoint/(2*pi_midpoint)+F(1, 2)).numerator // (midpoint/(2*pi_midpoint)+F(1, 2)).denominator
    reduced = value - (2*cycles)*pi
    magnitude = reduced.max_abs()
    if magnitude > 4:
        return Interval(-1, 1), Interval(-1, 1)
    square = reduced.square()
    sine_poly = Interval(F((-1)**(terms-1), math.factorial(2*terms-1)))
    cosine_poly = Interval(F((-1)**(terms-1), math.factorial(2*terms-2)))
    for i in range(terms-2, -1, -1):
        sine_poly = sine_poly*square + F((-1)**i, math.factorial(2*i+1))
        cosine_poly = cosine_poly*square + F((-1)**i, math.factorial(2*i))
    sine = reduced*sine_poly
    cosine = cosine_poly
    sine_remainder = magnitude**(2*terms+1)/math.factorial(2*terms+1)
    cosine_remainder = magnitude**(2*terms)/math.factorial(2*terms)
    sine = Interval.rounded(sine.lo-sine_remainder, sine.hi+sine_remainder)
    cosine = Interval.rounded(cosine.lo-cosine_remainder, cosine.hi+cosine_remainder)
    return Interval(max(F(-1), sine.lo), min(F(1), sine.hi)), Interval(max(F(-1), cosine.lo), min(F(1), cosine.hi))


def error_upper(value, reference):
    value = F(value)
    return max(abs(value-reference.lo), abs(value-reference.hi))


def upward_float(value):
    value = F(value)
    result = float(value)
    if not math.isfinite(result): raise ValueError('finite displayed bound required')
    return math.nextafter(result, math.inf) if F(result) < value else result
