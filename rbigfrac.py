from rpython.rlib import jit
from rpython.rlib.rbigint import rbigint, ONERBIGINT, NULLRBIGINT
from rpython.rlib.rfloat import float_as_rbigint_ratio, formatd

class rbigfrac(object):
  __slots__ = ['numerator', 'denominator']

  def __init__(self, numerator, denominator):
    self.numerator = numerator
    self.denominator = denominator
    self.normalize()

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
  def tostr(self):
    if self.d.int_eq(1):
      return self.n.str()
    # undesirable!
    return formatd(self.n.tofloat() / self.d.tofloat(), 'r', 0)

  @jit.elidable
  def tobool(self):
    return self.n.tobool()

  @jit.elidable
  def add(self, other):
    return rbigfrac(
      self.n.mul(other.d).add(other.n.mul(self.d)),
      self.d.mul(other.d)
    )

  @jit.elidable
  def sub(self, other):
    return rbigfrac(
      self.n.mul(other.d).sub(other.n.mul(self.d)),
      self.d.mul(other.d)
    )

  @jit.elidable
  def mul(self, other):
    return rbigfrac(
      self.n.mul(other.n),
      self.d.mul(other.d)
    )

  @jit.elidable
  def div(self, other):
    if other.n.int_eq(0): raise ZeroDivisionError
    return rbigfrac(
      self.n.mul(other.d),
      self.d.mul(other.n)
    )

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
    return rbigfrac(
      num.sub(den.mul(quo)),
      self.d.mul(other.d)
    )

  @jit.elidable
  def lt(self, other):
    return self.n.mul(other.d).lt(self.d.mul(other.n))

  @jit.elidable
  def le(self, other):
    return self.n.mul(other.d).le(self.d.mul(other.n))

  @jit.elidable
  def gt(self, other):
    return self.n.mul(other.d).gt(self.d.mul(other.n))

  @jit.elidable
  def ge(self, other):
    return self.n.mul(other.d).ge(self.d.mul(other.n))

  @jit.elidable
  def eq(self, other):
    return self.n.mul(other.d).eq(self.d.mul(other.n))

  @jit.elidable
  def ne(self, other):
    return self.n.mul(other.d).ne(self.d.mul(other.n))


ZERO = rbigfrac(NULLRBIGINT, ONERBIGINT)
ONE  = rbigfrac( ONERBIGINT, ONERBIGINT)
