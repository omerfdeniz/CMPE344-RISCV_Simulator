with open("program.txt", 'r') as f:
    instructions = [line.strip() for line in f.readlines()]

print(instructions)