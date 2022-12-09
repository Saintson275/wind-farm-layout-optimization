import argparse
import pandas as pd
import numpy as np
import time
import copy
import os

# Set Hyperparameters
parser = argparse.ArgumentParser()
parser.add_argument('--file', default='test-10.txt', type=str)
parser.add_argument('--instance_no', default=1, type=int)
parser.add_argument('--instance_all', default=False, type=bool)
parser.add_argument('--population', default=100, type=int)
parser.add_argument('--crossover_rate', default=0.8, type=float)
parser.add_argument('--mutation_rate', default=0.2, type=float)
parser.add_argument('--mutation_selection', default=0.5, type=float)
parser.add_argument('--iteration', default=1000, type=int)
parser.add_argument('--mutation_operator', default='seq', type=str)


def read_file(file_name, instance):
    data_tmp = pd.read_csv(file_name)
    data = data_tmp.to_numpy()
    gl = 0
    num_m = 0
    num_job = 0
    global data_new
    # Read the data of the specified instance according to the input
    for i, data in enumerate(data):
        data = str(data[0]).split( )
        if data[0] == "instance" and int(data[1]) == instance:
            print("instance:", instance)
            gl = i
        if i == gl + 1:
            num_job = int(data[0])
            num_m = int(data[1])
            data_new = np.zeros(shape=(num_job, num_m))
        if i < gl + num_job + 2 and i > gl +1:
            for j in range(0, num_m):
                data_new[i-gl-2][j] = int(data[j*2+1])
    data = data_new.tolist()

    return data, num_m, num_job

def crossover(population_list, population, crossover_rate, num_job):
    parent_list = copy.deepcopy(population_list)
    offspring_list = copy.deepcopy(population_list)

    # Generate a random sequence and select the parent chromosomes to cross
    S = list(np.random.permutation(population))

    for m in range(int(population/2)):
        crossover_prob = np.random.rand()
        if crossover_rate >= crossover_prob:
            parent_1 = population_list[S[2*m]][:]
            parent_2 = population_list[S[2*m+1]][:]
            child_1 = ['na' for i in range(num_job)]
            child_2 = ['na' for i in range(num_job)]
            fix_num = round(num_job/2)
            g_fix = list(np.random.choice(num_job, fix_num, replace=False))

            # Single point crossing to fix_ Num is the Cutting Point. To avoid illegal duplication, the order of children after the Cutting Point is determined by the corresponding order of the other parent.
            for g in range(fix_num):
                child_1[g_fix[g]] = parent_2[g_fix[g]]
                child_2[g_fix[g]] = parent_1[g_fix[g]]
            c1 = [parent_1[i] for i in range(num_job) if parent_1[i] not in child_1]
            c2 = [parent_2[i] for i in range(num_job) if parent_2[i] not in child_2]            
            for i in range(num_job-fix_num):
                child_1[child_1.index('na')] = c1[i]
                child_2[child_2.index('na')] = c2[i]
            offspring_list[S[2*m]] = child_1[:]
            offspring_list[S[2*m+1]] = child_2[:]

    return offspring_list, parent_list

def mutation(offspring_list, mutation_rate, num_job, mutation_selection, mutation_operator):
    # Number of mutation jobs
    num_mutation_jobs = round(num_job*mutation_selection)
    for m in range(len(offspring_list)):
        mutation_prob = np.random.rand()
        if mutation_rate >= mutation_prob:
            # Randomly select tasks to be mutated
            m_chg = list(np.random.choice(num_job, num_mutation_jobs, replace=False)) 
            if mutation_operator == 'seq':
            # Extend these positions to be mutated by one
                t_value_last = offspring_list[m][m_chg[0]]
                for i in range(num_mutation_jobs-1):
                    offspring_list[m][m_chg[i]] = offspring_list[m][m_chg[i+1]]
                offspring_list[m][m_chg[num_mutation_jobs-1]]=t_value_last 
            elif mutation_operator == 'base':
            # Randomly modify two gene values
                i = np.random.randint(0, num_mutation_jobs/2)
                t_value = offspring_list[m][m_chg[i]]
                offspring_list[m][m_chg[i]] = offspring_list[m][m_chg[num_mutation_jobs-1-i]]
                offspring_list[m][m_chg[num_mutation_jobs-1-i]] = t_value
            elif mutation_operator == 'random':
            # Rerandom sequence
                new_offspring_list = list(np.random.permutation(num_job))
                for i in range(num_job):
                    offspring_list[m][i] = new_offspring_list[i]
             # else:
             #    raise(ValueError, "Uknown mutation operator: %s" % mutation_operator )
    return offspring_list

def cost_time(parent_list, offspring_list, data, num_m, num_job, population):
    total_chromosome = copy.deepcopy(parent_list)+copy.deepcopy(offspring_list) # combine parent and offspring chromosomes
    chrom_fit = []
    # Hold is used to indicate the end time of each generator after the current job comes in
    flow_hold = {}
    v=[0 for c in range(population*2)]
    
    for c in range(population*2):
        # Initialize flow_ hold
        for i in range(num_m):
            v[c] = v[c] + data[total_chromosome[c][0]][i]
            flow_hold[c,i] = v[c]

        # Over is used to calculate whether the time of the current task on the previous machine will exceed the time of the previous fhold after i+1 execution. If not, it is 0
        for index,j in enumerate(total_chromosome[c]):
            if index == 0:
                continue
            over = [0 for _ in range(num_m+1)]
            for i in range(num_m):
                flow_hold[c,i] = flow_hold[c,i] + data[j][i] + over[i]
                if i < num_m-1:
                    over[i+1] = max(0, flow_hold[c,i] - flow_hold[c,i+1])

        # flow_ Hold [c, num_m-1] indicates the final time consumption
        chrom_fit.append(flow_hold[c,num_m-1])
    return chrom_fit, total_chromosome

def selection(population, population_list, chrom_fit, total_chromosome):
    pk, qk = [], []   
    # Proportional selection strategy, followed by Roulette Wheel
    chrom_fitness = 1./np.array(chrom_fit)
    total_fitness = np.sum(chrom_fitness)
    for i in range(population*2):
        pk.append(chrom_fitness[i]/total_fitness)
    for i in range(population*2):
        cumulative = 0
        for j in range(0,i+1):
            cumulative = cumulative+pk[j]
        qk.append(cumulative)
    
    selection_rand = [np.random.rand() for _ in range(population)]
    
    for i in range(population):
        if selection_rand[i] <= qk[0]:
            population_list[i] = copy.deepcopy(total_chromosome[0])
            break
        else:
            for j in range(0,population*2-1):
                if selection_rand[i] > qk[j] and selection_rand[i] <= qk[j+1]:
                    population_list[i] = copy.deepcopy(total_chromosome[j+1])
    return population_list

def comparison(population, chrom_fit, total_chromosome, Tbest, Tbest_now, sequence_best):
    
    for i in range(population*2):
        if chrom_fit[i] < Tbest_now:
            Tbest_now = chrom_fit[i]
            sequence_now = copy.deepcopy(total_chromosome[i])
    
    if Tbest_now <= Tbest:
        Tbest = Tbest_now
        sequence_best = copy.deepcopy(sequence_now)
    return sequence_best, Tbest

def main(args,instance):
    if os.path.isfile(args.file):
        start_time = time.time()
        
        # Read instance data, number of machines, and number of tasks
        data, num_m, num_job = read_file(args.file, instance)
        # GA
        Tbest = 2**20
        population_list, sequence_best = [], []
        # Initialize population and random job sequence (real number coding)
        for i in range(args.population):
            nxm_random_num=list(np.random.permutation(num_job))
            population_list.append(nxm_random_num)
        # Iterative search for optimal solution
        for n in range(args.iteration):
            Tbest_now = 2**20
            offspring_list, parent_list = crossover(population_list, args.population, args.crossover_rate, num_job)
            offspring_list = mutation(offspring_list, args.mutation_rate, num_job, args.mutation_selection, args.mutation_operator)
            chrom_fit, total_chromosome = cost_time(parent_list, offspring_list, data, num_m, num_job, args.population)
            population_list = selection(args.population, population_list, chrom_fit, total_chromosome)
            # Find the best job sequence and the shortest time consumed
            sequence_best, Tbest = comparison(args.population, chrom_fit, total_chromosome, Tbest, Tbest_now, sequence_best)
            if n % 50 == 0:
                print("optimal value:%f"%Tbest)

        # show results
        print("optimal sequence",sequence_best)
        print("optimal value:%f"%Tbest)
        print('the elapsed time:%s'% (time.time() - start_time))
        file.write("optimal sequence" + str(sequence_best) + '\n')
        file.write("optimal value:" + str(Tbest) + '\n')
        file.write("the elapsed time:" + str(time.time() - start_time) + '\n')
        file.write('\n')

    else:
        raise(ValueError, "Uknown document")


if __name__ == '__main__':
    args = parser.parse_args()
    file = open("result.txt", mode='w')
    if not args.instance_all:
        file.write('\n'+'\n')
        file.write('instance:' + str(args.instance_no) + '\n')
        main(args, args.instance_no)
    else:
        for sub_ins in range(1,11):
            file.write('\n'+'\n')
            file.write('instance:' + str(sub_ins) + '\n')
            main(args, sub_ins)
