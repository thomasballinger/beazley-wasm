class Machine:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def execute(self, instructions):
        for op, *args in instructions:
            print(op, args, self.stack)
            if op == "const":
                self.push(args[0])
            elif op == "add":
                right = self.pop()
                left = self.pop()
                self.push(left + right)
            elif op == "mul":
                right = self.pop()
                left = self.pop()
                self.push(left * right)
            else:
                raise RuntimeError(f"Bad op! {op}")


def example():
    # compute 2 + 3 * 0.1
    code = [
        ("const", 2),
        ("const", 3),
        ("const", 0.1),
        ("mul",),
        ("add",),
    ]

    m = Machine()
    m.execute(code)
    print("Result: ", m.pop())


if __name__ == "__main__":
    example()
