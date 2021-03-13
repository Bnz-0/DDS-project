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
		state.completions[self.id] = state.t

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

		if last_sampling <= t and len(samplings) < NSAMPLINGS-1:
			samplings.append({"queue_len":len(state.fifo), "t": state.t})
			last_sampling += sampling_interval

		state.t = t
		event.process(state)
		del event
	
  del state.events
	return state, samplings


def main(calculateVariance = True):
	results = {}
  NSAMPLINGS = 10001
  MAXT = 10000000

  results["metadata"] = {}
  results["metadata"]["NSAMPLINGS"] = NSAMPLINGS
  results["metadata"]["MAXT"] = MAXT

  len_results = []
  lambdas = [0.5,0.7,0.8,0.9,0.95,0.99, 1, 1.01]
  for lam in lambdas:
    print(f"calculating lambda: {lam}")
    results[str(lam)] = {}

    state, samplings = mm1.start(lam, MAXT, NSAMPLINGS)
    results[str(lam)]['queue_lens'] = []
    results[str(lam)]['ts'] = []

    tot_len = 0
    for x in samplings:
      tot_len += x['queue_len']
      results[str(lam)]['queue_lens'].append(x['queue_len'])
      results[str(lam)]['ts'].append(x['t'])

    values_sum = 0
    values_count = 0
    for k_arr, v_arr in state.arrivals.items(): 
      values_sum += state.completions[k_arr] - v_arr
      values_count += 1

    results[str(lam)]['expected_len'] = lam/(1-lam) if lam != 1 else 'inf'
    results[str(lam)]['expected_time'] = 1/(1-lam) if lam != 1 else 'inf'

    if calculateVariance:
      print("calculating variance")
      meanLengths = [tot_len/len(samplings)]
      meanTimes   = [values_sum / values_count]

      nvariance = 10
      for z in range(nvariance):
        print(f"{z} execution over {nvariance}")
        state, samplings = mm1.start(lam, MAXT, NSAMPLINGS)
        tot_len = 0
        for x in samplings:
          tot_len += x['queue_len']

        values_sum = 0
        values_count = 0
        for k_arr, v_arr in state.arrivals.items():
          values_sum += state.completions[k_arr] - v_arr
          values_count += 1

        meanLengths.append(tot_len/len(samplings))
        meanTimes.append(values_sum / values_count)
      
      meanmeanLengths = sum(meanLengths)/len(meanLengths)
      meanmeanTimes = sum(meanTimes)/len(meanTimes)

      variance_len  = sqrt(sum((xi - meanmeanLengths) ** 2 for xi in meanLengths) / len(meanLengths))
      variance_time = sqrt(sum((xi - meanmeanTimes  ) ** 2 for xi in meanTimes) / len(meanTimes))

      results[str(lam)]['variance_len'] = variance_len
      results[str(lam)]['mean_len'] = meanmeanLengths

      results[str(lam)]['variance_time'] = variance_time
      results[str(lam)]['mean_time'] = meanmeanTimes

    else:
      results[str(lam)]['mean_len'] = tot_len/len(samplings)
      results[str(lam)]['mean_time'] = values_sum / values_count

    
  with open('results/mm1_lengths.hjson','w') as f:
      s = re.sub(r'([,\[])\s+', r'\1 ', json.dumps(results, indent=2))
      s = re.sub(r'(\s+)],\s+', r'],\1', s)
      s = re.sub(r'(\s+)},\s+', r'\1},\n\1', s)
      s = re.sub(r'(\s+)"(.*),\s"', r'\1"\2\1"', s)
      f.write(s)

if __name__ == '__main__':
  main()