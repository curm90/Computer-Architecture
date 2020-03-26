"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001

SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Memory
        self.ram = [0] * 256
        # Registers
        self.register = [0] * 8
        # Internal registers
        self.pc = 0

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def load(self, filename):
        """Load a program into memory."""
        if len(sys.argv) != 2:
            print('Must specify a file to run.')
            print('Usage: <ls8.py> filename')
            sys.exit(1)

        try:
            address = 0
            with open(filename) as f:
                for instruction in f:
                    # Split instruction before and after comment symbol
                    comment_split = instruction.split('#')

                    # Extract our number
                    num = comment_split[0].strip()  # Trim whitespace

                    if comment_split[0] == '':
                        continue  # Ignore blank lines

                    # Convert our binary string to a number
                    val = int(num, 2)

                    self.ram[address] = val
                    address += 1

        except FileNotFoundError:
            print('File not found')
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        running = True
        while running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir == HLT:
                running = False

            elif ir == LDI:
                self.register[operand_a] = operand_b
                self.pc += 3

            elif ir == PRN:
                print(self.register[operand_a])
                self.pc += 2

            elif ir == MUL:
                self.alu('MUL', operand_a, operand_b)
                self.pc += 3

            elif ir == PUSH:
                # Extract register argument
                val = self.register[operand_a]
                # Decrement SP
                self.register[SP] -= 1
                # Copy the value in the given register to the address pointed to by SP
                self.ram_write(val, self.register[SP])
                # Increment program counter
                self.pc += 2

            elif ir == POP:
                # Grab value from stack
                val = self.ram[self.register[SP]]
                # Copy the value from the address pointed to by `SP` to the given register
                self.register[operand_a] = val
                # Increment SP
                self.register[SP] += 1
                # Increment program counter
                self.pc += 2


cpu = CPU()
# print(cpu.ram)
# print(cpu.ram_read(cpu.ram[cpu.pc + 1]))
