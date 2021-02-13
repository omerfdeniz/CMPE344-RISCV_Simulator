from instruction import *
class Simulator:
    def __init__(self, program_path):
        self.INSTRUCTION_MEMORY = get_instructions(program_path) # list of Instruction objects
        self.REGISTERS = [0] * 32
        self.MEMORY = [0] * 1000
        self.PC = 0
        self.CLOCK = 0

        self.NOP_CONTROL = get_control_values("NOP") # all fields are 0

        self.IF_ID = {'control': self.NOP_CONTROL}
        self.ID_EX = {'control': self.NOP_CONTROL}
        self.EX_MEM = {'control': self.NOP_CONTROL}
        self.MEM_WB = {'control': self.NOP_CONTROL}
    
    def print_status(self):
        print(f"-----STATUS AT THE BEGINNING OF CLOCK = {self.CLOCK}-----")
        print(f"PC: {self.PC}")
        for i, val in enumerate(self.REGISTERS):
            print(f"x{i}: {val}",end=" ")
        print()
    def run(self):
        ALL_STAGES_NOP = True
        self.print_status()
        # while PC is valid and not all PHASES are None
        while(self.PC <= len(self.INSTRUCTION_MEMORY) or not ALL_STAGES_NOP):
            self.print_status()
            self.run_WB()
            self.run_EX()
            self.run_MEM()
            self.run_ID()
            self.run_IF()
            #break
            self.CLOCK += 1
            # if all registers are full of control values of zero
            if ((self.IF_ID['control'] == self.ID_EX['control'] and self.ID_EX['control'] == self.EX_MEM['control']) and
                (self.EX_MEM['control'] == self.MEM_WB['control'] and self.MEM_WB['control'] == self.NOP_CONTROL)):
                ALL_STAGES_NOP = True
            else:
                ALL_STAGES_NOP = False
                

    def run_WB(self):
        if self.MEM_WB['control'] == self.NOP_CONTROL:
            return
        # read from stage registers
        control = self.MEM_WB['control'] # read control from previous stage
        read_from_memory = self.MEM_WB['read_from_memory']
        ALU_result = self.MEM_WB['ALU_result']
        rd = self.MEM_WB['rd']
        # operate
        if control['RegWrite']:
            if control['MemToReg']: # ld: write the value at rs2+offset to rs1, else do not write to reg
                self.REGISTERS[rd] = read_from_memory
            else: # r-type: write the ALU_result to rd
                self.REGISTERS[rd] = ALU_result

    def run_MEM(self):
        if self.MEM_WB['control'] == self.NOP_CONTROL:
            return
        # read from stage registers
        control = self.EX_MEM['control'] # read control from previous stage
        PC_plus_OFFSET = self.EX_MEM['PC_plus_OFFSET']
        ALU_zero = self.EX_MEM['ALU_zero']
        ALU_result = self.EX_MEM['ALU_result']
        rs2_data = self.EX_MEM['rs2_data']
        rd = self.EX_MEM['rd']

        # operate
        if control['Branch'] and ALU_zero: # if a branch instruction and rs1_data-rs2_data==0
            self.PC = PC_plus_OFFSET
            # flush instructions in the IF, ID, EX when MEM is executing
            self.IF_ID['control'] = get_alu_control('NOP')
            self.ID_EX['control'] = get_alu_control('NOP')
            self.EX_MEM['control'] = get_alu_control('NOP')

        else:
            self.PC += 1

        if control('MemWrite'): # sd, will write to memory
            self.MEMORY[ALU_result] = rs2_data

        read_from_memory = None
        if control['MemRead']: # ld, will write to register file
            read_from_memory = self.MEMORY[ALU_result]
        
        # write to stage registers
        self.MEM_WB['read_from_memory'] = read_from_memory
        self.MEM_WB['ALU_result'] = ALU_result
        self.MEM_WB['control'] = control # pass control to next stage
        self.MEM_WB['rd'] = rd

    def run_EX(self):
        if self.MEM_WB['control'] == self.NOP_CONTROL:
            return
        # read from stage registers
        control = self.ID_EX['control'] # read control from previous stage
        PC = self.ID_EX['PC']
        rs1_data = self.ID_EX['rs1_data']
        rs2_data = self.ID_EX['rs2_data']
        imm_gen_offset = self.ID_EX['imm_gen_offset']
        funct_for_alu_control = self.ID_EX['funct_for_alu_control']
        rs1 = self.ID_EX['rs1']
        rs2 = self.ID_EX['rs2']
        rd = self.ID_EX['rd']

        # operate
        # forwarding unit
        # EX Hazard: pg 300 in the book
        ForwardA = "00"
        ForwardB = "00"
        if (self.EX_MEM['control']['RegWrite'] and (self.EX_MEM['rd'] != 0) and (self.EX_MEM['rd'] == self.ID_EX['rs1'])):
            ForwardA = "10"
        if (self.EX_MEM['control']['RegWrite'] and (self.EX_MEM['rd'] != 0) and (self.EX_MEM['rd'] == self.ID_EX['rs2'])):
            ForwardB = "10"

        # MEM Hazard: pg 301 in the book
        if (self.MEM_WB['control']['RegWrite'] and (self.MEM_WB['rd'] != 0) and not(self.EX_MEM['control']['RegWrite'] 
            and (self.EX_MEM['rd'] != 0) and (self.EX_MEM['rd'] == self.ID_EX['rs1'])) and (self.MEM_WB['rd'] == self.ID_EX['rs1'])):
            ForwardA = "01"
        if (self.MEM_WB['control']['RegWrite'] and (self.MEM_WB['rd'] != 0) and not(self.EX_MEM['control']['RegWrite'] 
            and (self.EX_MEM['rd'] != 0) and (self.EX_MEM['rd'] == self.ID_EX['rs2'])) and (self.MEM_WB['rd'] == self.ID_EX['rs2'])):
            ForwardB = "01"

        ALU_control = get_alu_control(control['ALU_Op1']+control['ALU_Op0'], funct_for_alu_control)
        PC_plus_OFFSET = PC + 2 * imm_gen_offset
        ALU_result = None
        if ForwardA == "00":
            param1 = rs1_data
        elif ForwardA == "10":
            param1 = self.EX_MEM['ALU_result'] 
        elif ForwardA == "01":
            if self.MEM_WB['control']['RegWrite']:
                read_from_memory = self.MEM_WB['read_from_memory']
                ALU_result = self.MEM_WB['ALU_result']
                if self.MEM_WB['control']['MemToReg']: # ld: write the value at rs2+offset to rs1, else do not write to reg
                    param1 = read_from_memory
                else: # r-type: write the ALU_result to rd
                    param1 = ALU_result

        if ForwardB == "00":
            param2 = rs2_data
        elif ForwardB == "10":
            param2 = self.EX_MEM['ALU_result'] 
        elif ForwardB == "01":
            if self.MEM_WB['control']['RegWrite']:
                read_from_memory = self.MEM_WB['read_from_memory']
                ALU_result = self.MEM_WB['ALU_result']
                if self.MEM_WB['control']['MemToReg']: # ld: write the value at rs2+offset to rs1, else do not write to reg
                    param2 = read_from_memory
                else: # r-type: write the ALU_result to rd
                    param2 = ALU_result

        if control['ALUSrc'] == 0: # r-format or beq
            ALU_result = perform_ALU_operation(ALU_control, param1, param2)
        elif control['ALUSrc'] == 1: # ld, sd: MEM[rs1]+offset
            ALU_result = perform_ALU_operation(ALU_control, param1, imm_gen_offset)
        ALU_zero = ALU_result == 0

        # write to stage registers
        self.EX_MEM['PC_plus_OFFSET'] = PC_plus_OFFSET
        self.EX_MEM['ALU_zero'] = ALU_zero
        self.EX_MEM['ALU_result'] = ALU_result
        self.EX_MEM['rs2_data'] = rs2_data
        self.EX_MEM['rd'] = rd
        self.EX_MEM['control'] = control # pass control to next stage

    def run_ID(self):
        if self.MEM_WB['control'] == self.NOP_CONTROL:
            return
        # read from stage registers
        instruction = self.IF_ID['instruction']
        PC = self.IF_ID['PC']

        # operate
        control = get_control_values(instruction) # calculate control
        imm_gen_offset = sign_extend(instruction)
        rs1 = instruction['rs1']
        rs2 = instruction['rs2']
        rs1_data = self.REGISTERS[rs1]
        rs2_data = self.REGISTERS[rs2]
        funct_for_alu_control = instruction['funct7'][1] + instruction['funct3'] # will be used for setting ALU control in EX
        rd = instruction['rd']

        # check for hazard ????? check the if statement
        if self.ID_EX['control']['MemRead'] and ((self.ID_EX['rd'] == self.IF_ID['rs1']) or (self.ID_EX['rd'] == self.IF_ID['rs2'])):
            # stall the pipeline
            self.ID_EX['control'] = self.NOP_CONTROL
        else:
            # write to stage registers
            self.ID_EX['control'] = control # pass control to next stage
            self.ID_EX['imm_gen_offset'] = imm_gen_offset
            
            self.ID_EX['rs1_data'] = rs1_data # not selecting the none values are handled by the control bits in EX stage
            self.ID_EX['rs2_data'] = rs2_data
            self.ID_EX['funct_for_alu_control'] = funct_for_alu_control
            self.ID_EX['rd'] = rd
            self.ID_EX['rs1'] = rs1
            self.ID_EX['rs2'] = rs2

    def run_IF(self):
        # write to stage registers
        if self.PC <= len(self.INSTRUCTION_MEMORY):
            self.IF_ID['instruction'] = self.INSTRUCTION_MEMORY[self.PC]
            print(self.IF_ID['instruction'])
            self.IF_ID['PC'] = self.PC
