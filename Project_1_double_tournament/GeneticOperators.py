from .Individual import Individual
from .Node import Node
import sys

# 
# By using this file, you are agreeing to this product's EULA
#
# This product can be obtained in https://github.com/jespb/Python-StdGP
#
# Copyright ©2019-2022 J. E. Batista
#


def tournament(rng, population,n):
	'''
	Selects "n" Individuals from the population and return a 
	single Individual.

	Parameters:
	population (list): A list of Individuals, sorted from best to worse.
	'''
	print(len(str(population[2])))
	candidates = [rng.randint(0,len(population)-1) for i in range(n)]
	return population[min(candidates)]


def double_tournament(rng, population, sf, sp, n, switch=False): 
	'''
	Double tournament selection process. Will perform two tournaments based on
	fitness and size and return a single Individual. The switch parameter defines 
	which type of tournament will be performed first.

	Parameters: 
	- rng (a random number generator)
	- population (a list of individuals) sorted from best to worse
	- sf and sp (tournament sizes for fitness and size)
	- n (the number of random individuals in the first tournament) 
	- Switch, determines the order of the tournaments. False by default
	'''


	##################################################################
	######################### Fitness first ##########################

	if switch == False and sp <= sf: 									#Check for switch and tournament sizes (Sf & Sp)
		
		#First Tournament: Fitness --------------------------------------------------------------------------------------------
		winners_one = []												#Create an empty list for the indexes with the best fit
		for i in range(sf):												#Perform Sf tournaments
			can_1 = [rng.randint(0,len(population)-1) for i in range(n)]#Choose n random individuals
			winners_one.append(min(can_1))								#Save the individual with the lowest index (highest fit) in the list

		#Second Tournament: Size -----------------------------------------------------------------------------------------------
		candidates_2 = rng.sample(winners_one, sp) 						#Get a random sample in the size of Sp
		size = [] 														#Empty list for the size of the individuals
		for candidate in candidates_2: 									#Iterate through the selected winners of the first tournament
			size.append(Individual.getSize(population[candidate]))		#Use getSize() to get the size of the individuals
		min_value = min(size) 											#Get the smallest size 
		min_index = [i for i, x in enumerate(size) if x == min_value] 	#Get the index for the individual with the smallest size
		rng_index = rng.randint(0, len(min_index)-1)					#Choose a random index of the smallest individuals (if there is the same size twice)
		#print("Fitness:",winners_one[min_index[rng_index]], "Size:",min_value)
		return population[winners_one[min_index[rng_index]]] 			#Return the winnning individual

	

	#############################################################	
	#########################Size first##########################
	
	elif switch == True and sp >= sf: 									#Check for switch and tournament sizes (Sf & Sp)

		#First Tournament: Size -----------------------------------------------------------------------------------------------
		winners_1 =[]													#Empty list for the winners 
		for i in range(sp):												#Perform sp tournaments
			can = [rng.randint(0,len(population)-1) for i in range(n)]	#Get n random individuals
			size = []													#Empty list for the size
			for candidate in can:										#Iterate through the candidates for the tournament
				size.append(Individual.getSize(population[candidate]))	#Get the sizes of the candidates								
			min_value = min(size)										#Get the minimum size
			min_index =[i for i, x in enumerate(size) if x == min_value]#Get the index for the minimum size
			winners_1.append(can[min_index[0]])							#Save the indexes of the winner
		#Second Tournament: Fitness -----------------------------------------------------------------------------------------------
		candidates_2 = rng.sample(winners_1, sf)						#Get sf samples of the first winners
		#print("Fitness:", min(candidates_2), "Size:", Individual.getSize(population[min(candidates_2)]))
		return population[min(candidates_2)]							#Return the individual with the lowest index (highest fitness)
	

	################################################################
	#If the conditions and the switch do not fit -> kill the process
	################################################################

	elif switch == True and sp < sf: 									
		sys.exit("Conditions: Switch == True and sp < sf. The switch needs to be turned to False in order to proceed")
	elif switch == False and sp > sf: 
		sys.exit("Conditions: switch == False and sp > sf. The switch needs to be turned to True in order to proceed")

def getElite(population,n):
	'''
	Returns the "n" best Individuals in the population.

	Parameters:
	population (list): A list of Individuals, sorted from best to worse.
	'''
	return population[:n]


def getOffspring(rng, population, sf, sp,n, switch):
	'''
	Genetic Operator: Selects a genetic operator and returns a list with the 
	offspring Individuals. The crossover GOs return two Individuals and the
	mutation GO returns one individual. Individuals over the LIMIT_DEPTH are 
	then excluded, making it possible for this method to return an empty list.

	Parameters:
	population (list): A list of Individuals, sorted from best to worse.
	'''
	isCross = rng.random()<0.5

	desc = None

	if isCross:
		desc = STXO(rng, population, sf, sp, n, switch)
	else:
		desc = STMUT(rng, population, sf, sp, n, switch)

	return desc


def discardDeep(population, limit):
	ret = []
	for ind in population:
		if ind.getDepth() <= limit:
			ret.append(ind)
	return ret


def STXO(rng, population, sf, sp, n, switch):
	'''
	Randomly selects one node from each of two individuals; swaps the node and
	sub-nodes; and returns the two new Individuals as the offspring.

	Parameters:
	population (list): A list of Individuals, sorted from best to worse.
	'''
	ind1 = double_tournament(rng, population, sf, sp, n, switch)
	ind2 = double_tournament(rng, population, sf, sp, n, switch)

	h1 = ind1.getHead()
	h2 = ind2.getHead()

	n1 = h1.getRandomNode(rng)
	n2 = h2.getRandomNode(rng)

	n1.swap(n2)

	ret = []
	for h in [h1,h2]:
		i = Individual(ind1.operators, ind1.terminals, ind1.max_depth, ind1.model_name, ind1.fitnessType)
		i.copy(h)
		ret.append(i)
	return ret


def STMUT(rng, population, sf, sp, n, switch):
	'''
	Randomly selects one node from a single individual; swaps the node with a 
	new, node generated using Grow; and returns the new Individual as the offspring.

	Parameters:
	population (list): A list of Individuals, sorted from best to worse.
	'''
	ind1 = double_tournament(rng, population, sf, sp, n, switch)
	h1 = ind1.getHead()
	n1 = h1.getRandomNode(rng)
	n = Node()
	n.create(rng, ind1.operators, ind1.terminals, ind1.max_depth)
	n1.swap(n)


	ret = []
	i = Individual(ind1.operators, ind1.terminals, ind1.max_depth, ind1.model_name, ind1.fitnessType)
	i.copy(h1)
	ret.append(i)
	return ret
