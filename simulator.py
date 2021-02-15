from instruction import *
class Simulator:
    def __init__(self, program_path):
        self.REGISTERS = [0] * 32
        self.MEMORY = [0] * 1000
        self.PC = 0
        self.CLOCK = 1

        init_lines, self.INSTRUCTION_MEMORY = get_instructions(program_path) # list of Instruction objects
        self.parse_inits(init_lines)

        self.NOP_INSTRUCTION = get_nop_instruction()
        self.NOP_CONTROL = get_nop_control() # all fields are 0
        self.ALL_STAGES_NOP = True

        self.IF_ID = {"PC": 0, "instruction": self.NOP_INSTRUCTION, "rs1": 1, "rs2": 1}
        self.ID_EX = {"PC": 0, "rs1_data": 0, "rs2_data": 0, 
            "imm_gen_offset": 0, "funct_for_alu_control": "0000", "rd": 0, 
            "control": self.NOP_CONTROL, "rs1": None, "rs2": None}
        self.EX_MEM = {"PC_plus_OFFSET": 0, "ALU_zero": 0, "ALU_result": 0, "rs1_data": 0, "rd": None,
            "control": self.NOP_CONTROL}
        self.MEM_WB = {"read_from_memory": 0, "ALU_result": 0, "rd": None, "control": self.NOP_CONTROL}
    
    def parse_inits(self, init_lines):
        for init in init_lines:
            init = init.replace(" ","")
            if init[0] == 'x': # write to register file
                eq_index = init.index('=')
                reg = int(init[1:eq_index])
                val = int(init[eq_index+1:])
                self.write_to_register(reg, val)
            if init[0] == 'm': # write to memory
                eq_index = init.index('=')
                mem_index = int(init[init.index('[')+1:init.index(']')])
                val = int(init[eq_index+1:])
                self.MEMORY[mem_index] = val
    def write_to_register(self, index, value):
        if index == 0 or index == None or value == None:
            return
        else:
            self.REGISTERS[index] = value

    def read_register(self, index):
        if index == None or index >= len(self.REGISTERS):
            return 0
        else:
            return self.REGISTERS[index]
    def print_status(self):
        print(f"PC: {self.PC}")
        for i, val in enumerate(self.REGISTERS):
            """if i == 16:
                print()
            print(f"x{i}: {val}",end=" ")"""
            if val != 0:
                print(f"x{i}: {val}",end=" ") # FOR DEBUG PURPOSES
        print()
    
    def print_final_report(self):
        print(f"-----FINAL REPORT-----")
        print(f"Total # of Clock Cycles: {self.CLOCK}")
        CPI = self.CLOCK / len(self.INSTRUCTION_MEMORY)
        print(f"Cycles per Instruction(CPI): {CPI}")
        num_stalls = 0
        print(f"Total # of Stalls: {num_stalls}")
        instructions_causing_stalls = [('add', 2)]
        print(f"Instructions and Caused Stall numbers:")
        for i, num in instructions_causing_stalls:
            print(f"{i}: {num}")

    def run(self):
        print(f"-----STATUS AT THE BEGINNING-----")
        self.print_status()
        # while PC is valid and not all STAGES are filled with NOPs
        while(self.PC < len(self.INSTRUCTION_MEMORY) or not self.ALL_STAGES_NOP):
            self.run_WB()
            self.run_MEM()
            self.run_EX()
            self.run_ID()
            self.run_IF()
            print(f"-----STATUS AT THE END OF CLOCK = {self.CLOCK}-----")
            self.print_status()
            #break
            self.CLOCK += 1
            # if all registers are full of control values of zero
            if ((self.IF_ID['instruction'] == self.NOP_INSTRUCTION and self.ID_EX['control'] == self.EX_MEM['control']) and
                (self.EX_MEM['control'] == self.MEM_WB['control'] and self.MEM_WB['control'] == self.NOP_CONTROL)):
                self.ALL_STAGES_NOP = True
            else:
                self.ALL_STAGES_NOP = False
        self.print_final_report()
        

    def run_WB(self):
        # read from stage registers
        control = self.MEM_WB['control'] # read control from previous stage
        read_from_memory = self.MEM_WB['read_from_memory']
        ALU_result = self.MEM_WB['ALU_result']
        rd = self.MEM_WB['rd']
        # operate
        if control['RegWrite']:
            if control['MemToReg']: # ld: write the value at rs2+offset to rs1, else do not write to reg
                self.write_to_register(rd, read_from_memory)
            else: # r-type: write the ALU_result to rd
                self.write_to_register(rd, ALU_result)

    def run_MEM(self):
        # read from stage registers
        control = self.EX_MEM['control'] # read control from previous stage
        PC_plus_OFFSET = self.EX_MEM['PC_plus_OFFSET']
        ALU_zero = self.EX_MEM['ALU_zero']
        ALU_result = self.EX_MEM['ALU_result']
        rs1_data = self.EX_MEM['rs1_data']
        rd = self.EX_MEM['rd']

        # operate
        if control['Branch'] and ALU_zero: # if a branch instruction and rs1_data-rs2_data==0
            self.PC = PC_plus_OFFSET
            # flush instructions in the IF, ID, EX when MEM is executing
            self.IF_ID['instruction'] = self.NOP_INSTRUCTION
            self.ID_EX['control'] = self.NOP_CONTROL
            self.EX_MEM['control'] = self.NOP_CONTROL

        if control['MemWrite']: # sd, will write to memory
            self.MEMORY[ALU_result] = rs1_data

        read_from_memory = None
        if control['MemRead']: # ld, will write to register file
            read_from_memory = self.MEMORY[ALU_result]
        
        # write to stage registers
        self.MEM_WB = {"read_from_memory": read_from_memory, "ALU_result": ALU_result, "rd": rd, "control": control}

    def run_EX(self):
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

        ALU_control = get_alu_control(str(control['ALUOp1'])+str(control['ALUOp0']), funct_for_alu_control)
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
            ALU_result = perform_ALU_operation(ALU_control, param2, imm_gen_offset)
        ALU_zero = ALU_result == 0

        # write to stage registers
        self.EX_MEM = {"PC_plus_OFFSET": PC_plus_OFFSET, "ALU_zero": ALU_zero, 
            "ALU_result": ALU_result, "rs1_data": rs1_data, "rd": rd, "control": control}

    def run_ID(self):
        # read from stage registers
        instruction = self.IF_ID['instruction']
        PC = self.IF_ID['PC']

        # operate
        control = get_control_values(instruction) # calculate control
        imm_gen_offset = sign_extend(instruction)
        rs1 = instruction['rs1']
        rs2 = instruction['rs2']
        rs1_data = self.read_register(rs1)
        rs2_data = self.read_register(rs2)
        # will be used for setting ALU control in EX
        funct_for_alu_control = get_funct_for_alu_control(instruction)
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
            self.ID_EX['rs1'] = rs1 # ????
            self.ID_EX['rs2'] = rs2 # ????

    def run_IF(self):
        # write to stage registers
        if self.PC < len(self.INSTRUCTION_MEMORY):
            self.IF_ID['instruction'] = self.INSTRUCTION_MEMORY[self.PC]
            self.IF_ID['PC'] = self.PC
            self.PC += 1
        else:
            self.IF_ID['instruction'] = self.NOP_INSTRUCTION
            self.IF_ID['PC'] = self.PC
