import sys
from simulator import Simulator
program_path = sys.argv[1]
simulator = Simulator(program_path)
simulator.run()