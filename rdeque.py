class rdeque(object):
  __slots__ = ['right', 'left']

  def __init__(self, right):
    self.right = right
    self.left = []

  def len(self):
    return len(self.left) + len(self.right)

  def iadd(self, other):
    tmp = other.left[:]
    tmp.reverse()
    self.right += tmp
    self.right += other.right

  def append(self, value):
    self.right.append(value)

  def appendleft(self, value):
    self.left.append(value)

  def extend(self, values):
    self.right += values

  def extendleft(self, values):
    tmp = values[:]
    tmp.reverse()
    self.left += tmp

  def pop(self):
    if not self.right:
      mid = len(self.left) + 1 >> 1
      self.right = self.left[:mid]
      self.right.reverse()
      del self.left[:mid]
    if self.right:
      return self.right.pop()
    raise IndexError('pop from empty list')

  def popleft(self):
    if not self.left:
      mid = len(self.right) + 1 >> 1
      self.left = self.right[:mid]
      self.left.reverse()
      del self.right[:mid]
    if self.left:
      return self.left.pop()
    raise IndexError('pop from empty list')

  def popn(self, n):
    if n < 0:
      raise IndexError('list index out of range')
    i = len(self.right) - n
    if i >= 0:
      result = self.right[i:]
      del self.right[i:]
      return result
    i = -i
    if len(self.left) >= i > 0:
      result = self.left[:i]
      result.reverse()
      result += self.right
      del self.left[:i]
      self.right = []
      return result
    raise IndexError('list index out of range')

  def reverse(self):
    self.left, self.right = self.right, self.left

  def top(self):
    i = len(self.right) - 1
    if i >= 0:
      return self.right[i]
    if self.left:
      return self.left[0]
    raise IndexError('list index out of range')
