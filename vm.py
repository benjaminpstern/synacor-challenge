import inspect


OVERFLOW_VALUE = 32768
ADDR_BITS = 15
NUM_REGS = 8
debug = False
wmemDebug = False
callretDebug = False

def parse_two_bytes(two_bytes):
    most_sig = 256 * two_bytes[1]
    least_sig = two_bytes[0]
    return most_sig + least_sig

class VirtualMachine:
    def __init__(self):
        self.pc = 0
        self.registers = [0] * NUM_REGS
        self.memory = [0] * (2 ** ADDR_BITS)
        self.line_buf = ""
        self.stack = []
        self.text = []
        self.commands =  [self.o_halt, self.o_set, self.o_push, self.o_pop, self.o_eq, self.o_gt, self.o_jmp, self.o_jt,\
                self.o_jf, self.o_add, self.o_mult, self.o_mod, self.o_and, self.o_or, self.o_not, self.o_rmem, \
                self.o_wmem, self.o_call, self.o_ret, self.o_out, self.o_in, self.o_noop]

    def run_program(self, fname):
        program = self.parse(fname)
        for i in range(len(program)):
            self.memory[i] = program[i]
        while(True):
            opcode = self.memory[self.pc]
            arg_index = self.pc + 1
            num_args_incl_self = len(inspect.getargspec(self.commands[opcode]).args)
            num_args = num_args_incl_self - 1
            args = []
            while num_args:
                args.append(self.memory[arg_index])
                num_args -= 1
                arg_index += 1
            if debug:
                print("executing: ",self.commands[opcode].__name__, args, "pc =", self.pc, "stack =", self.stack)
            self.pc = arg_index
            self.exec_op(opcode, args)


    def parse(self, fname):
        f = open(fname, "rb")
        program = []
        byte_pair = f.read(2)
        while len(byte_pair) == 2:
            program.append(parse_two_bytes(byte_pair))
            byte_pair = f.read(2)

        return program

    def get_value(self, a):
        if a >= OVERFLOW_VALUE:
            return self.registers[a - OVERFLOW_VALUE]
        else:
            return a

    def o_halt(self):
        exit()

    def o_set(self, a, b):
        self.registers[a - OVERFLOW_VALUE] = self.get_value(b)

    def o_push(self, a):
        self.stack.append(self.get_value(a))

    def o_pop(self, a):
        if not self.stack:
            raise ValueError("stack empty")
        self.o_set(a, self.stack.pop())

    def o_eq(self, a, b, c):
        boolean = self.get_value(b) == self.get_value(c)
        if boolean:
            val = 1
        else:
            val = 0
        self.o_set(a, val)

    def o_gt(self, a, b, c):
        boolean = self.get_value(b) > self.get_value(c)
        if boolean:
            val = 1
        else:
            val = 0
        self.o_set(a,val)

    def o_jmp(self, a):
        if debug:
            print("jmp", a)
        self.pc = self.get_value(a)

    def o_jt(self, a, b):
        if self.get_value(a):
            self.o_jmp(b)

    def o_jf(self, a, b):
        if not self.get_value(a):
            self.o_jmp(b)

    def o_add(self, a, b, c):
        result = (self.get_value(b) + self.get_value(c)) % OVERFLOW_VALUE
        self.o_set(a, result)

    def o_mult(self, a, b, c):
        result = (self.get_value(b) * self.get_value(c)) % OVERFLOW_VALUE
        self.o_set(a, result)

    def o_mod(self, a, b, c):
        result = self.get_value(b) % self.get_value(c)
        self.o_set(a, result)

    def o_and(self, a, b, c):
        result = self.get_value(b) & self.get_value(c)
        self.o_set(a, result)

    def o_or(self, a, b, c):
        result = self.get_value(b) | self.get_value(c)
        self.o_set(a, result)

    def o_not(self, a, b):
        result = ~self.get_value(b) % OVERFLOW_VALUE
        self.o_set(a, result)

    def o_rmem(self, a, b):
        result = self.memory[self.get_value(b)]
        self.o_set(a, result)

    def o_wmem(self, a, b):
        if wmemDebug:
            print("wmem: ", a, b, self.get_value(a), self.get_value(b), "prev val", self.memory[self.get_value(a)])
        self.memory[self.get_value(a)] = self.get_value(b)

    def o_call(self, a):
        if callretDebug:
            print("Calling to", a)
        self.o_push(self.pc)
        self.o_jmp(self.get_value(a))

    def o_ret(self):
        if self.stack:
            dest = self.stack.pop()
            if callretDebug:
                print("Returning", dest)
            self.o_jmp(dest)
        else:
            self.o_halt()

    def o_out(self, a):
        print(chr(self.get_value(a)), end='')

    def o_in(self, a):
        if debug:
            print("input",self.line_buf)
        if not self.line_buf:
            self.line_buf = input() + '\n'
        self.set(a, ord(self.line_buf[0]))
        self.line_buf = self.line_buf[1:]

    def o_noop(self):
        pass

    def exec_op(self, opcode, args):
        self.commands[opcode](*args)

if __name__ == "__main__":
    vm = VirtualMachine()
    vm.run_program("challenge.bin")
