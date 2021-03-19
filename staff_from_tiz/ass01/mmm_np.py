#!/usr/bin/env python3

from collections import deque
from heapq import heappush, heappop
from random import expovariate, randint, random
import time, sys
import numpy as np
from NpFifo import Fifo
from dynarray import DynamicArray


MAXT = 1000000
LAMBDA = 0.7

s = set()
s_arr = set()

# class Event:
# 	def __lt__(self, other):
# 		return random() >= 0.5

# class Arrival(Event):
# 	def __init__(self, id):
# 		self.id = id

# 	def process(self, state):
# 		# * save job arrival time in state.arrivals
# 		# * push the new job arrival in the event queue
# 		#   (the new event will happen at time t + expovariate(LAMBDA))
# 		# * if the server FIFO queue is empty, add this job termination
# 		#   (termination will happen at time t + expovariate(1))

# 		state.arrivals[self.id] = state.t
		
# 		tmp_t = state.t + expovariate(state.LAMBDA)

# 		# I moved this check here so that when the time finish I will not add events anymore
# 		# but I will finish the ones in the queue, otherwise I would have Arrivals > Completions (nothing too bad btw)
# 		if tmp_t < state.MAXT:
# 			heappush(state.events, (tmp_t, Arrival(self.id + 1)))
		
# 		q = state.select_queue()

# 		if not len(state.fifo[q]):
# 			heappush(state.events, (state.t + expovariate(1), Completion(self.id, q)))
		
# 		state.fifo[q].append(self.id)


# class Completion(Event):
# 	def __init__(self, id, queue_index):
# 		self.id = id
# 		self.queue_index = queue_index
	
# 	def process(self, state):
# 		# * remove the first job from the FIFO queue
# 		# * update its completion time in state.completions
# 		# * insert the termination event for the next job in queue
# 		tmp = state.fifo[self.queue_index].popleft()
# 		state.completions[tmp] = state.t

# 		# check if it was not the last element
# 		if len(state.fifo[self.queue_index]):
# 			heappush(state.events, (state.t + expovariate(1), Completion(state.fifo[self.queue_index][0],self.queue_index)))

def processArrival(state, infos):
	# * save job arrival time in state.arrivals
	# * push the new job arrival in the event queue
	#   (the new event will happen at time t + expovariate(LAMBDA))
	# * if the server FIFO queue is empty, add this job termination
	#   (termination will happen at time t + expovariate(1))

	jobid, _ = infos
	state.arrivals[jobid] = state.t
	tmp_t = state.t + expovariate(state.LAMBDA)

	# I moved this check here so that when the time finish I will not add events anymore
	# but I will finish the ones in the queue, otherwise I would have Arrivals > Completions (nothing too bad btw)
	if tmp_t < state.MAXT:
		heappush(state.events, (tmp_t, (jobid + 1, -1)))
	
	q = state.select_queue()
	if not len(state.fifo[q]):
		heappush(state.events, (state.t + expovariate(1), (-jobid, q)))
	
	state.fifo[q].append(jobid)

def processCompletion(state, infos):
	# * remove the first job from the FIFO queue
	# * update its completion time in state.completions
	# * insert the termination event for the next job in queue
	jobid, queue_index = infos
	tmp = state.fifo[queue_index].popleft()
	# state.completions[tmp] = state.t
	
	if state.t > 10_000:
		state.values_sum += state.t - state.arrivals[tmp]
		state.values_count += 1
		del state.arrivals[tmp]

	# check if it was not the last element
	if len(state.fifo[queue_index]):
		heappush(state.events, (state.t + expovariate(1), (-state.fifo[queue_index][0],queue_index)))

def process(state, infos):
	jobid, queue_index = infos
	if jobid < 0:
		processCompletion(state, (-jobid, queue_index))
	else:
		processArrival(state, (jobid, -1))


class State:
	def __init__(self, LAMBDA, MAXT, QUEUE_NUMBER = 10, CHOICES = 1):
		self.values_sum = 0
		self.values_count = 0
		self.t = 0  # current time in the simulation
		self.events = [(0, (1, -1))]  # queue of events to simulate

		self.fifo = [Fifo() for i in range(QUEUE_NUMBER)] # queue at the server
		self.CHOICES = CHOICES

		self.arrivals = {}  # jobid -> arrival time mapping
		self.completions = {}  # jobid -> completion time mapping

		self.LAMBDA = LAMBDA * QUEUE_NUMBER
		self.MAXT = MAXT
		self.QUEUE_NUMBER = QUEUE_NUMBER
	
	def select_queue(self):
		res = randint(0, self.QUEUE_NUMBER-1)

		for i in range(self.CHOICES - 1):
			tmp = randint(0, self.QUEUE_NUMBER-1)
			if len(self.fifo[tmp]) < len(self.fifo[res]):
				res = tmp
		
		return res



def start(LAMBDA = 0.7, MAXT = 1000000, NSAMPLINGS = 1001, QUEUE_NUMBER = 100, CHOICES = 1):
	print(f"Starting:\n\tLAMBDA = {LAMBDA},\n\tMAXT = {MAXT},\n\tNSAMPLINGS = {NSAMPLINGS},\n\tQUEUE_NUMBER = {QUEUE_NUMBER},\n\tCHOICES = {CHOICES}\n")
	state = State(LAMBDA, MAXT, QUEUE_NUMBER, CHOICES)
	events = state.events

	samplings = []

	sampling_interval = MAXT / NSAMPLINGS
	last_sampling = sampling_interval

	start = time.time()

	while events:
		t, event = heappop(events)
		# if t > MAXT:
		#   break

		if last_sampling <= t and len(samplings) < NSAMPLINGS-1:
			newsampling = np.zeros(QUEUE_NUMBER)
			print(f"{len(samplings)}/{NSAMPLINGS}", end='\r')
			for i, f in enumerate(state.fifo):
				newsampling[i] = len(f)
			samplings.append({"queue_len":newsampling, "t": state.t})
			last_sampling += sampling_interval
		
		state.t = t
		process(state, event)
		del event
	
	end = time.time()
	print(end - start)
	
	del state.events
	print(f"Terminated:\n\tLAMBDA = {LAMBDA},\n\tMAXT = {MAXT},\n\tNSAMPLINGS = {NSAMPLINGS},\n\tQUEUE_NUMBER = {QUEUE_NUMBER},\n\tCHOICES = {CHOICES}\n")
	return state, samplings

def main():
	start()

if __name__ == '__main__':
	main()

# state = start(LAMBDA, MAXT)

# deltas = {}
# values_sum = 0
# values_count = 0
# for k_arr, v_arr in state.arrivals.items():
# 	dt = state.completions[k_arr] - v_arr
# 	deltas[k_arr] = dt
# 	values_sum += dt
# 	values_count += 1

# mean = values_sum / values_count

# print(f"Mean time is : {mean}")
# print(f"Mean time expected is : {1/(1-LAMBDA)}")

# process state.arrivals and state.completions, find average time spent
# in the system, and compare it with the theoretical value of 1 / (1 - LAMBDA)
