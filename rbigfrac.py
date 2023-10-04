import math

from rpython.rlib import jit
from rpython.rlib.rbigint import rbigint, ONERBIGINT, NULLRBIGINT, _AsScaledDouble, SHIFT
from rpython.rlib.rfloat import float_as_rbigint_ratio, formatd

class rbigfrac(object):
  __slots__ = ['numerator', 'denominator']

  def __init__(self, numerator, denominator):
    self.numerator = numerator
    self.denominator = denominator

  def normalize(self):
    if self.denominator.int_ne(1):
      g = self.numerator.gcd(self.denominator)
      self.numerator = self.numerator.div(g)
      self.denominator = self.denominator.div(g)

  @property
  def n(self):
    return self.numerator

  @property
  def d(self):
    return self.denominator

  @staticmethod
  @jit.elidable
  def fromint(n):
    return rbigfrac(rbigint.fromint(n), ONERBIGINT)

  @staticmethod
  @jit.elidable
  def fromfloat(f):
    num, den = float_as_rbigint_ratio(f)
    return rbigfrac(num, den)

  @staticmethod
  @jit.elidable
  def frombool(b):
    if b: return ONE
    return ZERO

  @jit.elidable
  def toint(self):
    return self.n.div(self.d).toint()

  @jit.elidable
  def tofloat(self):
    nman, nexp = _AsScaledDouble(self.n)
    dman, dexp = _AsScaledDouble(self.d)
    return math.ldexp(nman / dman, (nexp - dexp) * SHIFT)

  @jit.elidable
  def tobool(self):
    return self.n.tobool()

  @jit.elidable
  def tostr(self):
    self.normalize()
    if self.d.int_eq(1):
      return self.n.str()
    # undesirable!
    return formatd(self.tofloat(), 'r', 0)

  @jit.elidable
  def add(self, other):
    ret = rbigfrac(
      self.n.mul(other.d).add(self.d.mul(other.n)),
      self.d.mul(other.d)
    )
    if self.d.numdigits() > 1 and other.d.numdigits() > 1:
      ret.normalize()
    return ret

  @jit.elidable
  def sub(self, other):
    ret = rbigfrac(
      self.n.mul(other.d).sub(self.d.mul(other.n)),
      self.d.mul(other.d)
    )
    if self.d.numdigits() > 1 and other.d.numdigits() > 1:
      ret.normalize()
    return ret

  @jit.elidable
  def mul(self, other):
    ret = rbigfrac(
      self.n.mul(other.n),
      self.d.mul(other.d)
    )
    if self.d.numdigits() > 1 and other.d.numdigits() > 1:
      ret.normalize()
    return ret

  @jit.elidable
  def div(self, other):
    if other.n.get_sign() == 0: raise ZeroDivisionError
    num = self.n.mul(other.d)
    den = self.d.mul(other.n)
    if den.get_sign() == -1:
      num = num.neg()
      den = den.neg()
    ret = rbigfrac(num, den)
    if self.d.numdigits() > 1 and other.n.numdigits() > 1:
      ret.normalize()
    return ret

  @jit.elidable
  def floordiv(self, other):
    return rbigfrac(
      self.n.mul(other.d).div(self.d.mul(other.n)),
      ONERBIGINT
    )

  @jit.elidable
  def mod(self, other):
    num = self.n.mul(other.d)
    den = self.d.mul(other.n)
    quo = num.div(den)
    ret = rbigfrac(
      num.sub(den.mul(quo)),
      self.d.mul(other.d)
    )
    if self.d.numdigits() > 1 and other.d.numdigits() > 1:
      ret.normalize()
    return ret

  @jit.elidable
  def lt(self, other):
    return self.n.mul(other.d).lt(self.d.mul(other.n))

  @jit.elidable
  def le(self, other):
    return not other.lt(self)

  @jit.elidable
  def gt(self, other):
    return other.lt(self)

  @jit.elidable
  def ge(self, other):
    return not self.lt(other)

  @jit.elidable
  def eq(self, other):
    return self.n.mul(other.d).eq(self.d.mul(other.n))

  @jit.elidable
  def ne(self, other):
    return not self.eq(other)


ZERO = rbigfrac(NULLRBIGINT, ONERBIGINT)
ONE  = rbigfrac( ONERBIGINT, ONERBIGINT)
