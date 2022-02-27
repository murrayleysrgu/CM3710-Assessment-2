from audioop import cross
import math
import random
import time
import pandas as pd

def init_Population(population_size: int,genome_length):
    # Function to generate a new solution set - AKA Initialise the population with random values
    popualtion = list()
    genome = list(range(1,genome_length+1))
    for i in range(population_size):
        random.shuffle(genome)
        genome2 = list(random.randint(1,3) for j in range(1,genome_length+1))
        popualtion.append(genome+genome2) 
    return popualtion


def chromosome_repair(chromosome,valid_chromosome):

    # Reapir the schromosome so that it still represents a valid sequence

    template = list(range(min(valid_chromosome),max(valid_chromosome)+1))

    replace=[]

    for i in range (len(template)):
        
        value = chromosome[i]
        
        if value in template:
            template.pop(template.index(value))

        else:
            replace.append(i)

    for i in range(len(replace)):
        random.shuffle(template)
        chromosome[replace.pop()]=template.pop()
    return chromosome


def crossover(chromosome1: list,chromosome2: list, type: int,repair:int):
    # Crossover function
    # Type 
    # 1 - Single Crossover at random point in the sequence
    # 2 - Double crossover at 2 random points in the sequence
    cuts = list()

    if type ==0 :## Single crossover no repiar option - full DNA
        
        # split the DNA list into individual chromosomes
        split = len(chromosome1)//2
        ch1 = chromosome1[:split]
        ch2 = chromosome1[split:]

        xover = random.randint(1,len(chromosome1)-1) # Random slice point
        pa1_first_half = chromosome1[:xover]    #was ch1
        pa1_second_half = chromosome1[xover:]   # was ch1

        pa2_first_half = chromosome2[:xover]    # was ch2
        pa2_second_half = chromosome2[xover:]   # was ch2

        kida = pa1_first_half+pa2_second_half
        kidb = pa2_first_half+pa1_second_half

        newchromo = kida #+kidb
        if repair==1:
            newchromo = chromosome_repair(newchromo,chromosome1)

        return newchromo

    elif type ==1:
        xover = random.randint(1,len(chromosome1)-1) # Random sllice point

        # slit chromosomes
        pa1_first_half = chromosome1[:xover]
        pa1_second_half = chromosome1[xover:]
        pa2_first_half = chromosome2[:xover]
        pa2_second_half = chromosome2[xover:]
                
        # Recombine swapped chromosome parts                
        newchromo = pa1_first_half+pa2_second_half
        
        if repair==1:
            newchromo = chromosome_repair(newchromo,chromosome1)

        return newchromo 

    elif type ==2:
        
        cuts.append(random.randint(1,len(chromosome1)-1))
        cuts.append(random.randint(1,len(chromosome1)-1))
        cuts.sort()

        pa1_first = chromosome1[:cuts[0]]
        pa1_second = chromosome1[cuts[0]:cuts[1]]
        pa1_third = chromosome1[cuts[1]:]
        pa2_first = chromosome2[:cuts[0]]
        pa2_second = chromosome2[cuts[0]:cuts[1]]
        pa2_third = chromosome2[cuts[1]:]

        newchromo = pa1_first+pa2_second+pa1_third
                
        if repair==1:
            newchromo = chromosome_repair(newchromo,chromosome1)
        return newchromo 
    elif type ==3:
        return chromosome1

# FITNESS TEST FOR TESTING THE PERFORANCE OF THE ALGORITM ONLY

def fitness(dna: list,ideal_solution: list): 
    # calculate the fitness of a given solution/chromosome
    #ideal_solution = [11, 9, 7, 1, 6, 8, 4, 3, 2, 10, 5, 12] # just for testing purposes
    #ideal_solution = [3, 74, 45, 65, 62, 16, 66, 51, 38, 6, 23, 47, 5, 28, 37, 36, 33, 63, 67, 13, 56, 59, 27, 24, 52, 2, 15, 21, 70, 39, 26, 46, 14, 1, 48, 31, 43, 79, 50, 58, 40, 76, 29, 32, 25, 22, 61, 7, 9, 10, 35, 55, 64, 4, 34, 71, 42, 77, 20, 30, 57, 8, 80, 11, 60, 44, 68, 54, 12, 72, 53, 73, 49, 18, 17, 78, 69, 75, 19, 41]
    
    fitness = 0
    fit_view = list()
    # Score fitness of member dna
    #for i in range(0, int(len(ideal_solution)/2)):  ### JUST CHECK 1st CHROMO --- !!!!! REOMVE 
    for i in range(0, len(ideal_solution)):
        if ideal_solution[i]==dna[i]:
            fitness = fitness + 1
            fit_add=1
        else:
            fit_add=0
        pass
        fit_view.append(fit_add)
    
    return fitness,fit_view 



def fitness2(dna: list,ideal_solution: list): 
    # calculate the fitness of a given solution/chromosome
    #ideal_solution = [11, 9, 7, 1, 6, 8, 4, 3, 2, 10, 5, 12] # just for testing purposes
    #ideal_solution = [3, 74, 45, 65, 62, 16, 66, 51, 38, 6, 23, 47, 5, 28, 37, 36, 33, 63, 67, 13, 56, 59, 27, 24, 52, 2, 15, 21, 70, 39, 26, 46, 14, 1, 48, 31, 43, 79, 50, 58, 40, 76, 29, 32, 25, 22, 61, 7, 9, 10, 35, 55, 64, 4, 34, 71, 42, 77, 20, 30, 57, 8, 80, 11, 60, 44, 68, 54, 12, 72, 53, 73, 49, 18, 17, 78, 69, 75, 19, 41]
    
    ideal_solution_dna = list()
    combined_dna = list()
    chromos = len(ideal_solution[0])-2
    ideal_solution_chromos = ideal_solution[0][1:]
    dna_chromos = dna[1:]
    
    # Combine chromosomes into one list for soltion and one list for currnet members dna
    for i in range(chromos):
        ideal_solution_dna=ideal_solution_dna+ideal_solution_chromos[i]
        combined_dna = combined_dna + dna_chromos[i]
        
    fitness = 0

    # Score fitness of member dna
    for i in range(0, len(ideal_solution_dna)):
        if ideal_solution_dna[i]==combined_dna[i]:
            fitness = fitness + 1
        pass
    return fitness #/len(ideal_solution_dna)*100  # Convert fitness score into % of max possible fitness

def population_fitness(population:list,ideal_sol:list = []):
    
    # Calulate Fitness of each member of the population
    pop_fitness = list()
    pop_sex = list()
    new_population = list()

    size = len(population)
    found = 0

    for member in range(len(population)):
        # calculate fitness of individual member of the population
        fit = fitness2(population[member],ideal_sol)
        sex = population[member][-1][0]
        pop_fitness.append(fit)
        pop_sex.append(sex)

    # Rank the population
    ranked_population = pd.DataFrame({'id':range(size),'pop':population,'fit':pop_fitness,'sex':pop_sex})  

    return ranked_population

def generations(population_size: int,genome_length:int,chromo_spec:list,  generations: int,mutations: int,crossover_type:int,pad:int,repair:int,user_fitness_function,exit_type:str='Ideal',exit_value=0.0,ideal_sol:list=[]):
  
    start = time.perf_counter()
    pop = init_Population(population_size, genome_length)
    
    max_fit = 0
    mutation_count = 0
    gen_fit = []
    
    for i in range(generations):

        # calculate fitness
        pop_fitness = list()
        pop_view = list()
        for j in range(0,len(pop)):
            
            fit,view = user_fitness_function(pop[j],ideal_sol)
            pop_fitness.append(fit)
            pop_view.append(view)
            
        # Selection
        df = pd.DataFrame({'id':range(population_size),'pop':pop,'fit':pop_fitness,'view':pop_view})

        if exit_type=='Min':
            ordered = df.sort_values('fit',ascending = True).head(int(math.ceil(population_size*0.2)))
        else:
            ordered = df.sort_values('fit',ascending = False).head(int(math.ceil(population_size*0.2)))

        toppop = ordered['id'].tolist()
        
        if exit_type=='Ideal':

            if (max(ordered['fit'])==genome_length*2-pad):    
                print()
                print('Solution Found on Loop:',i,'in ',time.perf_counter()-start,'seconds. ',mutation_count, 'Mutations')
                if max(pop_fitness)>max_fit:
                    max_fit=max(pop_fitness)
                    gen_fit.append(max_fit)
                print(ordered.head(1)['pop'])
                break
            
        elif exit_type=='Max':
            if max(ordered['fit'])==exit_value:
                max_fit=max(pop_fitness)
                gen_fit.append(max_fit)
                print()
                print('Solution Found on Loop:',i,'in ',time.perf_counter()-start,'seconds. ',mutation_count, 'Mutations')
                print(ordered.head(1)['pop'])
                break
        elif exit_type=='Min':
            if min(ordered['fit'])==exit_value:
                max_fit=min(pop_fitness)
                gen_fit.append(max_fit)
                print()
                print('Solution Found on Loop:',i,'in ',time.perf_counter()-start,'seconds. ',mutation_count, 'Mutations')
                print('')
                print(ordered.head(1)['pop'])
                break

        
        a1 = list()
        a2 = list()
        b1 = list()
        b2= list()
        pop.clear()
        for breed in range(int(population_size*0.2)):
            alpha = toppop[breed]
            a1 = df['pop'][alpha][:genome_length]
            a2 = df['pop'][alpha][genome_length:]

            for kids in range(5):
                beta = random.randint(0,population_size-1)
                b1 = df['pop'][beta][:genome_length]
                b2 = df['pop'][beta][genome_length:]
             #   crossover_type = random.randint(1,2)
                if crossover_type ==0:
                    kida = crossover(df['pop'][alpha],df['pop'][beta], crossover_type,repair)
                else:
                    kida = crossover(a1,b1,crossover_type,repair)
                    kidb = crossover(a2,b2,crossover_type,0)#repair)
                
                #if (random.randint(0,mutations)==1):
                if (random.randint(1,100)<=mutations):

                    ## Mutate the chromosome

                    for muts in range(1):
                        
                        # Randomly select mutation poins in chromosome
                        pos = random.randint(0,len(kida)-1)
                        pos2 = random.randint(0,len(kida)-1)

                        cuts = list()
                        cuts.append(random.randint(1,len(kida)-1))
                        cuts.append(random.randint(1,len(kida)-1))
                        cuts.sort()


                        # M1 - Set random gemome to random number
                        #pos = random.randint(0,genome_length)
                        #kid[pos]=random.randint(1,len(kid))

                        if crossover_type >0:
                            # Resourse mutation just select random reourse from available resourses
                            kidb[pos2] = random.randint(1,3) #genome3
                            kidb[pos] =  random.randint(1,3) #genome4

                        mut_type = random.randint(1,3)
                        ch1 = kida[:cuts[0]]
                        ch2 = kida[cuts[0]:cuts[1]]
                        ch3 = kida[cuts[1]:]
                        mut_type=1
                        if mut_type==1:
                            # M2 - Swap two chromosomes
                            

                            genome1 = kida[pos]
                            genome2 = kida[pos2]

                            kida[pos2] = genome1
                            kida[pos] = genome2

                        elif mut_type==2:

                            # M3 Mix genes

                            random.shuffle(ch2)
                            kida = ch1+ch2+ch3

                        elif mut_type==3:
                            # M4 Reverse Genes
                            ch2.reverse()
                            if cuts[0]!=cuts[1]:
                                kida = ch1+ch2+ch3

                        mutation_count = mutation_count + 1


                if crossover_type > 0:
                    kid = kida+kidb
                else:
                    kid = kida
                pop.append(kid)
        
        
        # Keep best member in the next population
        pop.pop()
        best =toppop[0]
        pop.append(df['pop'][best])   
        
        pop_fitness.sort(reverse=True)

        if exit_type=='Min':
            if min(pop_fitness)<max_fit:
                max_fit=min(pop_fitness)
            if i==0:
                max_fit = min(pop_fitness)
        else:
            if max(pop_fitness)>max_fit:
                max_fit=max(pop_fitness)


        
       
        gen_fit.append(max_fit)
        print('Generation ',i+1,'Best Fit:',max_fit,"Gen Fit: {:1.2f}".format(sum(pop_fitness)/population_size),"Mutations:",mutation_count,"F/G%:",max_fit/(i+1)*100,repair,end='\r')

    print()
    print('Solution times out on Loop:',i,time.perf_counter()-start,mutations)

    print("Generations:",i+1)
    print("Mutations:",mutation_count)
    print ('Best Fit:', max_fit)
    print('Gen Best Fit:',list(dict.fromkeys(gen_fit)))

    return df, gen_fit