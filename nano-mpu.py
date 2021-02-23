from enum import Enum, unique


@unique
class Instructions(Enum):
    HLT = "0"
    OUTL = "1"
    OUTR = "2"
    OUTA = "3"
    OUTB = "4"
    MOVLA = "11"
    MOVLB = "12"
    MOVRA = "13"
    MOVRB = "14"
    MOVAR = "15"
    MOVBR = "16"
    ADDA = "21"
    ADDB = "22"
    SUBBA = "23"
    SUBAB = "24"
    ANDA = "31"
    ANDB = "32"
    ORA = "33"
    ORB = "34"

    @staticmethod
    def find_instruction(hexcode: str):
        for i in Instructions:
            if i.value == hexcode[2:]:
                return i


@unique
class BitWidth(Enum):
    TWO_BIT = 2
    EIGHT_BIT = 8

    def max_value(self):
        return 2 ** self.value - 1


class Register:
    def __init__(self, bit_width: BitWidth):
        self.bitWidth = bit_width
        self.maxValue = self.bitWidth.max_value()
        self.value = 0

    def set_value(self, value: int):
        assert 0 <= value <= self.maxValue
        self.value = value

    def __str__(self):
        return hex(self.value)


class Counter:
    def __init__(self, bit_width: BitWidth):
        self.bitWidth = bit_width
        self.maxValue = self.bitWidth.max_value()
        self.value = 0

    def set_counter(self, address: int):
        assert 0 <= address <= self.maxValue
        self.value = address

    def get_counter(self):
        return self.value

    def inc_counter(self):
        self.value += 1
        if self.value > self.maxValue:
            self.value = 0

    def __str__(self):
        return hex(self.value)


class RAM:
    def __init__(self, address_width: BitWidth, data_width: BitWidth):
        self.addressWidth = address_width
        self.dataWidth = data_width
        self.addressMaxValue = self.addressWidth.max_value()
        self.dataMaxValue = self.dataWidth.max_value()
        self.memory = dict()

    def read(self, address: int):
        if not (0 <= address <= self.addressMaxValue):
            raise RuntimeError("Invalid Address: " + hex(address))
        return hex(self.memory.get(address, 0))

    def write(self, address: int, value: int):
        assert 0 <= address <= self.addressMaxValue
        assert 0 <= value <= self.dataMaxValue
        self.memory[address] = value

    def __str__(self):
        output_str = ""
        for row in range(32):
            for col in range(8):
                output_str += self.read(row * 8 + col) + "\t"
            output_str += "\n"
        return output_str


class CPU:
    def __init__(self):
        self.pc = Counter(BitWidth.EIGHT_BIT)
        self.reg_a = Register(BitWidth.EIGHT_BIT)
        self.reg_b = Register(BitWidth.EIGHT_BIT)
        self.reg_out = Register(BitWidth.EIGHT_BIT)
        self.ram_mem = RAM(BitWidth.EIGHT_BIT, BitWidth.EIGHT_BIT)
        self.reg_zero_carry = Register(BitWidth.TWO_BIT)

        self.enable = True

        self.current_instruction = ""
        self.current_instruction_decoded = ""

    def is_enabled(self):
        return self.enable

    def set_instructions(self, commands: list):
        commands = [int(c, 16) for c in commands]

        self.pc.set_counter(0)
        self.reg_a.set_value(0)
        self.reg_b.set_value(0)
        self.reg_out.set_value(0)

        for i in range(self.ram_mem.addressMaxValue + 1):
            self.ram_mem.write(i,
                               commands[i]
                               if i < len(commands)
                               else 0)

    def fetch(self):
        self.current_instruction = self.ram_mem.read(
            self.pc.get_counter())

    def decode(self):
        self.current_instruction_decoded = Instructions.find_instruction(
            self.current_instruction)
        self.pc.inc_counter()

    def execute(self):
        i = self.current_instruction_decoded

        if i == Instructions.HLT:
            self.enable = False

        elif i == Instructions.OUTL:
            arg = int(self.ram_mem.read(self.pc.get_counter()), 16)
            self.reg_out.set_value(arg)
            self.pc.inc_counter()

        elif i == Instructions.OUTR:
            arg = int(self.ram_mem.read(self.pc.get_counter()), 16)
            arg_decoded = int(self.ram_mem.read(arg), 16)
            self.reg_out.set_value(arg_decoded)
            self.pc.inc_counter()