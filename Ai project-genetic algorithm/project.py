import random
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

mutation_rate = 0.01
selection_rate = 0.2

Population_Size = int(input("Enter the population size: "))
Number_of_Generations = int(input("Enter the number of generations: "))
num_machines = int(input("Enter the number of machines: "))
list_of_jobs = []


def initialize_jobs_from_file(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()

    for line in lines:
        job_id = int(line.split(":")[0].split("_")[1])
        data = line.split(":")[1].strip().split("->")
        num_operations = 0
        operations = []
        for op_data in data:
            machine, processing_time = int(op_data.split("M")[1].split("[")[0]), int(
                op_data.split("[")[1].split("]")[0])
            operations.append({'machine': machine, 'processing_time': processing_time})
            num_operations += 1
        list_of_jobs.append({'job_id': job_id, 'num_operations': num_operations, 'operations': operations})
    # print(list_of_jobs)


def initialize_jobs():
    num_jobs = int(input("Enter the number of jobs: "))
    for i in range(num_jobs):
        job_id = i + 1
        num_operations = int(input(f"Enter the number of operations for Job {i + 1}: "))
        operations = []
        for j in range(num_operations):
            while True:
                machine = int(input(f"Enter machine for operation {j + 1} of Job {i + 1}: "))
                if machine > num_machines:
                    print(f"Invalid machine number. Please enter a valid machine number (1 to {num_machines}).")
                else:
                    break
            processing_time = int(input(f"Enter processing time for operation {j + 1} of Job {i + 1}: "))
            operations.append({'machine': machine, 'processing_time': processing_time})

        list_of_jobs.append({'job_id': job_id, 'num_operations': num_operations, 'operations': operations})


def initialize_chromosome():
    chromosome = []
    for job in list_of_jobs:
        job_id = job['job_id']
        for operation in range(job['num_operations']):
            chromosome.append(job_id)
    return chromosome


def initialize_population():
    initial_chromosome = initialize_chromosome()
    population = []
    for i in range(Population_Size):
        chromosome_copy = initial_chromosome[:]
        random.shuffle(chromosome_copy)
        population.append(chromosome_copy)
    return population


def fitness_func(chromosome):
    machine_avail_time = {machine: 0 for machine in range(1, num_machines + 1)}
    job_completion_time = {job['job_id']: 0 for job in list_of_jobs}
    job_operation_index = {job['job_id']: 0 for job in list_of_jobs}
    schedule = []

    for job_id in chromosome:
        job = list_of_jobs[job_id - 1]
        operations = job['operations']
        op_index = job_operation_index[job_id]

        # Ensure the operation index is within the bounds
        if op_index >= len(operations):
            continue

        operation = operations[op_index]
        machine = operation['machine']
        processing_time = operation['processing_time']
        start_time = max(machine_avail_time[machine], job_completion_time[job_id])
        completion_time = start_time + processing_time
        machine_avail_time[machine] = completion_time
        job_completion_time[job_id] = completion_time
        job_operation_index[job_id] += 1

        schedule.append((job_id, machine, start_time, completion_time))

    makespan = max(job_completion_time.values())
    return makespan, schedule


def select_parents(population):
    parents = []
    for _ in range(2):
        tournament = random.sample(population, k=3)
        parents.append(min(tournament, key=lambda x: fitness_func(x)[0]))
    return parents


def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]

    child1 = validate_and_repair(child1)
    child2 = validate_and_repair(child2)

    return child1, child2


def validate_and_repair(child):
    job_operation_counts = {job['job_id']: job['num_operations'] for job in list_of_jobs}
    child_counts = {job_id: child.count(job_id) for job_id in job_operation_counts}

    for job_id, expected_count in job_operation_counts.items():
        if child_counts[job_id] != expected_count:
            current_count = child_counts[job_id]
            if current_count < expected_count:
                missing_count = expected_count - current_count
                for _ in range(missing_count):
                    child.append(job_id)
            elif current_count > expected_count:
                excess_count = current_count - expected_count
                indices_to_remove = [i for i, x in enumerate(child) if x == job_id][:excess_count]
                for index in sorted(indices_to_remove, reverse=True):
                    child.pop(index)

    return child


def mutation(chromosome):
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(chromosome)), 2)
        chromosome[i], chromosome[j] = chromosome[j], chromosome[i]


def genetic_algorithm():
    population = initialize_population()
    best_schedule = None
    for generation in range(Number_of_Generations):
        new_population = []
        for _ in range(Population_Size // 2):
            parents = select_parents(population)
            child1, child2 = crossover(parents[0], parents[1])
            mutation(child1)
            mutation(child2)
            new_population.extend([child1, child2])

        # population = sorted(new_population, key=lambda x: fitness_func(x)[0])[:Population_Size]
        best_schedule = min(population, key=lambda x: fitness_func(x)[0])
        BF, BS = fitness_func(best_schedule)
        print(f"Generation {generation}: Best fitness = {BF} -> Schedule = {BS}")

    return best_schedule


def plot_gantt_chart(schedule):
    fig, ax = plt.subplots()
    cmap = ListedColormap(
        ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray',
         'tab:olive', 'tab:cyan'])

    for job_id, machine, start_time, end_time in schedule:
        ax.barh(machine, end_time - start_time, left=start_time, height=0.3, color=cmap(job_id % 10), edgecolor='black')
        ax.text(start_time + (end_time - start_time) / 2, machine, f'J{job_id}', color='black', ha='center',
                va='center')

    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    ax.set_title('Job Shop Schedule')
    plt.yticks(range(1, num_machines + 1), [f'M{i}' for i in range(1, num_machines + 1)])
    plt.show()


# initialize_jobs()
initialize_jobs_from_file("input_file.txt")
Population = initialize_population()

best_chromosome = genetic_algorithm()
_, best_schedule = fitness_func(best_chromosome)
print("Best Schedule:", best_schedule)

plot_gantt_chart(best_schedule)