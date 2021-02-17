from instruction import *
class Simulator:
    def __init__(self, program_path):
        self.REGISTERS = [0] * 32 # REGISTER FILE
        self.MEMORY = [0] * 1000 # MEMORY
        self.PC = 0 # PROGRAM COUNTER
        self.CLOCK = 1 # CLOCK
        self.WORD_LEN = 4
        self.FLUSH = False

        self.FINISHED_INSTRUCTION_COUNT = 0
        init_lines, self.INSTRUCTION_NAMES, self.INSTRUCTION_MEMORY = get_program(program_path) # read program
        self.parse_inits(init_lines) # parse register and memory init commands
        
        self.NOP_INSTRUCTION = get_nop_instruction() # get nop instruction which has all fields 0
        self.NOP_CONTROL = get_nop_control() # all fields are 0
        self.ALL_STAGES_NOP = True # used to check if all stages are having NOP instructions

        self.stalls = {} # dictinary that holds instruction name and their stall counts
        self.STALL_OCCURRED = False # flag to check stall occurred in the current clock

        self.INSTRUCTIONS_IN_PIPELINE = ['NOP'] * 5 # name of instructions in the pipeline, used only for reporting purposes

        # fields of the stage registers and their initial values for NOP instructions
        self.IF_ID = {"PC": 0, "instruction": self.NOP_INSTRUCTION}
        self.ID_EX = {"PC": 0, "rs1_data": 0, "rs2_data": 0, 
            "imm_gen_offset": 0, "funct_for_alu_control": "0000", "rd": 0, 
            "control": self.NOP_CONTROL, "rs1": None, "rs2": None}
        self.EX_MEM = {"PC_plus_OFFSET": 0, "ALU_zero": 0, "ALU_result": 0, "rs1_data": 0, "rd": None,
            "control": self.NOP_CONTROL}
        self.MEM_WB = {"read_from_memory": 0, "ALU_result": 0, "rd": None, "control": self.NOP_CONTROL}
    
    # parse initializing commands for the program
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

    # writes to register if not x0 and parameters are not None
    def write_to_register(self, index, value):
        if index == 0 or index == None or value == None:
            return
        else:
            self.REGISTERS[index] = value

    # reads from register
    def read_register(self, index):
        if index == None or index >= len(self.REGISTERS):
            return 0
        else:
            return self.REGISTERS[index]

    # prints the status of the class variables for the current clock cycle
    def print_status(self):
        for i, val in enumerate(self.REGISTERS):
            if val != 0:
                print(f"x{i}: {val}",end=" ") # FOR DEBUG PURPOSES
        for i, val in enumerate(self.MEMORY):
            if val != 0:
                print(f"m[{i}]: {val}",end=" ") # FOR DEBUG PURPOSES
        print()
    
    # prints the final report for the program
    def print_final_report(self):
        print()
        print(f"-----FINAL REPORT-----")
        print(f"Total # of Clock Cycles: {self.CLOCK}")
        CPI = self.CLOCK / self.FINISHED_INSTRUCTION_COUNT
        print(f"Cycles per Instruction(CPI): {CPI}")
        if len(self.stalls) == 0:
            print("No stall occurred.")
        else:
            print(f"Total # of Stalls: {len(self.stalls)}")
            print(f"Instructions and # of Stalls Caused: ")
            for i, num in self.stalls.items():
                print(f"---> {i}: {num}")

    # main method to run the simulator
    def run(self):
        print(f"-----STATUS AT THE BEGINNING-----")
        print(*self.INSTRUCTIONS_IN_PIPELINE, sep=' | ')
        self.print_status()
        # while PC is valid and not all STAGES are filled with NOPs
        while(self.PC < len(self.INSTRUCTION_MEMORY) or not self.ALL_STAGES_NOP):
            PC_running = self.PC
            # run each stage separately before updating the stage registers
            self.run_WB()
            output_for_MEM_WB = self.run_MEM()
            output_for_EX_MEM = self.run_EX()
            output_for_ID_EX = self.run_ID()
            output_for_IF_ID = self.run_IF()

            # update the stage registers
            if not self.STALL_OCCURRED:
                self.IF_ID = output_for_IF_ID
            else: # self.IF_ID should be preserved if stall is occurred and instruction is fetched
                self.STALL_OCCURRED = False
            self.ID_EX = output_for_ID_EX
            self.EX_MEM = output_for_EX_MEM
            self.MEM_WB = output_for_MEM_WB
            # fill stage registers with NOP
            if self.FLUSH:
                self.PC = self.PC_plus_OFFSET
                self.IF_ID['instruction'] = self.NOP_INSTRUCTION
                self.ID_EX['control'] = self.NOP_CONTROL
                self.EX_MEM['control'] = self.NOP_CONTROL
                self.FLUSH = False


            print(f"-----STATUS AT THE END OF CLOCK = {self.CLOCK}-----")
            print(*self.INSTRUCTIONS_IN_PIPELINE, sep=' | ', end="")
            print(f" is run at PC = {PC_running}")
            self.print_status()
            #break
            self.CLOCK += 1
            # if all registers are full of control values of zero, namely NOPs update the flag
            if ((self.IF_ID['instruction'] == self.NOP_INSTRUCTION and self.ID_EX['control'] == self.EX_MEM['control']) and
                (self.EX_MEM['control'] == self.MEM_WB['control'] and self.MEM_WB['control'] == self.NOP_CONTROL)):
                self.ALL_STAGES_NOP = True
            else:
                self.ALL_STAGES_NOP = False
        self.CLOCK -= 1
        self.print_final_report()
    
    # runs the WB stage
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
        if control != self.NOP_CONTROL:
            self.FINISHED_INSTRUCTION_COUNT += 1

    # runs the MEM stage
    def run_MEM(self):
        # read from stage registers
        control = self.EX_MEM['control'] # read control from previous stage
        PC_plus_OFFSET = self.EX_MEM['PC_plus_OFFSET']
        ALU_zero = self.EX_MEM['ALU_zero']
        ALU_result = self.EX_MEM['ALU_result']
        rs1_data = self.EX_MEM['rs1_data']
        rd = self.EX_MEM['rd']

        # operate
        if control['Branch'] and ALU_zero: # if a branch instruction and rs1_data-rs2_data == 0
            self.PC_plus_OFFSET = PC_plus_OFFSET
            # flush instructions in the IF, ID, EX when MEM is executing
            self.FLUSH = True
            self.INSTRUCTIONS_IN_PIPELINE = ['NOP', 'NOP'] + self.INSTRUCTIONS_IN_PIPELINE[2:]
            stall_instruction = self.INSTRUCTIONS_IN_PIPELINE[2]
            if stall_instruction in self.stalls:
                self.stalls[stall_instruction] += 3 # since flush adds two stalls to the pipeline
            else:
                self.stalls[stall_instruction] = 3
        if control['MemWrite']: # sd, will write to memory
            self.MEMORY[ALU_result] = rs1_data

        read_from_memory = None
        if control['MemRead']: # ld, will write to register file
            read_from_memory = self.MEMORY[ALU_result]
        
        # return the output to be written to MEM_WB
        return {"read_from_memory": read_from_memory, "ALU_result": ALU_result, "rd": rd, "control": control}

    # runs the EX stage
    def run_EX(self):
        # read from stage registers
        control = self.ID_EX['control'] 
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
        PC_plus_OFFSET = PC + 2 * imm_gen_offset # calculate PC offset
        ALU_result = None
        param1 = 0
        param2 = 0
        if ForwardA == "00":
            param1 = rs1_data
        elif ForwardA == "10":
            rs1_data = self.EX_MEM['ALU_result']
            param1 = rs1_data 
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
            rs2_data = self.EX_MEM['ALU_result']
            param2 = rs2_data 
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
        elif control['ALUSrc'] == 1: # ld, sd
            if control['MemWrite'] == 1: # sd: rs2_data+offset
                ALU_result = perform_ALU_operation(ALU_control, param2, imm_gen_offset)
            else: # ld: rs1_data+offset
                ALU_result = perform_ALU_operation(ALU_control, param1, imm_gen_offset)
        ALU_zero = ALU_result == 0

        # return the output to be written to EX_MEM
        return {"PC_plus_OFFSET": PC_plus_OFFSET, "ALU_zero": ALU_zero, 
            "ALU_result": ALU_result, "rs1_data": rs1_data, "rd": rd, "control": control}

    # runs the ID stage
    def run_ID(self):
        # read from stage registers
        instruction = self.IF_ID['instruction']
        PC = self.IF_ID['PC']

        # operate
        control = get_control_values(instruction) # calculate control
        imm_gen_offset = instruction['immed'] # sign extend the offset
        rs1 = instruction['rs1']
        rs2 = instruction['rs2']
        rs1_data = self.read_register(rs1)
        rs2_data = self.read_register(rs2)
        # will be used for setting ALU control in EX
        funct_for_alu_control = get_funct_for_alu_control(instruction)
        rd = instruction['rd']

        # check for hazard
        if self.ID_EX['control']['MemRead'] and ((self.ID_EX['rd'] == self.IF_ID['instruction']['rs1']) or (self.ID_EX['rd'] == self.IF_ID['instruction']['rs2'])):
            self.STALL_OCCURRED = True
            self.INSTRUCTIONS_IN_PIPELINE = [self.INSTRUCTIONS_IN_PIPELINE[0]] + ['NOP'] + self.INSTRUCTIONS_IN_PIPELINE[1:-1]
            stall_instruction = self.INSTRUCTIONS_IN_PIPELINE[2] # instruction in the ex stage causes the hazard
            # if already defined
            if stall_instruction in self.stalls:
                self.stalls[stall_instruction] += 1
            else:
                self.stalls[stall_instruction] = 1
            # return the output to be written to ID_EX
            return {"PC": 0, "rs1_data": 0, "rs2_data": 0, 
            "imm_gen_offset": 0, "funct_for_alu_control": "0000", "rd": 0, 
            "control": self.NOP_CONTROL, "rs1": None, "rs2": None}
        else:
            # return the output to be written to ID_EX
            return {"PC": PC, "rs1_data": rs1_data, "rs2_data": rs2_data, 
            "imm_gen_offset": imm_gen_offset, "funct_for_alu_control": funct_for_alu_control, "rd": rd, 
            "control": control, "rs1": rs1, "rs2": rs2}

    # runs the IF stage
    def run_IF(self):
        # if not all instructions are entered the pipeline
        if self.FLUSH:
            self.INSTRUCTIONS_IN_PIPELINE = ['NOP'] + self.INSTRUCTIONS_IN_PIPELINE[:-1]
            return {'PC':self.PC,'instruction': self.NOP_INSTRUCTION}
        if self.PC < len(self.INSTRUCTION_MEMORY) and not self.STALL_OCCURRED:
            new_instruction = self.INSTRUCTION_MEMORY[self.PC]
            self.INSTRUCTIONS_IN_PIPELINE = [self.INSTRUCTION_NAMES[self.PC // self.WORD_LEN]] + self.INSTRUCTIONS_IN_PIPELINE[:-1]
            PC = self.PC 
            self.PC += self.WORD_LEN
            return {'PC':PC, 'instruction': new_instruction, 'rs1': new_instruction['rs1'], 'rs2': new_instruction['rs2']}
        else: # add NOP to the pipeline
            if not self.STALL_OCCURRED:
                self.INSTRUCTIONS_IN_PIPELINE = ['NOP'] + self.INSTRUCTIONS_IN_PIPELINE[:-1]
            return {'PC':self.PC,'instruction': self.NOP_INSTRUCTION}
