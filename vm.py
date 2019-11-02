import struct

class Function:
    def __init__(self, nparams, returns, code):
        self.nparams = nparams
        self.returns = returns
        self.code = code

class ImportFunction:
    def __init__(self, nparams, returns, call):
        self.nparams = nparams
        self.returns = returns
        self.call = call


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
        if isinstance(func, Function):
            try:
                self.execute(func.code, locals)
            except Return:
                pass
            if func.returns:
                return self.pop()
        else:
            return func.call(*args)  # External (import function)

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
            elif op == 'sub':
                right = self.pop()
                left = self.pop()
                self.push(left - right)
            elif op == 'le':
                right = self.pop()
                left = self.pop()
                self.push(left < right)
            elif op == 'ge':
                right = self.pop()
                left = self.pop()
                self.push(left >= right)
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

            elif op == 'br':
                raise Break(args[0])

            elif op == 'br_if':
                if self.pop():
                    raise Break(args[0])

            elif op == 'block':  # ('block', [instructions])
                try:
                    self.execute(args[0], locals)
                except Break as b:
                    if b.level > 0:
                        b.level -= 1
                        raise
            # describes the above, 'block'
            # if (test) { consequence } else {alternative }
            #
            # ('block', [
            #             ('block', [
            #                         test
            #                         ('br_if', 0), # Goto 0
            #                         alternative,
            #                         ('br', 1),    # Goto 1
            #                       ]
            #             ),  # Label : 0
            #             consequence,
            #           ]
            # ) # Label 1:

            elif op == 'loop':
                while True:
                    try:
                        self.execute(args[0], locals)
                        break
                    except Break as b:
                        if b.level > 0:
                            b.level -= 1
                            raise
            # describes the above, 'loop'
            # while
            # ('block', [
            #            ('loop', [     # Label 0
            #                       not test
            #                       ('br_if', 1), # Goto 1:  (break)
            #                       body,
            #                       ('br', 0),    # Goto 0:  (continue)
            #                      ]
            #            )
            #           ]
            # )

            elif op == 'return':
                raise Return()

            else:
                raise RuntimeError(f'Bad op! {op}')


class Break(Exception):
    def __init__(self, level):
        self.level = level

class Return(Exception):
    def __init__(self):
        pass


def example():
    def py_display_player(x):
        import time
        print(' '*int(x) + '<O:>')
        time.sleep(0.05)

    display_player = ImportFunction(nparams=1, returns=None, call=py_display_player)
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

    functions = [update_position, display_player]

    x_addr = 22
    v_addr = 42

    m = Machine(functions)
    m.store(x_addr, 2.0)
    m.store(v_addr, 3.0)

    # while x > 0 {
    #   x = update_position(x, v, 0.1)
    #   if x >= 70 {
    #     v = -v;
    #   }
    # }

    m.execute([
        ('block', [
            ('loop', [
                ('const', x_addr),
                ('load',),
                ('call', 1),
                ('const', x_addr),
                ('load',),
                ('const', 0.0),
                ('le',),
                ('br_if', 1),
                ('const', x_addr),
                ('const', x_addr),
                ('load',),
                ('const', v_addr),
                ('load',),
                ('const', 0.1),
                ('call', 0),
                ('store',),
                ('block', [
                    ('const', x_addr),
                    ('load',),
                    ('const', 70.0),
                    ('ge',),
                    ('block', [
                            ('br_if', 0),
                            ('br', 1),
                        ]
                    ),
                    ('const', v_addr),
                    ('const', 0.0),
                    ('const', v_addr),
                    ('load',),
                    ('sub',),
                    ('store',),
                    ]
                ),
                ('br', 0),
            ])
        ])
    ], None)

    print("Result: ", m.load(x_addr));

if __name__ == '__main__':
    example()
