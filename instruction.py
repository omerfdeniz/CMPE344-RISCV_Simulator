R_TYPE_OPCODE = "0110011"  # add, sub, and, or
I_TYPE_OPCODE = "0000011"  # ld
S_TYPE_OPCODE = "0100011"  # sd
SB_TYPE_OPCODE = "1100111"  # beq

INSTRUCTION_LEN = 64
WORD_LEN = 4

# parses the instructions to their fields
def get_program(program_path):
    with open(program_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    ind = -1
    if '---' in lines:
        ind = lines.index('---')
    init_lines = lines[:ind]
    program_lines = lines[ind+1:]

    BRANCH_TABLE = {}
    instruction_fullnames = []
    instructions = []
    # extract labels
    for i, instruction in enumerate(program_lines):
        if instruction.endswith(':'): # if it is a label
            instruction_name = instruction.split(' ')[0]
            BRANCH_TABLE[instruction_name[:-1]] = i
        else:
            instruction_fullnames.append(instruction)

    # for each program line
    for i, line in enumerate(instruction_fullnames):
        # continue if it is a label
        if line.endswith(':'):
            continue
        instruction = line
        instruction_name = instruction.split(' ')[0]
        instruction_fields = {}

        if instruction_name == 'add':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rd = int(regs[0][1:])
            rs1 = int(regs[1][1:])
            rs2 = int(regs[2][1:])
            instruction_fields = {
                'funct7': '0000000',
                'rs2': rs2,
                'rs1': rs1,
                'funct3': '000',
                'rd': rd,
                'opcode': '0110011',
                'immed': 0
            }
        elif instruction_name == 'and':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(
                ' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rd = int(regs[0][1:])
            rs1 = int(regs[1][1:])
            rs2 = int(regs[2][1:])
            instruction_fields = {
                'funct7': '0000000',
                'rs2': rs2,
                'rs1': rs1,
                'funct3': '111',
                'rd': rd,
                'opcode': '0110011',
                'immed': 0
            }
        elif instruction_name == 'or':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(
                ' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rd = int(regs[0][1:])
            rs1 = int(regs[1][1:])
            rs2 = int(regs[2][1:])
            instruction_fields = {
                'funct7': '0000000',
                'rs2': rs2,
                'rs1': rs1,
                'funct3': '110',
                'rd': rd,
                'opcode': '0110011',
                'immed': 0
            }
        elif instruction_name == 'sub':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(
                ' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rd = int(regs[0][1:])
            rs1 = int(regs[1][1:])
            rs2 = int(regs[2][1:])
            instruction_fields = {
                'funct7': '0100000',
                'rs2': rs2,
                'rs1': rs1,
                'funct3': '000',
                'rd': rd,
                'opcode': '0110011',
                'immed': 0
            }
        elif instruction_name == 'ld':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(
                ' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rd = int(regs[0][1:])
            # find rs1 by looking inside the parentheses after the immediate
            rs1 = int(regs[1][regs[1].find('(') + 1: regs[1].find(')')][1:])
            # find immed by looking at the string just before the parentheses
            immed = int(regs[1][:regs[1].find('(')])
            #immed = f'{immed:012b}' # convert to 12 bit representation
            instruction_fields = {
                'funct7': None,
                'rs2': None,
                'rs1': rs1,
                'funct3': '011',
                'rd': rd,
                'opcode': '0000011',
                'immed': immed
            }
        elif instruction_name == 'sd':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(
                ' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rs1 = int(regs[0][1:])
            # find rs2 by looking inside the parentheses after the immediate
            rs2 = int(regs[1][regs[1].find('(') + 1: regs[1].find(')')][1:])
            # find immed by looking at the string just before the parentheses
            immed = int(regs[1][:regs[1].find('(')])
            #immed = f'{immed:012b}' # convert to 12 bit representation
            instruction_fields = {
                'funct7': None,
                'rs2': rs2,
                'rs1': rs1,
                'funct3': '111',
                'rd': None,
                'opcode': '0100011',
                'immed': immed
            }
        elif instruction_name == 'beq':
            # get the register names from assembly instruction string
            regs = instruction[instruction.find(
                ' ') + 1:].replace(' ', '').split(',')

            # fill the correct fields for this instruction
            rs1 = int(regs[0][1:])
            rs2 = int(regs[1][1:])
            
            next_instruction = program_lines[BRANCH_TABLE[regs[2]]+1]
            immed = (instruction_fullnames.index(next_instruction) - i) * WORD_LEN // 2
            #immed = f'{immed:012b}' # convert to 12 bit representation
            instruction_fields = {
                'funct7': None,
                'rs2': rs2,
                'rs1': rs1,
                'funct3': '000',
                'rd': None,
                'opcode': '1100111',
                'immed': immed
            }
        instructions += [instruction_fields, 0, 0, 0]
    return init_lines, instruction_fullnames, instructions

# performs ALU operation according to ALU_control and params
def perform_ALU_operation(ALU_control, param1, param2):
    if ALU_control == '0010':
        # function ADD
        return param1 + param2
    elif ALU_control == '0110':
        # function SUB
        return param1 - param2
    elif ALU_control == '0000':
        # function AND
        return param1 & param2
    elif ALU_control == '0001':
        # function OR
        return param1 | param2
    else:
        return None

# returns the alu_control bits for the given ALU_op and funct_for_alu_control
def get_alu_control(ALU_op, funct_for_alu_control):  # used fig 4.12
    if ALU_op == "00" or ALU_op == "01":
        return ALU_op + "10"
    else:
        if funct_for_alu_control[0] == "0" and funct_for_alu_control[1:] == "000":
            return "0010"
        elif funct_for_alu_control[0] == "1" and funct_for_alu_control[1:] == "000":
            return "0110"
        elif funct_for_alu_control[0] == "0" and funct_for_alu_control[1:] == "111":
            return "0000"
        else:
            return "0001"

# get nop instruction fields
def get_nop_instruction():
    return {
                'funct7': '0000000',
                'rs2': 0,
                'rs1': 0,
                'funct3': '000',
                'rd': 0,
                'opcode': '0000000',
                'immed': 0 # 12 bit
    }
# get nop control values
def get_nop_control():
    return {
            'ALUSrc': 0,
            'MemToReg': 0,
            'RegWrite': 0,
            'MemRead': 0,
            'MemWrite': 0,
            'Branch': 0,
            'ALUOp1': 0,
            'ALUOp0': 0
        }
# get control values for the given instruction
def get_control_values(instruction):
    if instruction == get_nop_instruction():
        return get_nop_control()
    opcode = instruction['opcode']
    control_values = {}
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
    return control_values

# calculate the instruction[30,14-12] which is used in finding ALU_control for the given instruction
def get_funct_for_alu_control(instruction):
    if instruction['funct7'] != None:
        return instruction['funct7'][1] + instruction['funct3']
    else:
        return "0000"