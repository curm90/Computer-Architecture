"""CPU functionality."""

import sys

HLT = 0b00000001   # 1
LDI = 0b10000010   # 130
PRN = 0b01000111   # 71
ADD = 0b10100000   # 160
MUL = 0b10100010   # 162
POP = 0b01000110   # 70
PUSH = 0b01000101  # 69
CALL = 0b01010000  # 80
RET = 0b00010001   # 17
CMP = 0b10100111   # 167
JMP = 0b01010100   # 84
JEQ = 0b01010101   # 85
JNE = 0b01010110   # 86
AND = 0b10101000   # 168
OR = 0b10101010    # 170
XOR = 0b10101011   # 171
NOT = 0b01101001   # 105
MOD = 0b10100100   # 164
SHL = 0b10101100   # 172
SHR = 0b10101101   # 173


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # Memory
        self.register = [0] * 8  # Registers
        self.PC = 0  # Program counter
        self.FL = 0b00000000  # Flags
        self.register[7] = 0xF4  # Stack pointer

    def ram_read(self, MAR):
        ''' Return a value at memory address register (MAR) '''
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        ''' Write value memory data register to address memory address register (MAR) '''
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print('Must specify a file to run.')
            print('Usage: <ls8.py> filename')
            sys.exit(1)

        try:
            address = 0
            with open(sys.argv[1]) as f:
                for instruction in f:
                    # Split instruction before and after comment symbol
                    comment_split = instruction.strip().split('#')  # Trim whitespace

                    # Extract our number
                    num = comment_split[0]

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
        elif op == 'CMP':
            if self.register[reg_a] < self.register[reg_b]:
                self.FL = 0b00000100
            elif self.register[reg_a] > self.register[reg_b]:
                self.FL = 0b00000010
            elif self.register[reg_a] == self.register[reg_b]:
                self.FL = 0b00000001
        elif op == 'AND':
            self.register[reg_a] &= self.register[reg_b]
        elif op == 'OR':
            self.register[reg_a] |= self.register[reg_b]
        elif op == 'XOR':
            self.register[reg_a] ^= self.register[reg_b]
        elif op == 'NOT':
            self.register[reg_a] = ~self.register[reg_a]
        elif op == 'MOD':
            if self.register[reg_b] == 0:
                print('Error')
                sys.exit(1)
            self.register[reg_a] %= self.register[reg_b]
        elif op == 'SHL':
            self.register[reg_a] = self.register[reg_a] << self.register[reg_b]
        elif op == 'SHR':
            self.register[reg_a] = self.register[reg_a] >> self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            # self.FL,
            # self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        running = True

        while running:
            ir = self.ram_read(self.PC)
            operand_a = self.ram_read(self.PC + 1)
            operand_b = self.ram_read(self.PC + 2)

            if ir == HLT:
                running = False

            elif ir == LDI:
                self.register[operand_a] = operand_b

            elif ir == PRN:
                print(self.register[operand_a])

            elif ir == MUL:
                self.alu('MUL', operand_a, operand_b)

            elif ir == ADD:
                self.alu('ADD', operand_a, operand_b)

            elif ir == CMP:
                self.alu('CMP', operand_a, operand_b)

            elif ir == AND:
                self.alu('AND', operand_a, operand_b)

            elif ir == OR:
                self.alu('OR', operand_a, operand_b)

            elif ir == XOR:
                self.alu('XOR', operand_a, operand_b)

            elif ir == NOT:
                self.alu('NOT', operand_a, None)

            elif ir == MOD:
                self.alu('MOD', operand_a, operand_b)

            elif ir == SHL:
                self.alu('SHL', operand_a, operand_b)

            elif ir == SHR:
                self.alu('SHR', operand_a, operand_b)

            elif ir == PUSH:
                # Decrement SP
                self.register[7] -= 1
                # Extract register argument
                val = self.register[operand_a]
                # # Copy the value in the given register to the address pointed to by SP
                self.ram_write(val, self.register[7])

            elif ir == POP:
                # Grab value from stack
                val = self.ram_read(self.register[7])
                # Copy the value from the address pointed to by `SP` to the given register
                self.register[operand_a] = val
                # Increment SP
                self.register[7] += 1

            elif ir == CALL:
                self.register[7] -= 1
                self.ram_write(self.PC + 2, self.register[7])
                self.PC = self.register[operand_a]

            elif ir == RET:
                self.PC = self.ram_read(self.register[7])
                self.register[7] += 1

            elif ir == JMP:
                self.PC = self.register[operand_a]

            elif ir == JEQ:
                if self.FL & 0b00000001 == 1:
                    self.PC = self.register[operand_a]
                else:
                    self.PC += 2

            elif ir == JNE:
                if self.FL & 0b00000001 != 1:
                    self.PC = self.register[operand_a]
                else:
                    self.PC += 2

            else:
                print(f'Invalid instruction {ir}')
                running = False

            if ir & 0b00010000 == 0:
                self.PC += (ir >> 6) + 1


cpu = CPU()
