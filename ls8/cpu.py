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
        self.opcodes = {
            "LDI": 0b10000010,
            "PRN": 0b01000111,
            "MUL": 0b10100010,
            "PUSH": 0b01000101,
            "POP": 0b01000110,
            "HLT": 0b00000001,
        }

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

                    program.append(val)

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} not found")
            sys.exit(2)

        for instruction in program:
            self.ram_write(address, instruction)
            address += 1

    # should accept the address to read and return the value stored there.
    def ram_read(self, address):
        return self.ram[address]

    # should accept a value to write, and the address to write it to.
    def ram_write(self, address, value):
        self.ram[address] = value

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
        # Running?
        running = True

        while running:
            # Fetch
            # Read the memory address stored in PC and store that result in instruction.
            instruction = self.ram_read(self.pc)

            # Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # Decode
            if instruction == self.opcodes["LDI"]:
                # Execute
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif instruction == self.opcodes["PRN"]:
                print(self.reg[operand_a])
                self.pc += 2
            elif instruction == self.opcodes["MUL"]:
                self.reg[operand_a] *= operand_b
                self.pc += 3
            elif instruction == self.opcodes["HLT"]:
                running = False
            else:
                print(f"Invalid Instruction {instruction}")
                sys.exit(1)
