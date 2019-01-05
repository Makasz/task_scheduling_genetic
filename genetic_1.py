from random import randint
import math

class GeneticScheduler:
    def __init__(self, n, k, h, ot, tpt, dd, bs, gv, stl):
        self.n = n  #Number of tasks (file)
        self.k = k  #Instance number
        self.h = h  #Due date
        self.original_tasks = ot
        self.tasks_processing_time = tpt
        self.due_date = dd
        self.best_scheduled = bs
        self.goal_value = gv
        self.start_time_line = stl
        self.gen_zero = []
        self.population = 100  # Must be x * 4
        self.mutation_rate = 0.2
        self.mutation_rate_percent = self.mutation_rate * 100
        self.mutation_flat = int(n * self.mutation_rate)
        self.generations = 1000

        for i, task in enumerate(bs):
            task['id'] = i

    def calculate_penalties(self, tasks, start):
        result = 0
        time = start

        for task in tasks:
            result += task['a'] * max(self.due_date - (task['p'] + time), 0) \
                      + task['b'] * max((task['p'] + time) - self.due_date, 0)
            time += task['p']

        return result

    def print_parameters(self):
        print('n:', self.n)
        print('k:', self.k)
        print('h:', self.h)
        print('original_tasks:', self.original_tasks)
        print('tasks_processing_time:', self.tasks_processing_time)
        print('due_date:', self.due_date)
        print('best_scheduled:', self.best_scheduled)
        print('goal_value:', self.goal_value)
        print('start_time_line:', self.start_time_line)

    def read_from_file(self):
        with open('results/sch{}_{}_{}.txt'.format(self.n, self.k, int(self.h * 10))) as file:
            for line in file:
                print(line.strip())

    def create_gen_zero(self):
        # self.gen_zero.append(self.best_scheduled.copy())  # Add original schedule to generation zero
        for entity in range(self.population):
            ns = self.best_scheduled.copy()  # Create new schedule
            # print(', '.join([str(task['p']) for task in ns]))
            for mutation in range(self.mutation_flat):
                tasks_to_swap = (randint(0, self.n-1), randint(0, self.n-1))  # Choose tasks to swap
                ns[tasks_to_swap[0]], ns[tasks_to_swap[1]] = ns[tasks_to_swap[1]], ns[tasks_to_swap[0]]  # Mutate schedule
            # print(', '.join([str(task['p']) for task in ns]))
            self.gen_zero.append(ns.copy())

    def crossover(self, s1, s2):
        ns = [{'id': -1} for _ in range(self.n)]
        s1_indexes = (randint(0, self.n/2-1), randint(self.n/2-1, self.n-1))
        ns[s1_indexes[0]:s1_indexes[1]] = s1[s1_indexes[0]:s1_indexes[1]]
        # print(s1_indexes, ', '.join([str(task['id']) for task in ns]))
        # Fill empty places with tasks with matching position
        s2_indexes = set(range(0, self.n, 1)) - set(range(s1_indexes[0], s1_indexes[1], 1))
        # print('I2:', s2_indexes)
        # print('NS:', ', '.join([str(task['id']) for task in ns]))
        index_to_fill = []
        used_taks = [task['id'] for task in ns]
        for index in s2_indexes:
            if s2[index]['id'] not in used_taks:
                ns[index] = s2[index]
            else:
                index_to_fill.append(index)
        missing_tasks = set(range(0, self.n, 1)) - set([task['id'] for task in ns])
        # print('NS:', ', '.join([str(task['id']) for task in ns]))
        # print('INDEX TO FILL:', index_to_fill)
        # print('MISSING TASKS:', missing_tasks)
        for index, task_id in zip(index_to_fill, missing_tasks):
            ns[index] = [t for t in s1 if t['id'] == task_id][0]
        # print('Crossover result::', ', '.join([str(task['id']) for task in ns]))
        return ns

    def create_new_gen(self, prev, group_size):
        number_of_groups = int(len(prev) / group_size)
        groups = [[] for _ in range(number_of_groups)]
        for i in range(0, len(prev), group_size):
            groups[int(i/group_size)] = prev[i:i + group_size]
        new_seed = []
        for group in groups:
            _best_task = (-1, math.inf)
            for i, task in enumerate(group):
                _penalty = self.calculate_penalties(task, self.start_time_line)
                _best_task = (i, _penalty) if _penalty < _best_task[1] else _best_task
            new_seed.append(group[_best_task[0]])
        # new_population = [self.crossover(randint(0, self.population), randint(0, self.population) for _ in range(self.population)]
        # print(len(new_population))
        new_population = []
        nsl = len(new_seed)
        _best_penalty = math.inf
        for _ in range(self.population):
            new_task = self.crossover(new_seed[randint(0, nsl-1)], new_seed[randint(0, nsl-1)])

            if randint(0, 100) < self.mutation_rate_percent:
                tasks_to_swap = (randint(0, self.n-1), randint(0, self.n-1))  # Choose tasks to swap
                new_task[tasks_to_swap[0]], new_task[tasks_to_swap[1]] = new_task[tasks_to_swap[1]], new_task[tasks_to_swap[0]]  # Mutate schedule

            new_population.append(new_task)
            _penalty = self.calculate_penalties(new_task, self.start_time_line)
            _best_penalty = _penalty if _penalty < _best_penalty else _best_penalty

        # for entity in new_population:
        #     penalty = self.calculate_penalties(entity, self.start_time_line)
        #     print(', '.join([str(task['id']) for task in entity]), penalty)
        print(_best_penalty)
        return new_population

    def get_best(self, population):
        _best_task = (-1, math.inf)
        for i, task in enumerate(population):
            _penalty = self.calculate_penalties(task, self.start_time_line)
            _best_task = (i, _penalty) if _penalty < _best_task[1] else _best_task
        return population[i]



    def run(self):
        self.create_gen_zero()
        # for entity in self.gen_zero:
        #     penalty = self.calculate_penalties(entity, self.start_time_line)
        #     print(', '.join([str(task['id']) for task in entity]), penalty)
        # self.crossover(self.gen_zero[0], self.gen_zero[1])  # Crossover 2 initial solutions
        ng = self.gen_zero
        for gen in range(self.generations):
            ng = self.create_new_gen(ng, 4)
        best_schedule = self.get_best(ng)
        return best_schedule, self.calculate_penalties(best_schedule, self.start_time_line)




