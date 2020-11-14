import os

from rpython.rlib.jit import JitDriver, elidable
from rpython.rlib.rrandom import Random
from rpython.rlib.rutf8 import unichr_as_utf8, codepoint_at_pos

from rbigfrac import rbigfrac, ZERO

jitdriver = JitDriver(
  greens = ['pcx', 'pcy', 'dx', 'dy'],
  reds   = 'auto'
)

NOUNS = {
  48: 0, 49: 1, 50:  2, 51:  3, 52:  4,  53:  5,  54:  6,  55:  7,
  56: 8, 57: 9, 97: 10, 98: 11, 99: 12, 100: 13, 101: 14, 102: 15
}

DYADICS = { 37:0, 40:0, 41:0, 42:0, 43:0, 44:0, 45:0, 61:0 }
STACKS  = { 36:0, 58:0, 64:0, 91:0, 93:0,108:0,114:0,123:0,125:0,126:0 }
MIRRORS = { 35:0, 47:0, 60:0, 62:0, 92:0, 94:0, 95:0,118:0,120:0,124:0 }
CONTROL = {  0:0, 32:0, 33:0, 38:0, 46:0, 59:0, 63:0,103:0,105:0,110:0,111:0,112:0 }
QUOTES  = { 34:0, 39:0 }


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


def mainloop(program, col_max, row_max, read_uni):
  pcx, pcy = 0, 0
  dx, dy = 1, 0
  stack = []
  stacks = []
  register = ZERO
  has_register = False
  registers = []
  skip = False
  slurp = False
  slurp_char = 0
  prng = Random()

  while True:
    jitdriver.jit_merge_point(
      pcx=pcx, pcy=pcy, dx=dx, dy=dy
    )

    if (pcx, pcy) in program:
      code = program[(pcx, pcy)]
    else:
      code = 0

    if skip:
      skip = False

    elif slurp:
      if code != slurp_char:
        stack.append(rbigfrac.fromint(code))
      else:
        slurp = False
        slurp_char = 0

    elif code in NOUNS:
      stack.append(rbigfrac.fromint(NOUNS[code]))

    elif code in DYADICS:
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

    elif code in STACKS:
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
            registers.append((register, has_register))
            register = ZERO
            has_register = False
          else:
            raise RuntimeError('Insufficient stack')
        elif code == 93:
          stack = stacks.pop() + stack
          register, has_register = registers.pop()
        elif code == 108:
          stack.append(rbigfrac.fromint(stacklen))
        elif code == 114:
          stack.reverse()
        elif code == 123:
          a = stack.pop(0)
          stack.append(a)
        elif code == 125:
          a = stack.pop()
          stack.insert(0, a)
        elif code == 126:
          stack.pop()
      except:
        raise

    elif code in MIRRORS:
      if   code ==  35: dx, dy = (-dx, -dy)
      elif code ==  47: dx, dy = (-dy, -dx)
      elif code ==  60: dx, dy = ( -1,   0)
      elif code ==  62: dx, dy = (  1,   0)
      elif code ==  92: dx, dy = ( dy,  dx)
      elif code ==  94: dx, dy = (  0,  -1)
      elif code ==  95: dx, dy = ( dx, -dy)
      elif code == 118: dx, dy = (  0,   1)
      elif code == 120:
        dx, dy = [(0, 1), (1, 0), (0, -1), (-1, 0)][int(prng.random() * 4)]
      elif code == 124: dx, dy = (-dx,  dy)

    elif code in CONTROL:
      try:
        if code == 33:
          skip = True
        elif code == 38:
          if has_register:
            stack.append(register)
            register = ZERO
            has_register = False
          else:
            register = stack.pop()
            has_register = True
        elif code == 46:
          pcy, pcx = stack.pop().toint(), stack.pop().toint()
        elif code == 59:
          return
        elif code == 63:
          skip = not stack.pop().tobool()
        elif code == 103:
          y, x = stack.pop().toint(), stack.pop().toint()
          if (x, y) in program:
            stack.append(rbigfrac.fromint(program[(x, y)]))
          else:
            stack.append(ZERO)
        elif code == 105:
          if read_uni:
            char = read_unichar()
          else:
            char = read_char()
          stack.append(rbigfrac.fromint(char))
        elif code == 110:
          n = stack.pop()
          os.write(1, n.tostr())
        elif code == 111:
          n = stack.pop()
          os.write(1, unichr_as_utf8(n.toint()))
        elif code == 112:
          y, x, v = stack.pop().toint(), stack.pop().toint(), stack.pop().toint()
          program[(x, y)] = v
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

    elif code in QUOTES:
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


def run(source, read_uni):
  lines = source.splitlines()
  program = {}
  col_max = {}
  row_max = {}
  y = 0
  for line in lines:
    x = 0
    for c in line.decode('utf-8'):
      program[(x, y)] = ord(c)
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
  mainloop(program, col_max, row_max, read_uni)


def main(argv):
  from rgetopt import gnu_getopt, GetoptError
  try:
    optlist, args = gnu_getopt(argv[1:], 'hc:u', ['help', 'code=', 'utf8'])
  except GetoptError as ex:
    os.write(2, ex.msg + '\n')
    return 1

  source = ''
  read_uni = False
  for opt, val in optlist:
    if opt == '-c' or opt == '--code':
      source = val
    elif opt == '-u' or opt == '--utf8':
      read_uni = True
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

  try:
    run(source, read_uni)
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
  -h, --help    display this message
''')


def target(*args):
  return main
