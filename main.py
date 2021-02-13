import sys
from simulator import Simulator
#program_path = sys.argv[1]
program_path = "program.txt"
simulator = Simulator(program_path)
simulator.run()

"""
def do():
    print("in do")
    print(4)
a = 5
print(a)
a = 10
do()
b = 7
print(a,b)
"""