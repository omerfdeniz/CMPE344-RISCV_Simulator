from instruction import *
class Simulator:
    def __init__(self, program_path):
        self.INSTRUCTION_MEMORY = get_instructions(program_path) # list of Instruction objects
        self.REGISTERS = [0] * 32
        self.MEMORY = [0] * 1000
        self.PC = -1
        self.CLOCK = 0
        self.PCSrc = 0

        self.PHASE_INSTRUCTIONS = {'IF': None, 'ID': None, 'EX': None, 'MEM': None, 'WB': None}

        self.IF_ID = {}
        self.ID_EX = {}
        self.EX_MEM = {}
        self.MEM_WB = {}
        self.IF_ID = {}

    def run(self):
        # while PC is valid and not all PHASES are None
        while(self.PC <= len(self.INSTRUCTION_MEMORY) or sum(self.PHASES.values()) != 0):
            self.PC = self.EX_MEM['PC+Offset'] if self.PCSrc else self.PC+1
            #WB

            #MEM
            if self.EX_MEM['ALU_zero'] and self.EX_MEM['control']['Branch']: # if a branch instruction and rs1_data-rs2_data==0
                self.PCSrc = 1
            else:
                self.PCSrc = 0
            
            if self.EX_MEM['control']['MemRead']: # ld, will write to register file
                self.MEM_WB['read_from_memory'] = self.MEMORY[self.EX_MEM['ALU_result']]
            #EX
            ALU_result = None
            if self.ID_EX['control']['ALUSrc'] == 0:
                ALU_result = perform_ALU_operation(self.ID_EX['rs1_data'], self.ID_EX['rs2_data'])
            else:
                ALU_result = perform_ALU_operation(self.ID_EX['rs1_data'], self.ID_EX['im_gen?????'])
            self.EX_MEM['ALU_zero'] = ALU_result == 0
            self.EX_MEM['ALU_result'] = ALU_result
            self.EX_MEM['PC+Offset'] = self.EX_MEM['PC'] + self.ID_EX['im_gen?????'] * 2

            if self.ID_EX['rs2_data']:
                self.EX_MEM['rs2_data'] = self.ID_EX['rs2_data']

            self.EX_MEM['control'] = self.ID_EX['control']

            # ID
            self.ID_EX['control'] = get_control_values(self.IF_ID['instruction'])
            self.ID_EX['PC'] = self.IF_ID['PC']

            if 'rs1' in self.ID_EX['instruction']:
                self.ID_EX['rs1_data'] = self.REGISTERS[self.ID_EX['instruction']['rs1']]
            if 'rs2' in self.ID_EX['instruction']:
                self.ID_EX['rs2_data'] = self.REGISTERS[self.ID_EX['instruction']['rs2']]

            # IF
            if self.PC <= len(self.INSTRUCTION_MEMORY):
                self.IF_ID['instruction'] = self.INSTRUCTION_MEMORY[self.PC]
                self.IF_ID['PC'] = self.PC