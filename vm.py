import inspect


def parse_two_bytes(two_bytes):
    most_sig = 256 * two_bytes[1]
    least_sig = two_bytes[0]
    return most_sig + least_sig

OVERFLOW_VALUE = 32768
ADDR_BITS = 15
NUM_REGS = 8

class VirtualMachine:
    def __init__(self):
        self.pc = 0
        self.registers = [0] * NUM_REGS
        self.memory = [0] * (ADDR_BITS ** 2)
        self.stack = []
        self.text = []
        self.commands =  [self.o_halt, self.o_set, self.o_push, self.o_pop, self.o_eq, self.o_gt, self.o_jmp, self.o_jt,\
                self.o_jf, self.o_add, self.o_mult, self.o_mod, self.o_and, self.o_or, self.o_not, self.o_rmem, \
                self.o_wmem, self.o_call, self.o_ret, self.o_out, self.o_in, self.o_noop]

    def run_program(self, fname):
        program = self.parse(fname)
        while(True):
            opcode = program[self.pc]
            arg_index = self.pc + 1
            num_args_incl_self = len(inspect.getargspec(self.commands[opcode]).args)
            num_args = num_args_incl_self - 1
            args = []
            while num_args:
                args.append(program[arg_index])
                num_args -= 1
                arg_index += 1
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
        pass

    def o_pop(self, a):
        pass

    def o_eq(self, a, b, c):
        boolean = self.get_value(b) == self.get_value(c)
        if boolean:
            val = 1
        else:
            val = 0
        self.registers[a - OVERFLOW_VALUE] = val

    def o_gt(self, a, b, c):
        pass

    def o_jmp(self, a):
        self.pc = self.get_value(a)

    def o_jt(self, a, b):
        if self.get_value(a):
            self.o_jmp(b)

    def o_jf(self, a, b):
        if not self.get_value(a):
            self.o_jmp(b)

    def o_add(self, a, b, c):
        self.registers[a - OVERFLOW_VALUE] = \
                self.get_value(b) + self.get_value(c) % OVERFLOW_VALUE

    def o_mult(self, a, b, c):
        pass

    def o_mod(self, a, b, c):
        pass

    def o_and(self, a, b, c):
        pass

    def o_or(self, a, b, c):
        pass

    def o_not(self, a, b):
        pass

    def o_rmem(self, a, b):
        pass

    def o_wmem(self, a, b):
        pass

    def o_call(self, a):
        pass

    def o_ret(self):
        pass

    def o_out(self, a):
        print(chr(a), end='')

    def o_in(self, a):
        pass

    def o_noop(self):
        pass

    def exec_op(self, opcode, args):
        self.commands[opcode](*args)

if __name__ == "__main__":
    vm = VirtualMachine()
    vm.run_program("challenge.bin")
