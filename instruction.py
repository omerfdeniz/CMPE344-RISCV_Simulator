R_TYPE_OPCODE = "0110011"  # add, sub, and, or
I_TYPE_OPCODE = "0000011"  # ld
S_TYPE_OPCODE = "0100011"  # sd
SB_TYPE_OPCODE = "1100111"  # beq

INSTRUCTION_LEN = 64


def get_instructions(program_path):
    with open(program_path, 'r') as f:
        instruction_lines = [line.strip() for line in f.readlines()]

    instructions = []

    # for each assembly code line, put together the intruction fields 
    # according to its instruction type
    for instruction in instruction_lines:
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
                'immed': "00000000000000"
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
                'immed': "00000000000000"
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
                'immed': "00000000000000"
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
                'immed': "00000000000000"
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
            immed = f'{immed:012b}' # convert to 12 bit representation
            instruction_fields = {
                'funct7': "0000000",
                'rs2': 1,
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
            immed = f'{immed:012b}' # convert to 12 bit representation
            instruction_fields = {
                'funct7': "0000000",
                'rs2': rs2,
                'rs1': rs1,
                'funct3': '111',
                'rd': 1,
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
            # immediate is assummed to be given as an offset (TALK ABOUT THIS LATER)
            immed = int(regs[2])
            immed = f'{immed:012b}' # convert to 12 bit representation
            instruction_fields = {
                'funct7': "0000000",
                'rs2': rs2,
                'rs1': rs1,
                'funct3': '000',
                'rd': 1,
                'opcode': '1100111',
                'immed': immed
            }
        instructions.append(instruction_fields)
    return instructions


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


# returns int
def sign_extend(immed):
    # if immed is none
    if not immed:
        return 0
    sign_bit = immed[0]
    extended_offset = sign_bit * \
        (INSTRUCTION_LEN - 12) + immed[1:]
    return int(extended_offset, 2)  # "111" -> 7


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

def get_nop_instruction():
    return {
                'funct7': '0000000',
                'rs2': 1,
                'rs1': 1,
                'funct3': '000',
                'rd': 1,
                'opcode': '0000000',
                'immed': "00000000000000" # 12 bit
    }

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
