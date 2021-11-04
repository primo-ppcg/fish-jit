class rdeque(object):
  __slots__ = ['right', 'left']

  def __init__(self, right):
    self.right = right
    self.left = []

  def __len__(self):
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
    if len(self.right) < 1:
      mid = len(self.left) + 1 >> 1
      self.right = self.left[:mid]
      self.right.reverse()
      del self.left[:mid]
    return self.right.pop()

  def popleft(self):
    if len(self.left) < 1:
      mid = len(self.right) + 1 >> 1
      self.left = self.right[:mid]
      self.left.reverse()
      del self.right[:mid]
    return self.left.pop()

  def popn(self, n):
    i = len(self.right) - n
    if i >= 0:
      result = self.right[i:]
      del self.right[i:]
      return result
    i = -i
    assert i > 0
    result = self.left[:i]
    result.reverse()
    result += self.right
    del self.left[:i]
    self.right = []
    return result

  def top(self):
    i = len(self.right) - 1
    if i >= 0:
      return self.right[i]
    return self.left[0]

  def reverse(self):
    self.left, self.right = self.right, self.left
  
