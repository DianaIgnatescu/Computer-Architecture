"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = False
        self.reg = [0] * 8
        self.pc = 0
        self.ram = [0] * 256
        self.reg[7] = 0xFF
        self.sp = 7
        self.fl = 0b00000000
        self.opcodes = {
            "LDI": 0b10000010,
            "PRN": 0b01000111,
            "MUL": 0b10100010,
            "ADD": 0b10100000,
            "CMP": 0b10100111,
            "PUSH": 0b01000101,
            "POP": 0b01000110,
            "CALL": 0b01010000,
            "RET": 0b00010001,
            "HLT": 0b00000001,
        }
        self.branchtable = {}
        self.branchtable[self.opcodes["LDI"]] = self.LDI
        self.branchtable[self.opcodes["PRN"]] = self.PRN
        self.branchtable[self.opcodes["MUL"]] = self.MUL
        self.branchtable[self.opcodes["ADD"]] = self.ADD
        self.branchtable[self.opcodes["PUSH"]] = self.PUSH
        self.branchtable[self.opcodes["POP"]] = self.POP
        self.branchtable[self.opcodes["CALL"]] = self.CALL
        self.branchtable[self.opcodes["RET"]] = self.RET
        self.branchtable[self.opcodes["CMP"]] = self.CMP

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        program = []

        try:
            with open(filename) as f:
                for line in f:
                    # split before and after any comment symbols
                    comment_split = line.split('#')
                    # convert the pre-comment portion to a value
                    number = comment_split[0].strip()  # trim whitespace

                    if number == "":
                        continue  # ignore blank lines

                    val = int(number, 2)

                    self.ram_write(address, val)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} not found")
            sys.exit(2)

    # should accept the address to read and return the value stored there.
    def ram_read(self, address):
        return self.ram[address]

    # should accept a value to write, and the address to write it to.
    def ram_write(self, address, value):
        self.ram[address] = value

    def stack_push(self, value):
        # Decrement the SP
        # Copy the value in the given register to the address pointed to by SP.
        self.alu("DEC", self.sp, self.reg[value])
        self.ram_write(self.reg[self.sp], value)

    def stack_pop(self, value):
        # Copy the value from the address pointed to by `SP` to the given register.
        # Increment `SP`.
        popped = self.ram_read(self.reg[self.sp])
        self.alu("INC", self.sp, value)
        return popped

    def LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 2

    def MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def ADD(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def CMP(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3

    def PUSH(self, operand_a, operand_b):
        self.stack_push(self.reg[operand_a])
        self.pc += 2

    def POP(self, operand_a, operand_b):
        self.reg[operand_a] = self.stack_pop(self.reg[operand_a])
        self.pc += 2

    # Push the value in the given register on the stack.
    # Decrement the SP
    # Copy the value in the given register to the address pointed to by SP.
    def stack_push(self, value):
        self.alu("DEC", self.sp, self.reg[value])
        self.ram_write(self.reg[self.sp], value)

    # Pop the value at the top of the stack into the given register.
    # 1. Copy the value from the address pointed to by `SP` to the given register.
    # 2. Increment `SP`.

    def stack_pop(self, value):
        popped = self.ram_read(self.reg[self.sp])
        self.alu("INC", self.sp, value)
        return popped

    def CALL(self, operand_a, operand_b):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2
        # set the instruction pointer to the subroutine
        next_instruction = self.ram[self.pc + 1]
        self.pc = self.reg[next_instruction]

    def RET(self, operand_a, operand_b):
        self.pc = self.stack_pop(self)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "DEC":
            self.reg[reg_a] -= 1
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            else:
                self.fl = 0b00000100
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        running = True

        while running:
            # Fetch
            # Read the memory address stored in PC and store that result in instruction.
            instruction = self.ram_read(self.pc)

            # Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # Decode
            if instruction in self.branchtable:
                self.branchtable[instruction](operand_a, operand_b)
            elif instruction == self.opcodes["HLT"]:
                running = False
            else:
                print(f"Invalid Instruction {instruction}")
                sys.exit(1)
