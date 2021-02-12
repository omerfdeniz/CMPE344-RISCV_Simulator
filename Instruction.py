def get_instructions(program_path):
    with open(program_path, 'r') as f:
        instruction_lines = [line.strip() for line in f.readlines()]

    instructions = []

    # for each assembly code line, create an Instruction object instance
    for instruction in instruction_lines:
        instruction_name = instruction.split(' ')[0]
        intstruction_fields = {}

        if instruction_name == 'add':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rd = int(regs[0][1:])
            rs1 = int(regs[1][1:])
            rs2 = int(regs[2][1:])
            intstruction_fields = {
                'funct7': '0000000',
                'rs2': rs2,
                'rs1': rs1, 
                'funct3': '000', 
                'rd': rd, 
                'opcode': '0110011'
                }
        elif instruction_name == 'and':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rd = int(regs[0][1:])
            rs1 = int(regs[1][1:])
            rs2 = int(regs[2][1:])
            intstruction_fields = {
                'funct7': '0000000',
                'rs2': rs2,
                'rs1': rs1, 
                'funct3': '111', 
                'rd': rd, 
                'opcode': '0110011'
                }
        elif instruction_name == 'or':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rd = int(regs[0][1:])
            rs1 = int(regs[1][1:])
            rs2 = int(regs[2][1:])
            intstruction_fields = {
                'funct7': '0000000',
                'rs2': rs2,
                'rs1': rs1, 
                'funct3': '110', 
                'rd': rd, 
                'opcode': '0110011'
                }
        elif instruction_name == 'sub':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rd = int(regs[0][1:])
            rs1 = int(regs[1][1:])
            rs2 = int(regs[2][1:])
            intstruction_fields = {
                'funct7': '0100000',
                'rs2': rs2,
                'rs1': rs1, 
                'funct3': '000', 
                'rd': rd, 
                'opcode': '0110011'
                }
        """
        TO BE COMPLETED
        elif instruction_name == 'ld':
        elif instruction_name == 'sd':
        elif instruction_name == 'beq'

        instructions.append(Instruction(instruction_fields))"""
    return instructions

def perform_ALU_operation(ALU_control, param1, param2):
    pass

def get_control_values(instruction):
    opcode = instruction['opcode']
    R_TYPE_OPCODE = "0110011" # add, sub, and, or
    I_TYPE_OPCODE = "0000011" # ld
    S_TYPE_OPCODE = "0100011" # sd
    SB_TYPE_OPCODE = "1100111" # beq
    control_values = {} # fill this
    if (opcode == R_TYPE_OPCODE):
        control_values = {
            'ALUSrc': 0,
            'MemToReg': 0,
            'RegWrite': 1,
            'MemRead': 0,
            'MemWrite': 0,
            'Branch': 0,
            'ALUOp1': 1,
            'ALUOp0': 0
        }
    elif (opcode == I_TYPE_OPCODE):
        control_values = {
            'ALUSrc': 1,
            'MemToReg': 1,
            'RegWrite': 1,
            'MemRead': 1,
            'MemWrite': 0,
            'Branch': 0,
            'ALUOp1': 0,
            'ALUOp0': 0
        }
    elif (opcode == S_TYPE_OPCODE):
        control_values = {
            'ALUSrc': 1,
            'RegWrite': 0,
            'MemRead': 0,
            'MemWrite': 1,
            'Branch': 0,
            'ALUOp1': 0,
            'ALUOp0': 0
        }
    elif (opcode == SB_TYPE_OPCODE):
        control_values = {
            'ALUSrc': 0,
            'RegWrite': 0,
            'MemRead': 0,
            'MemWrite': 0,
            'Branch': 1,
            'ALUOp1': 0,
            'ALUOp0': 1
        }       
    self.control_values = control_values