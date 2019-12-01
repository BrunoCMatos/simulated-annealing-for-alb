from workstation import WorkStation
import math
import random
import time


class SimulatedAnnealingForALB:
    INFINITE_CYCLE_TIME = 100000
    MIN_TEMPERATURE = 0.001

    def __init__(self, assembly_line):
        self.__assembly_line = assembly_line
        self.__current_solution = self.__build_initial_solution()
        self.__cycle_time_current_solution = self.__calculate_cycle_time(self.__current_solution)
        new_solution = []
        for workstation in self.__current_solution:
            new_workstation = workstation.copy()
            new_solution.append(new_workstation)
        self.__optimal_solution = new_solution
        self.__cycle_time_optimal_solution = self.__cycle_time_current_solution
        self.moment_optimal_was_found = time.time()


    def run(self, initial_temperature, maximum_number_of_disturbances, cooling_rate):
        self.__current_solution = self.__build_initial_solution()
        temperature = initial_temperature * 1.0
        cont = 0
        while temperature >= self.MIN_TEMPERATURE:
            cont += 1
            number_of_distubances = 0
            while number_of_distubances < maximum_number_of_disturbances:
                number_of_distubances += 1
                new_solution = self.__disturb_current_solution(self.__current_solution)
                cycle_time = self.__calculate_cycle_time(new_solution)
                delta_e = cycle_time - self.__cycle_time_current_solution
                if delta_e <= 0:
                    if cycle_time < self.__cycle_time_optimal_solution:
                        self.__cycle_time_optimal_solution = cycle_time
                        self.__optimal_solution = new_solution
                        self.moment_optimal_was_found = time.time()
                    self.__current_solution = new_solution
                    self.__cycle_time_current_solution = cycle_time
                    if delta_e < 0:
                        break
                elif random.uniform(0, 1) <= self.__calculate_probability(delta_e, temperature):
                    self.__current_solution = new_solution
                    self.__cycle_time_current_solution = cycle_time
            temperature = temperature * cooling_rate

    def __disturb_current_solution(self, solution):
        new_solution = []
        for workstation in solution:
            new_workstation = workstation.copy()
            new_solution.append(new_workstation)

        workstation1 = new_solution[random.randint(0, len(new_solution) - 1)]
        workstation2 = new_solution[random.randint(0, len(new_solution) - 1)]

        task1 = workstation1.tasks[random.randint(0, len(workstation1.tasks) - 1)]
        task2 = workstation2.tasks[random.randint(0, len(workstation2.tasks) - 1)]

        # action == 0 : troca de tarefas entre estações
        # action == 1 : Ambas as tarefas vão para a workstation 1
        # action == 2 : Ambas as tarefas vão para a workstation 2
        action = random.randint(0, 2)
        if action == 0:
            workstation1.tasks.remove(task1)
            workstation1.tasks.append(task2)
            workstation2.tasks.remove(task2)
            workstation2.tasks.append(task1)
        elif action == 1 and len(workstation2.tasks) > 1:
            workstation2.tasks.remove(task2)
            workstation1.tasks.append(task2)
        elif action == 2 and len(workstation1.tasks) > 1:
            workstation1.tasks.remove(task1)
            workstation2.tasks.append(task1)

        workstation1.has_changed = True
        workstation2.has_changed = True

        return new_solution

    def __calculate_probability(self, delta_e, temperature):
        return math.exp(-delta_e/float(temperature))


    def __build_initial_solution(self):
        unallocated_tasks = self.get_tasks_ordered_by_number_of_dependencies()
        workstations = []
        approximate_number_of_tasks_per_workstation = self.__assembly_line.get_number_of_tasks() / self.__assembly_line.get_number_of_workstations()
        workstation_identification = 1
        workstation = WorkStation(workstation_identification, self.__assembly_line)
        workstation.has_changed = True
        number_of_tasks_in_this_workstation = 0

        while len(unallocated_tasks) > 0:
            if number_of_tasks_in_this_workstation >= approximate_number_of_tasks_per_workstation and \
                    len(workstations) < self.__assembly_line.get_number_of_workstations():
                workstations.append(workstation)
                number_of_tasks_in_this_workstation = 0
                workstation_identification += 1
                workstation = WorkStation(workstation_identification, self.__assembly_line)
                workstation.has_changed = True

            rand_index = -1 #random.randint(0, len(unallocated_tasks) - 1)
            rand_task = unallocated_tasks[rand_index]
            unallocated_tasks.remove(rand_task)

            workstation.tasks.append(rand_task)
            number_of_tasks_in_this_workstation += 1

        workstations.append(workstation)

        return workstations

    def get_tasks_ordered_by_number_of_dependencies(self):
        ordered_tasks = list(self.__assembly_line.get_list_of_tasks())
        for i in range(len(ordered_tasks)):
            for j in range(len(ordered_tasks)):
                number_of_dependencies_i = len(self.__assembly_line.get_dependency_graph()[ordered_tasks[i]])
                number_of_dependencies_j = len(self.__assembly_line.get_dependency_graph()[ordered_tasks[j]])
                if number_of_dependencies_i > number_of_dependencies_j:
                    aux = ordered_tasks[i]
                    ordered_tasks[i] = ordered_tasks[j]
                    ordered_tasks[j] = aux
        return ordered_tasks


    def __get_workstations_precedencies_and_dependencies(self, solution):
        workstations_a_workstation_preceeds = {}
        workstations_a_workstation_depends_on = {}
        for workstation in solution:
            workstations_a_workstation_preceeds[workstation.workstation_identification] = set()
            workstations_a_workstation_depends_on[workstation.workstation_identification] = set()
        for workstation in solution:
            tasks_the_workstation_depends_on = set()
            for task in workstation.tasks:
                task_dependencies = self.__assembly_line.get_dependency_graph()[task]
                for task_dependency in task_dependencies:
                    if task_dependency not in workstation.tasks:
                        tasks_the_workstation_depends_on.add(task_dependency)

            for other_workstation in solution:
                if workstation.workstation_identification == other_workstation.workstation_identification:
                    continue

                if len(tasks_the_workstation_depends_on.intersection(other_workstation.tasks)) > 0:
                    workstations_a_workstation_preceeds[other_workstation.workstation_identification].add(
                        workstation.workstation_identification)
                    workstations_a_workstation_depends_on[workstation.workstation_identification].add(
                        other_workstation.workstation_identification)

        return workstations_a_workstation_depends_on, workstations_a_workstation_preceeds

    def __is_solution_is_valid(self, solution):
        workstations_a_workstation_depends_on, workstations_a_workstation_preceeds = \
            self.__get_workstations_precedencies_and_dependencies(solution)

        for workstation in solution:
            if len(workstations_a_workstation_depends_on[workstation.workstation_identification]) == 0 or \
                    len(workstations_a_workstation_preceeds[workstation.workstation_identification]) == 0:
                continue
            if len(workstations_a_workstation_depends_on[workstation.workstation_identification]
                           .intersection(workstations_a_workstation_preceeds[workstation.workstation_identification])) > 0:
                return False
        return True

    def __calculate_cycle_time(self, solution):
        if not self.__is_solution_is_valid(solution):
            return self.INFINITE_CYCLE_TIME # penalizar soluções não factíveis

        max_cycle_time = 0
        for workstation in solution:
            workstation.calculate_cycle_time()
            if workstation.cycle_time > max_cycle_time:
                max_cycle_time = workstation.cycle_time

        return max_cycle_time

    def get_current_solution(self):
        return self.__current_solution

    def get_cycle_time_current_solution(self):
        return self.__cycle_time_current_solution

    def get_optimal_solution(self):
        return self.__optimal_solution

    def get_cycle_time_optimal_solution(self):
        return self.__cycle_time_optimal_solution