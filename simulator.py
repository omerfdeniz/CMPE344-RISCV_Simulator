from instruction import *
class Simulator:
    def __init__(self, program_path):
        self.INSTRUCTION_MEMORY = get_instructions(program_path) # list of Instruction objects
        self.REGISTERS = [0] * 32
        self.MEMORY = [0] * 1000
        self.PC = 0
        self.CLOCK = 0

        self.PHASE_INSTRUCTIONS = {'IF': None, 'ID': None, 'EX': None, 'MEM': None, 'WB': None}

        self.IF_ID = None
        self.ID_EX = None
        self.EX_MEM = None
        self.MEM_WB = None
        self.IF_ID = None

    def run(self):
        # while PC is valid and not all PHASES are None
        while(self.PC <= len(self.INSTRUCTION_MEMORY) or sum(self.PHASES.values()) != 0):
            if self.PHASE_INSTRUCTIONS['WB']:
                self.REGISTERS[]
                pass
            if self.PHASE_INSTRUCTIONS['MEM']:
                pass
            if self.PHASE_INSTRUCTIONS['EX']:
                pass
            if self.PHASE_INSTRUCTIONS['ID']:
                opcode = self.PHASE_INSTRUCTIONS['ID'][25:]
                self.PHASE_INSTRUCTIONS['ID'].set_control_values(opcode)
                pass

            self.PHASE_INSTRUCTIONS['WB'] = self.PHASE_INSTRUCTIONS['MEM']
            self.PHASE_INSTRUCTIONS['MEM'] = self.PHASE_INSTRUCTIONS['EX']
            self.PHASE_INSTRUCTIONS['EX'] = self.PHASE_INSTRUCTIONS['ID']
            self.PHASE_INSTRUCTIONS['ID'] = self.PHASE_INSTRUCTIONS['IF']

            if self.PC <= len(self.INSTRUCTION_MEMORY):
                self.PHASE_INSTRUCTIONS['IF'] = self.INSTRUCTION_MEMORY[self.PC]
            else:
                self.PHASE_INSTRUCTIONS['IF'] = None

            if self.PC >= len(self.INSTRUCTION_MEMORY) and :
                return