class WorkStation:
    def __init__(self, workstation_identification, assembly_line):
        self.workstation_identification = workstation_identification
        self.tasks = []
        self.has_changed = False
        self.cycle_time = 0
        self.number_of_tasks = 0
        self.workstations_it_depends_on = set()
        self.idetification_of_workstations_it_depends_on = set()
        self.tasks_dependencies = set()
        self.__assembly_line = assembly_line

    def calculate_cycle_time(self):
        if self.has_changed:
            cycle_time = 0
            for task in self.tasks:
                cycle_time += self.__assembly_line.get_task_time(task)
            self.cycle_time = cycle_time
            self.has_changed = False

    def copy(self):
        workstation = WorkStation(self.workstation_identification, self.__assembly_line)
        workstation.tasks = list(self.tasks)
        workstation.cycle_time = self.cycle_time
        workstation.number_of_tasks = self.number_of_tasks
        workstation.workstations_it_depends_on = set(self.workstations_it_depends_on)
        workstation.idetification_of_workstations_it_depends_on = set(self.idetification_of_workstations_it_depends_on)
        workstation.tasks_dependencies = set(self.tasks_dependencies)
        workstation.has_changed = self.has_changed

        return workstation