from assembly_line import AssemblyLine
from simulated_annealing_for_alb import SimulatedAnnealingForALB
import time

filenames = ['./input/TONGE70.IN2', './input/WEE-MAG.IN2', './input/ARC83.IN2', './input/SCHOLL.IN2']
number_of_workstations = {}
number_of_workstations['./input/TONGE70.IN2'] = [3, 4, 5, 6, 7, 8, 9, 10, 20]
number_of_workstations['./input/ARC83.IN2'] = [6]
number_of_workstations['./input/WEE-MAG.IN2'] = [3, 4, 5, 6, 7, 12, 13, 14, 17]
number_of_workstations['./input/SCHOLL.IN2'] = [25, 35]

parameters = {}
parameters['./input/TONGE70.IN2'] = [0.6, 0.75]
parameters['./input/WEE-MAG.IN2'] = [0.7, 0.8]
parameters['./input/ARC83.IN2'] = [0.65, 0.95]
parameters['./input/SCHOLL.IN2'] = [0.65, 0.8]

print("dataset,workstations,solução,tempo execução")

for filename in filenames:
    for i in number_of_workstations[filename]:
        time_start = time.time()
        file = open(filename)
        assembly_line = AssemblyLine(file, i)
        file.close()
        simulated_annealing_for_alb = SimulatedAnnealingForALB(assembly_line)

        initial_temperature = simulated_annealing_for_alb.get_cycle_time_current_solution()
        maximum_number_of_disturbances = assembly_line.get_number_of_workstations() * assembly_line.get_number_of_tasks()
        cooling_rate = parameters[filename]

        simulated_annealing_for_alb.run(initial_temperature, maximum_number_of_disturbances, cooling_rate)

        time_end = time.time()
        solution = simulated_annealing_for_alb.get_cycle_time_optimal_solution()
        execution_time = time_end - time_start

        print("%s,%d,%d,%.2f" % (filename.split('/')[-1], i, solution, execution_time))
