from operator import contains
from copy import deepcopy
from typing import final
import pandas as pd
import time
import datetime
import csv
import matplotlib.pyplot as plt

from myGeneticAlgorithmScheduleModule import generations
from mySwarmAlgorithm import swarm


def build_schedule(job_list:list,resource_allocation:list,resource_availibility):
    
    # Build schedule for each resource
    # Coding ensures that all resources are fully utilised when available 

    schedule = [[] for x in range(len(job_list))]
    end_time = list(0 for i in range(resources))           
    
    for j in range(len(job_list)):
        job_id = job_list[j]
        resource_id = resource_allocation[j]
        resource_id = max(resource_id,1)            # Clamp Resource to lower bounds 
        resource_id = min(resource_id,resources)    # Clamp Resource to upper bounds

        start_time = end_time[resource_id-1]
        ctr = job_data['CTR Hrs'][job_id-1]
        if start_time>0:
            schedule[job_id-1] = list(0 for i in range(start_time))
         
        while ctr>0:
            av = 0
            rav = resource_availibility[resource_id-1]
            day_hrs = rav.pop(0)
            if day_hrs > ctr:
                schedule[job_id-1].append(ctr)
                resource_availibility[resource_id-1].insert(0,day_hrs-ctr)
                ctr = 0
            else:
                schedule[job_id-1].append(day_hrs)
                ctr -= day_hrs
                end_time[resource_id-1] +=1
    return schedule


def fitness_check(dna:list,ideal_solution:list = []):
   
    # Split dna into individual chromosomes

    chromosome_length = int(len(dna)/2)
    job_list = dna[:chromosome_length].copy()
    resource_allocation = dna[chromosome_length:].copy()
    res_avil = deepcopy(res_av)
    sched = build_schedule(job_list,resource_allocation,res_avil)

    loss = 0
    end_dates = list(0 for i in range (chromosome_length))
    
    # PENALTY

    # HARD CONSTRAINTS 
    # 1. Job Tasks must be completed in the correct order - physically impossible to do it otherwise in real world
    # 2. Job Tasks must be completed by the correct Resource - Unskilled technician couldn't carry out the work in the real world

    # SOFT Constraints 
    # 1. Deadline - Could possibly slip in the real world
    # 2. Overtime - Could be approved to meet a deadline if approved by the client

    for jid in range(len(job_list)):
        
        days = len(sched[jid])
        deadline = job_data['Deadline'][jid]
        end_date = start_date + datetime.timedelta(days=days)
        end_dates[jid] = end_date


        # Check that the correct resource has been allocated

        resourse_list  = (job_data['Resource'][jid])        # List of allowed resources
        resource_id = str(resource_allocation[jid])         # AI assigned resource
        if resource_id not in resourse_list:
            loss += job_data['CTR Hrs'][jid]                # Penalty for assigning incorrect resource

        # Check that tasks in multi cards are complted in the correct order
        if job_data['Predesessor'][jid]!=0:
            pre = int(job_data['Predesessor'][jid])
            last_end = end_dates[pre-1]
            zpad= [z for e,z in enumerate(sched[jid]) if z == 0]
            task_start = start_date + datetime.timedelta(days=len(zpad))
            if last_end>task_start:
                loss += job_data['CTR Hrs'][jid]            # Penalty for starting task before previous task has been completed
                pass

        if (deadline-end_date).days<0:
            loss += job_data['CTR Hrs'][jid]                # Penaly for missing the final deadline
            pass

    
    return loss,sched



# --- MAIN CODE BLOCK ---

global total_hrs
global res_av
global start_date
global resources
global job_data

print('--- START ---')
print()

# Import data exported from exiting sources
# Job Card Data
print("Loading Job Card Data...")
job_data = pd.read_excel('P&M Schedule Export - 2022-01-17.xlsx')   # Read in Job data export file

#Pre Process the data
job_data['Predesessor'] = job_data['Predesessor'].fillna(0)
job_data['Resource'] = job_data['Resource'].fillna ("0,0")
job_data['Resource'] = job_data['Resource'].astype(str) + " "       # add extra char to string so that it can be searched



#Limit the data for testing AI Algoritms on easier solutions

#job_data = job_data.head(10)         ####           --- UNCOMMENT TO LIMIT THE NUMBER OF TASKS ---


print('Data Loaded at ',datetime.datetime.now())


start_date =  datetime.datetime(2022, 1, 17)
job_count = len(job_data['ID'])
resources  = 3
chromo_spec = [[1,job_count],[1,resources]]
population_size = 50
gens = 2000
mutations = 50
crossover_type = 2
repair = 1

total_hrs = job_data['CTR Hrs'].sum()
days  = total_hrs/8
weeks = total_hrs/39+1

print(job_count,'Jobs Imported')
print('Max Hrs:',total_hrs)
print('Max Days:',days)
print('Max Weeks:',weeks)

# Build Availiable hrs schedules for each resource

av_hrs= list()
av = [8,8,8,8,7,0,0]                # 8 hrs Mon - Thurs, 7 Fri, 0 Sat & Sun
for i in range(0,round(weeks)):     #
    av_hrs.extend(av)               # Max availiable Hrs on standard time

res_av = list(av_hrs.copy() for i in range(resources))

sol,progress = generations(population_size,job_count,chromo_spec,gens,mutations,crossover_type,2,repair,fitness_check,'Min',0)#total_hrs)

print()
print('progreess')
print(progress)
print()
print('--- FULL SOLUTIION ---')
print(sol.sort_values("fit",ascending=True))
print()
print('--- BEST FIT ---')
print()
print(sol.sort_values("fit",ascending=True).head(1))
print()
print(sol.sort_values("fit",ascending=True).head(1)['pop'].iloc[0][:job_count])
print()
print(sol.sort_values("fit",ascending=True).head(1)['pop'].iloc[0][job_count:])
print()
print("--- Shedule ---")
print()

final_schedule = fitness_check(sol.sort_values("fit",ascending=True).head(1)['pop'].iloc[0])
#print(final_schedule)

# Export Finial Genetic AI Schedule to a csv file 
rows = final_schedule[1]
res = sol.sort_values("fit",ascending=True).head(1)['pop'].iloc[0][job_count:]
jobs = sol.sort_values("fit",ascending=True).head(1)['pop'].iloc[0][:job_count]
for r in range(len(rows)):
    
    jid = jobs[r]
    resa = res[r]
    rows[r].insert(0,resa)  
    rows[r].insert(0,r)  
    rows[r].insert(0,job_data['Predesessor'][r])  
    rows[r].insert(0,job_data['Resource'][r])  
    rows[r].insert(0,job_data['Deadline'][r]) 
    rows[r].insert(0,job_data['CTR Hrs'][r])  
    rows[r].insert(0,job_data['Task'][r]) 
    rows[r].insert(0,job_data['Card No.'][r])  
    rows[r].insert(0,job_data['Job Number'][r])  
    rows[r].insert(0,job_data['ID'][r])  

with open('solution schedule-genetic.csv', 'w') as f:
      
    write = csv.writer(f)
    write.writerows(rows)

final_schedule = fitness_check(sol.sort_values("fit",ascending=True).head(1)['pop'].iloc[0])


print('--- PARTICLE SWARM AI ---')
job_range = [1,job_count]
resource_range = [1,resources]
solution_spec = list()
for i in range(job_count):
    solution_spec.append(job_range)
for i in range(job_count):
    solution_spec.append(resource_range)
parameters = [0.9,0.5,0.3]

sol2,progress2 = swarm(population_size,solution_spec,gens,parameters,fitness_check)
print()
print("--- RESULTS COMPARISON ---")
print(sol.sort_values("fit",ascending=False).head(1)['pop'].iloc[0][:job_count])
print(sol.sort_values("fit",ascending=False).head(1)['pop'].iloc[0][job_count:])
print()
#print(progress2)

plot_title = 'AI Progress - ' + str(len(job_data)) +' Tasks'
plt.plot(progress)
plt.plot(progress2)
plt.legend(labels=['GA','PSO'])
plt.title(plot_title)
plt.ylabel('Cost / Overtime Hours')
plt.xlabel('Generation / Iteration')
plt.show()


    
# Export final swarm schedule to csv file 
rows = final_schedule[1]
res = sol2[job_count:]
jobs = sol2[:job_count]
for r in range(len(rows)):
    
    jid = jobs[r]
    resa = res[r]
    rows[r].insert(0,resa)  
    rows[r].insert(0,r)  
    rows[r].insert(0,job_data['Predesessor'][r])  
    rows[r].insert(0,job_data['Resource'][r])  
    rows[r].insert(0,job_data['Deadline'][r]) 
    rows[r].insert(0,job_data['CTR Hrs'][r])  
    rows[r].insert(0,job_data['Task'][r]) 
    rows[r].insert(0,job_data['Card No.'][r])  
    rows[r].insert(0,job_data['Job Number'][r])  
    rows[r].insert(0,job_data['ID'][r])  

with open('solution schedule-swarm.csv', 'w') as f:
      
    
    write = csv.writer(f)
    write.writerows(rows)





