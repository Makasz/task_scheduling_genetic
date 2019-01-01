from random import randint

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
        self.population = 2
        self.mutation_rate = 0.2
        self.mutation_flat = int(n * self.mutation_rate)

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

        ns = [{'id': -1} for _ in range(20)]
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
        print('Crossover result::', ', '.join([str(task['id']) for task in ns]))

        return ns



    def run(self):
        self.create_gen_zero()
        for entity in self.gen_zero:
            penalty = self.calculate_penalties(entity, self.start_time_line)
            print(', '.join([str(task['id']) for task in entity]), penalty)
        self.crossover(self.gen_zero[0], self.gen_zero[1])




