#!/usr/bin/env python3

from collections import deque
from heapq import heappush, heappop
from random import expovariate, random

MAXT = 100000000
LAMBDA = 0.99
NSAMPLINGS = 100000

class Event:
	def __lt__(self, other):
		return random() >= 0.5

class Arrival(Event):
	def __init__(self, id):
		self.id = id

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

		if not len(state.fifo):
			heappush(state.events, (state.t + expovariate(1), Completion(self.id)))
		
		state.fifo.append(self.id)


class Completion(Event):
	def __init__(self, id):
		self.id = id
	
	def process(self, state):
		# * remove the first job from the FIFO queue
		# * update its completion time in state.completions
		# * insert the termination event for the next job in queue
		tmp = state.fifo.popleft()
		state.completions[tmp] = state.t

		# check if it was not the last element
		if len(state.fifo):
			heappush(state.events, (state.t + expovariate(1), Completion(state.fifo[0])))


class State:
	def __init__(self, LAMBDA, MAXT):
		self.t = 0  # current time in the simulation
		self.events = [(0, Arrival(0))]  # queue of events to simulate
		self.fifo = deque()  # queue at the server
		self.arrivals = {}  # jobid -> arrival time mapping
		self.completions = {}  # jobid -> completion time mapping
		self.LAMBDA = LAMBDA
		self.MAXT = MAXT


def start(LAMBDA = 0.7, MAXT = 1000000, NSAMPLINGS = 2):
	state = State(LAMBDA, MAXT)
	events = state.events
	samplings = []

	sampling_interval = MAXT / NSAMPLINGS
	last_sampling = sampling_interval

	while events:
		t, event = heappop(events)
		# if t > MAXT:
		#   break

		if last_sampling <= t:
			samplings.append({"queue_len":len(state.fifo), "t": state.t})
			last_sampling += sampling_interval

		state.t = t
		event.process(state)
	
	return state, samplings

state, samplings = start(LAMBDA, MAXT)

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
