import struct

class Function:
    def __init__(self, nparams, returns, code):
        self.nparams = nparams
        self.returns = returns
        self.code = code

class Machine:
    def __init__(self, functions, memsize=65536):
        self.functions = functions
        self.stack = []
        self.memory = bytearray(memsize)

    def load(self, addr):
        return struct.unpack('<d', self.memory[addr:addr+8])[0]

    def store(self, addr, val):
        self.memory[addr:addr+8] = struct.pack('<d', val)

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def call(self, func, *args):
        locals = dict(enumerate(args))
        self.execute(func.code, locals)
        if func.returns:
            return self.pop()

    def execute(self, instructions, locals):
        for op, *args in instructions:
            print(op, args, self.stack)
            if op == 'const':
                self.push(args[0])
            elif op == 'add':
                right = self.pop()
                left = self.pop()
                self.push(left + right)
            elif op == 'mul':
                right = self.pop()
                left = self.pop()
                self.push(left * right)
            elif op == 'load':
                addr = self.pop()
                self.push(self.load(addr))
            elif op == 'store':
                val = self.pop()
                addr = self.pop()
                self.store(addr, val)
            elif op == 'local.get':
                self.push(locals[args[0]])
            elif op == 'local.set':
                locals[args[0]] = self.pop()
            elif op == 'call':
                func = self.functions[args[0]]
                fargs = reversed([self.pop() for _ in range(func.nparams)])
                result = self.call(func, *fargs)
                if func.returns:
                    self.push(result)
            else:
                raise RuntimeError(f'Bad op! {op}')


def example():
    # def update_position(x, v, dt):
    #     return x + v*dt
    #
    update_position = Function(nparams=3, returns=True, code=[
        ('local.get', 0), # x
        ('local.get', 1), # v
        ('local.get', 2), # dt
        ('mul',),
        ('add',),
    ])

    functions = [update_position]

    x_addr = 22
    v_addr = 42

    code = [
        ('const', x_addr),
        ('const', x_addr),
        ('load',),
        ('const', v_addr),
        ('load',),
        ('const', 0.1),
        ('call', 0),
        ('store',),
    ]

    m = Machine(functions)
    m.store(x_addr, 2.0)
    m.store(v_addr, 3.0)
    m.execute(code, None)
    print("Result: ", m.load(x_addr));

if __name__ == '__main__':
    example()
