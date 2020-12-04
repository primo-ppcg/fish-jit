import os

from rpython.rlib.jit import JitDriver, elidable
from rpython.rlib.rarithmetic import r_uint64
from rpython.rlib.rrandom import Random
from rpython.rlib.rtime import time
from rpython.rlib.rutf8 import Utf8StringIterator, unichr_as_utf8, codepoint_at_pos

from rbigfrac import rbigfrac, ZERO

jitdriver = JitDriver(
  greens = ['pcx', 'pcy', 'dx', 'dy'],
  reds   = 'auto'
)


NOUNS, DYADICS, STACKS, MIRRORS, CONTROL, QUOTES, OTHER = range(7)
symbols = {
  NOUNS:   '0123456789abcdef',
  DYADICS: '%*+,-()=',
  STACKS:  '$:@[]lr{}~',
  MIRRORS: '#/<>\\^_vx|',
  CONTROL: '\0 !&.;?ginop',
  QUOTES:  '\'"'
}
types = {}
for type, chars in symbols.items():
  for char in chars:
    types[ord(char)] = type
nouns = dict([(ord(c), rbigfrac.fromint(int(c, 16))) for c in symbols[NOUNS]])


def read_char():
  char = os.read(0, 1)
  if char:
    return ord(char[0])
  return -1

def read_unichar():
  """Assumes utf-8 input, latin1 will be mangled.
  """
  char = os.read(0, 1)
  if char:
    code = ord(char[0])
    if code < 0x80:
      return code
    elif code < 0xC0:
      raise UnicodeDecodeError
    elif code < 0xE0:
      return codepoint_at_pos(char + os.read(0, 1), 0)
    elif code < 0xF0:
      return codepoint_at_pos(char + os.read(0, 2), 0)
    return codepoint_at_pos(char + os.read(0, 3), 0)
  return -1


def mainloop(program, col_max, row_max, read_func, no_prng):
  pcx, pcy = 0, 0
  dx, dy = 1, 0
  stack = []
  stacks = []
  register = None
  registers = []
  skip = False
  slurp = False
  slurp_char = 0
  prng = Random(r_uint64(time()*1000))

  while True:
    jitdriver.jit_merge_point(
      pcx=pcx, pcy=pcy, dx=dx, dy=dy
    )

    if (pcx, pcy) in program:
      code, type = program[(pcx, pcy)]
    else:
      code, type = 0, CONTROL

    if skip:
      skip = False

    elif slurp:
      if code != slurp_char:
        stack.append(rbigfrac.fromint(code))
      else:
        slurp = False
        slurp_char = 0

    elif type == NOUNS:
      stack.append(nouns[code])

    elif type == DYADICS:
      try:
        b, a, o = stack.pop(), stack.pop(), ZERO
        if   code ==  37: o = a.mod(b)
        elif code ==  42: o = a.mul(b)
        elif code ==  43: o = a.add(b)
        elif code ==  44: o = a.div(b)
        elif code ==  45: o = a.sub(b)
        elif code ==  40: o = rbigfrac.frombool(a.lt(b))
        elif code ==  41: o = rbigfrac.frombool(a.gt(b))
        elif code ==  61: o = rbigfrac.frombool(a.eq(b))
        stack.append(o)
      except:
        raise

    elif type == STACKS:
      stacklen = len(stack)
      try:
        if code == 36:
          b, a = stack.pop(), stack.pop()
          stack.extend([b, a])
        elif code == 58:
          stack.append(stack[stacklen-1])
        elif code == 64:
          c, b, a = stack.pop(), stack.pop(), stack.pop()
          stack.extend([c, a, b])
        elif code == 91:
          n = stack.pop().toint()
          i = stacklen - n - 1
          if i >= 0:
            stacks.append(stack[:i])
            stack = stack[i:]
            registers.append(register)
            register = None
          else:
            raise RuntimeError('Insufficient stack')
        elif code == 93:
          if len(stacks) >= 1:
            stack = stacks.pop() + stack
            register = registers.pop()
          else:
            stack = []
            register = None
        elif code == 108:
          stack.append(rbigfrac.fromint(stacklen))
        elif code == 114:
          stack.reverse()
        elif code == 123:
          if stacklen > 1:
            a = stack.pop(0)
            stack.append(a)
        elif code == 125:
          if stacklen > 1:
            a = stack.pop()
            stack.insert(0, a)
        elif code == 126:
          stack.pop()
      except:
        raise

    elif type == MIRRORS:
      if   code ==  35: dx, dy = (-dx, -dy)
      elif code ==  47: dx, dy = (-dy, -dx)
      elif code ==  60: dx, dy = ( -1,   0)
      elif code ==  62: dx, dy = (  1,   0)
      elif code ==  92: dx, dy = ( dy,  dx)
      elif code ==  94: dx, dy = (  0,  -1)
      elif code ==  95: dx, dy = ( dx, -dy)
      elif code == 118: dx, dy = (  0,   1)
      elif code == 120 and not no_prng:
        dx, dy = [(0, 1), (1, 0), (0, -1), (-1, 0)][int(prng.random() * 4)]
      elif code == 124: dx, dy = (-dx,  dy)

    elif type == CONTROL:
      try:
        if code == 33:
          skip = True
        elif code == 38:
          if register is None:
            register = stack.pop()
          else:
            stack.append(register)
            register = None
        elif code == 46:
          pcy, pcx = stack.pop().toint(), stack.pop().toint()
        elif code == 59:
          return
        elif code == 63:
          skip = not stack.pop().tobool()
        elif code == 103:
          y, x = stack.pop().toint(), stack.pop().toint()
          if (x, y) in program:
            stack.append(rbigfrac.fromint(program[(x, y)][0]))
          else:
            stack.append(ZERO)
        elif code == 105:
          char = read_func()
          stack.append(rbigfrac.fromint(char))
        elif code == 110:
          n = stack.pop()
          os.write(1, n.tostr())
        elif code == 111:
          n = stack.pop().toint()
          if n >= 0:
            os.write(1, unichr_as_utf8(n))
          else:
            raise UnicodeError('utf-8', 'out of range', n)
        elif code == 112:
          y, x, v = stack.pop().toint(), stack.pop().toint(), stack.pop().toint()
          if v in types:
            t = types[v]
          else:
            t = OTHER
          program[(x, y)] = (v, t)
          if x in col_max:
            col_max[x] = max(col_max[x], y)
          else:
            col_max[x] = y
          if y in row_max:
            row_max[y] = max(row_max[y], x)
          else:
            row_max[y] = x
      except:
        raise

    elif type == QUOTES:
      slurp = True
      slurp_char = code

    else:
      raise RuntimeError('Invalid instruction', code)

    x = pcx + dx
    if pcy in row_max:
      rmax = row_max[pcy]
    else:
      rmax = 0
    if x < 0 or x > rmax:
      if dx < 0:
        x = rmax
      elif dx > 0:
        x = 0

    y = pcy + dy
    if pcx in col_max:
      cmax = col_max[pcx]
    else:
      cmax = 0
    if y < 0 or y > cmax:
      if dy < 0:
        y = cmax
      elif dy > 0:
        y = 0

    pcx, pcy = x, y


def parse(source):
  lines = source.splitlines()
  program = {}
  col_max = {}
  row_max = {}
  y = 0
  for line in lines:
    x = 0
    for c in Utf8StringIterator(line):
      if c in types:
        t = types[c]
      else:
        t = OTHER
      program[(x, y)] = (c, t)
      if x in col_max:
        col_max[x] = max(col_max[x], y)
      else:
        col_max[x] = y
      if y in row_max:
        row_max[y] = max(row_max[y], x)
      else:
        row_max[y] = x
      x += 1
    y += 1
  return program, col_max, row_max


def main(argv):
  from rgetopt import gnu_getopt, GetoptError
  try:
    optlist, args = gnu_getopt(argv[1:], 'hc:u', ['help', 'code=', 'utf8', 'no-prng'])
  except GetoptError as ex:
    os.write(2, ex.msg + '\n')
    return 1

  source = ''
  read_func = read_char
  no_prng = False
  for opt, val in optlist:
    if opt == '-c' or opt == '--code':
      source = val
    elif opt == '-u' or opt == '--utf8':
      read_func = read_unichar
    elif opt == '--no-prng':
      no_prng = True
    elif opt == '-h' or opt == '--help':
      display_usage(argv[0])
      display_help()
      return 1

  if source == '':
    try:
      with open(args[0]) as file:
        source = file.read()
    except IndexError:
      display_usage(argv[0])
      return 1
    except IOError:
      os.write(2, 'File not found: %s\n'%args[0])
      return 1

  program, col_max, row_max = parse(source)

  try:
    mainloop(program, col_max, row_max, read_func, no_prng)
  except:
    os.write(2, 'something smells fishy...\n')
    return 1
  return 0


def display_usage(name):
  os.write(2, 'Usage: %s [-h] (<file> | -c <code>) [<options>]\n'%name)

def display_help():
  os.write(2, '''
A just-in-time compiling interpreter for the ><> programming language.
Arguments:
  file          a ><> script file to execute
Options:
  -c, --code=   a string of instructions to be executed
                if present, the file argument will be ignored
  -u, --utf8    parse input as utf-8
  --no-prng     disable the PRNG (`x` command becomes a no-op)
  -h, --help    display this message
''')


def target(*args):
  return main
