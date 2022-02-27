import random
import numpy as np
import pandas
import time


def initialise_swarm(swarm_size:int,spec:list):

    swarm = list()
    particle_position = list()
    particle_best = list()
    particle_velocity = list()
    particle_fitness = list()
    for i in range(swarm_size):
        pp = list ()
        pv = list ()
        for dimensions in range(len(spec)):
            pp.append(random.randint(spec[dimensions][0],spec[dimensions][1]))
            pv.append(0) # No Idea what to set this to, lets sart will all particles stationary
        if i==1:
           # print(pp)
           pass
        particle_position.append(pp)
        particle_best.append(pp.copy())
        particle_velocity.append(pv)
        particle_fitness.append(10000000000000000000)

    df = pandas.DataFrame({'id':range(swarm_size),'position':particle_position,'best_pos':particle_best,'velocity':particle_velocity,'fit':particle_fitness,'best_fit':particle_fitness})
    
    return df


def reset_swarm(swarm,swarm_size:int,spec:list):

    particle_position = list()
    particle_best = list()
    particle_velocity = list()
    for i in range(swarm_size):
        pp = list ()
        pv = list ()
        for dimensions in range(len(spec)):
            pp.append(random.randint(spec[dimensions][0],spec[dimensions][1]))
            pv.append(0) # No Idea what to set this to, lets sart will all particles stationary
        if i==1:
           # print(pp)
           pass
        particle_position.append(pp)
        particle_best.append(pp.copy())
        particle_velocity.append(pv)

        swarm.loc[i,'position'].clear() 
        swarm.loc[i,'position'].extend(pp)
        swarm.loc[i,'velocity'].clear()
        swarm.loc[i,'velocity'].extend(pv)

  
    return swarm



def fitness(swarm,user_fitness_function, target_solution:list=[]):

    ideal_solution=target_solution

    for i in range(len(swarm['id'])):

        position = swarm['position'][i]

        fitness,sched = user_fitness_function(position,target_solution)
          
        swarm.loc[i,'fit']=fitness
        if abs(fitness) < abs(swarm.loc[i,'best_fit']):

            swarm.loc[i,'best_fit'] = fitness
            swarm.loc[i,'best_pos'].clear()
            swarm.loc[i,'best_pos'].extend(position)
    pass

def velocity(position:list ,velocity:list ,pbest:list ,gbest:list,w:list ,c1:list ,c2:list):
    
    return  np.array(w) * np.array(velocity) + np.array(c1) * random.random()*(np.array(pbest) - np.array(position)) + np.array(c2) * random.random()*(np.array(gbest) - np.array(position))      
    #    particle inertia // move towards particle best position //  move towrds the swarms best position

def update(swarm,parameters:list,spec:list):
    w = parameters[0]
    c1 = parameters[1]
    c2 = parameters[2]
    new_position = list()
    new_velocity = list()

    #print('-------- UODATE ---------')
    #print(swarm.sort_values('fit'))
    #print(swarm.sort_values('fit').head(1))

    gbid = swarm.sort_values('best_fit').head(1).iloc[0,0] # id of the gloab best particle // best is current swarm
    global_best = swarm['best_pos'][gbid]

    wl = [[w for j in range(30)] for i in range(len(swarm['id']))]
    c1l = [[c1 for j in range(30)]for i in range(len(swarm['id']))]
    c2l = [[c2 for j in range(30)]for i in range(len(swarm['id']))]
    

    for particle in range(len(swarm['id'])):           # Loop round all particles in the swarm
        particle_best = swarm['best_pos'][particle] 
     
        new_position.clear()
        new_velocity.clear()


        for dimension in range(len(swarm['position'][0])):  # Loop round each dimension in particle
    
            new_velocity.append((  w * swarm['velocity'][particle][dimension] +                        # move in current direction
            c1 * random.random()*(particle_best[dimension]-swarm['position'][particle][dimension]) +   # move towards own best position
            c2 * random.random()*(global_best[dimension] - swarm['position'][particle][dimension])))   # move towrds the swarms best position
            np = round(swarm['position'][particle][dimension] + new_velocity[dimension])
            
            np=min(np,spec[dimension][1])  ## Clamp the position if it exceeds the solution space
            np=max(np,spec[dimension][0])
            #print('NEW POS',i,j,new_position)
            new_position.append((np))
  
        swarm.loc[particle,'position'].clear() 
        swarm.loc[particle,'position'].extend(new_position)
        swarm.loc[particle,'velocity'].clear()
        swarm.loc[particle,'velocity'].extend(new_velocity)
        
    return swarm

        

def swarm(swarm_size:int,spec:list,iterations:int,parameters:list,user_fitness_function,target_solution:list=[]):
    # Initialise the swarm
    # Loop
        # Calculate Fitness of the swarm
        # Update each particles position and velocity
        # Update swarm best position
    # Loop
    start = time.perf_counter()
  
    print('------------')
    print('Parameters')
    print('Swarm Size:',swarm_size)
    print('Iterations:',iterations)
    print("Spec.:",spec)
    print('Parameters: w =',parameters[0],' C1 =',parameters[1],' C2 =',parameters[2])
    print('------------')

    glob_fit = 100000
    swarm = initialise_swarm(swarm_size,spec)
    
    fitness(swarm,user_fitness_function,target_solution)
    last_global_best = 0
    stuck_count = 0
    reset = 0 
    gen_fit = list()
    for i in range(iterations):

        fitness(swarm,user_fitness_function,target_solution)
        
        cur_fit = min(swarm['fit'])
        if reset ==1:
            print('swarm reset')
            reset=0
        if cur_fit<glob_fit:
                glob_fit=min(swarm['fit'])
        if (abs(glob_fit)==0): 
            gen_fit.append(glob_fit)
            print()
            print('Solution Found on iteration',i,'in',round(time.perf_counter()-start,4),'sec')
           # print(swarm.sort_values('fit'))
            print('Optimal Solution:',[round (i) for i in (swarm.sort_values('fit').iloc[0,2])])
            break   
        if (abs(glob_fit)<0.00005): 
            gen_fit.append(glob_fit)
            print()
            print('THRESHOLD OUT: Solution Found on iteration',i,'in',round(time.perf_counter()-start,4),'sec')
           # print(swarm.sort_values('fit'))
            print('Non-Optimal Solution:',[round (i) for i in (swarm.sort_values('fit').iloc[0,2])])
            break   

        swarm = update(swarm,parameters,spec)
        
        global_diff = last_global_best-glob_fit
        if cur_fit==glob_fit:
            stuck_count +=1
  
        if (swarm['best_fit'].sum()/swarm_size - last_global_best)<0.00003:
         if swarm['best_fit'].sum()==swarm['fit'].sum():

            print()
            print("STUCK IN A HOLE")

    
            pp = list ()
            pv = list ()
            for dimensions in range(len(spec)):
                pp.append(random.randint(spec[dimensions][0],spec[dimensions][1]))
                pv.append(0) # No Idea what to set this to, lets sart will all particles stationary

            reset_swarm(swarm,swarm_size,spec)

            reset =1


        else:
            pass
        gen_fit.append(glob_fit)
        print('Iteration:',i,'Reset:',reset,'Error/Cost:',glob_fit,'Cur Best:',cur_fit,'Difference',round(global_diff,2),'Stuck:',swarm['best_fit'].sum()/swarm_size-glob_fit,"Reset Trigger: {:1.7f}".format(swarm['fit'].sum()/swarm['best_fit'].sum()),  parameters[0],end="\r")
        last_global_best = swarm['best_fit'].sum()/swarm_size 
    #print('Swarm:',glob_fit,swarm.sort_values('fit'),"***",swarm.sort_values('fit').head(1).iloc[0,0])
    print()
    #print('Best Solution:',[round (i) for i in (swarm.sort_values('fit').iloc[0,5])])
    print('Best Solution:',swarm.sort_values('best_fit').iloc[0,2])
    if i == iterations-1:
        print('END OF ITEREATIONS: No Solution Found on iteration',i,'in',round(time.perf_counter()-start,4),'sec')       
        print('Non-Optimal Solution:',[round (i) for i in (swarm.sort_values('fit').iloc[0,2])])

    return swarm.sort_values('best_fit').iloc[0,2], gen_fit
    return [round (i) for i in (swarm.sort_values('fit').iloc[0,5])]
    pass

