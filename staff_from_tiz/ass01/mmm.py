#!/usr/bin/env python3

from collections import deque
from heapq import heapify, heappush, heappop
from random import expovariate, randint

MAXT = 1000000
LAMBDA = 0.7
DEBUG = False

def loggami(*s):
	if DEBUG:
		print(s)


class Arrival:
	def __init__(self, id):
		self.id = id
	
	def __repr__(self):
		return f"Arrival - id: {self.id}"
	

	def process(self, state):
		# * save job arrival time in state.arrivals
		# * push the new job arrival in the event queue
		#   (the new event will happen at time t + expovariate(LAMBDA))
		# * if the server FIFO queue is empty, add this job termination
		#   (termination will happen at time t + expovariate(1))

		state.arrivals[self.id] = state.t
		
		tmp_t = state.t + expovariate(state.LAMBDA)

		# I moved this check here so that when the time finish I will not add events anymore
		# but I will finish the ones in the queue, otherwise I would have Arrivals > Completions (nothing too bad btw)
		if tmp_t < state.MAXT:
			heappush(state.events, (tmp_t, Arrival(self.id + 1)))
		
		tmp = state.select_queue()
		loggami("Arr q selected: ",tmp)
		
		if len(state.fifo[tmp[1]]) == 0:
			# generate Completion timing
			how_much = expovariate(1)
			tmp_t = state.t + how_much
			# sum the delta, how much time in the queue
			tmp[0] += how_much
			# push the Completion event
			heappush(state.events, (tmp_t, Completion(self.id, tmp[1], how_much)))
			# push the new timing

		loggami("-- ",state.fifo_timings)
		heappush(state.fifo_timings, tmp)
		loggami("--- ",state.fifo_timings)
		
		state.fifo[tmp[1]].append(self.id)


class Completion:
	def __init__(self, id, queue_index, how_much):
		self.id = id
		self.queue_index = queue_index
		self.how_much = how_much
	
	def __repr__(self):
		return f"Complete - id: {self.id} - queue_index: {self.queue_index} - how_much: {self.how_much}"
	
	def process(self, state):
		# * remove the first job from the FIFO queue
		# * update its completion time in state.completions
		# * insert the termination event for the next job in queue
		tmp = state.fifo[self.queue_index].popleft()
		state.completions[tmp] = state.t

		# get reference to the timing of the queue queue_index
		tmp = state.timings_indexes[self.queue_index]
		loggami(tmp)
		tmp[0] -= self.how_much

		# check if it was not the last element
		if len(state.fifo[self.queue_index]):
			how_much = expovariate(1)
			tmp[0] += how_much
			heappush(state.events, (state.t + how_much, Completion(state.fifo[self.queue_index][0],self.queue_index,how_much)))
		
		heapify(state.fifo_timings)


class State:
	def __init__(self, LAMBDA, MAXT, QUEUE_NUMBER = 5):
		self.t = 0  # current time in the simulation
		self.events = [(0, Arrival(0))]  # queue of events to simulate
		self.fifo = [deque() for i in range(QUEUE_NUMBER)]  # queue at the server
		self.fifo_timings = [ [0,i] for i in range(5) ]
		self.timings_indexes = [self.fifo_timings[i] for i in range(len(self.fifo_timings))]
		heapify(self.fifo_timings)
		self.arrivals = {}  # jobid -> arrival time mapping
		self.completions = {}  # jobid -> completion time mapping
		#self.LAMBDA = LAMBDA
		self.LAMBDA = LAMBDA * QUEUE_NUMBER
		self.MAXT = MAXT
		self.QUEUE_NUMBER = QUEUE_NUMBER
	
	def select_queue(self):
		return heappop(self.fifo_timings)


def start(LAMBDA, MAXT):
	state = State(LAMBDA, MAXT)
	events = state.events

	i = 0
	while events:
		#if i == 20: exit(0)
		i+=1
		loggami(state.fifo_timings)
		t, event = heappop(events)
		loggami(event)
		# if t > MAXT:
		#   break
		state.t = t
		event.process(state)
	
	return state

state = start(LAMBDA, MAXT)
print((state.fifo_timings))

deltas = {}
values_sum = 0
values_count = 0
for k_arr, v_arr in state.arrivals.items():
	dt = state.completions[k_arr] - v_arr
	deltas[k_arr] = dt
	values_sum += dt
	values_count += 1

mean = values_sum / values_count

print(f"Mean time is : {mean}")
print(f"Mean time expected is : {1/(1-LAMBDA)}")

# process state.arrivals and state.completions, find average time spent
# in the system, and compare it with the theoretical value of 1 / (1 - LAMBDA)

