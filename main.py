import sys
from simulator import Simulator
#program_path = sys.argv[1]
program_path = "program.txt"
simulator = Simulator(program_path)
simulator.run()