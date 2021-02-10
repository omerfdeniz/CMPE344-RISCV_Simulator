from instruction import *
class Simulator:
    def __init__(self, program_path):
        self.INSTRUCTION_MEMORY = get_instructions(program_path) # list of Instruction objects
        self.REGISTERS = [0] * 32
        self.MEMORY = [0] * 1000
        self.PC = 0
        self.CLOCK = 0

        self.IF_PHASE = None
        self.ID_PHASE = None
        self.EX_PHASE = None
        self.MEM_PHASE = None
        self.WB_PHASE = None

    def run(self):
        pass