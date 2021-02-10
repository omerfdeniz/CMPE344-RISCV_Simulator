def get_instructions(program_path):
    with open(program_path, 'r') as f:
        instructions = [line.strip() for line in f.readlines()]
    for instruction in instructions:
        # convert to 32 bit
        R_type_register_fields = {'funct7': funct7, 'rs2': rs2, 'rs1': rs1, 'funct3': funct3, 'rd': rd, 'opcode': opcode}
    return [Instruction(instruction)]
class Instruction:
    def __init__(self, register_fields):
        self.register_fields = register_fields