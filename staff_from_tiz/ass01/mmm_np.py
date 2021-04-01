#!/usr/bin/env python3

from collections import deque
from datetime import datetime
from heapq import heappush, heappop
from random import expovariate, randint, random
import time, sys, csv, os.path
import numpy as np
from NpFifo import Fifo
from dynarray import DynamicArray


MAXT = 1000000
LAMBDA = 0.7

s = set()
s_arr = set()


def processArrival(state, infos):
  # * save job arrival time in state.arrivals
  # * push the new job arrival in the event queue
  #   (the new event will happen at time t + expovariate(LAMBDA))
  # * if the server FIFO queue is empty, add this job termination
  #   (termination will happen at time t + expovariate(1))

  jobid, _ = infos
  state.arrivals[jobid] = state.t
  newjobid = jobid + 1
  tmp_t = state.getArrivalTime(newjobid)

  # I moved this check here so that when the time finish I will not add events anymore
  # but I will finish the ones in the queue, otherwise I would have Arrivals > Completions (nothing too bad btw)
  if tmp_t is not None and tmp_t < state.MAXT:
    heappush(state.events, (tmp_t, (newjobid, -1)))
  
  q = state.select_queue()
  if not len(state.fifo[q]):
    heappush(state.events, (state.getCompletionTime(jobid), (-jobid, q)))
  
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
    heappush(state.events, (state.getCompletionTime(state.fifo[queue_index][0]), (-state.fifo[queue_index][0],queue_index)))

def processSampling(state):
  newsampling = np.zeros(state.QUEUE_NUMBER, dtype=int)
  print(f"{len(state.samplings)}/{state.NSAMPLINGS}", end='           \r')
  for i, f in enumerate(state.fifo):
    newsampling[i] = len(f)
  state.samplings.append({"queue_len":newsampling, "t": state.t})

def process(state, infos):
  jobid, queue_index = infos
  if jobid == 0:
    processSampling(state)
  elif jobid < 0:
    processCompletion(state, (-jobid, queue_index))
  else:
    processArrival(state, (jobid, -1))


class State:
  def __init__(self, LAMBDA, MAXT, QUEUE_NUMBER = 10, CHOICES = 1, NSAMPLINGS = 1000, LOCALITY = False, REAL_DATAS = None):
    self.values_sum = 0
    self.values_count = 0
    self.t = 0  # current time in the simulation
    self.events = [(0, (1, -1))]  # queue of events to simulate

    self.fifo = [Fifo() for i in range(QUEUE_NUMBER)] # queue at the server
    self.CHOICES = CHOICES

    self.arrivals = {}  # jobid -> arrival time mapping
    self.completions = {}  # jobid -> completion time mapping

    self.samplings = []

    self.LAMBDA = LAMBDA * QUEUE_NUMBER
    self.MAXT = MAXT
    self.STARTT = 0
    self.QUEUE_NUMBER = QUEUE_NUMBER
    self.NSAMPLINGS = NSAMPLINGS
    self.LOCALITY = LOCALITY
    self.REAL_DATAS = []
    self.USE_REAL_DATAS = REAL_DATAS is not None
    self.LEN_REAL_DATAS = 0

    if REAL_DATAS is not None:
      csv_reader = csv.DictReader(REAL_DATAS, delimiter=',')
      for x in csv_reader:
        if x['job_status'] == 'JOBEND':
          start_time = int(datetime.timestamp(datetime.strptime(x['start_time'],'%d/%m/%Y %H:%M')))
          end_time   = int(datetime.timestamp(datetime.strptime(x['end_time'],'%d/%m/%Y %H:%M')))
          self.REAL_DATAS.append((start_time, end_time, x['job_status']))

      self.LEN_REAL_DATAS = len(self.REAL_DATAS)
      self.MAXT = self.REAL_DATAS[-1][1] - self.REAL_DATAS[0][0]
      self.STARTT = self.REAL_DATAS[0][0]

  def getArrivalTime(self,id):
    if self.USE_REAL_DATAS:
      if id < self.LEN_REAL_DATAS:
        return self.REAL_DATAS[id][0] - self.STARTT
      return None
    else:
      return self.t + expovariate(self.LAMBDA)

  def getCompletionTime(self,id):
    if self.USE_REAL_DATAS:
      if id < self.LEN_REAL_DATAS:
        # print(f"get end {id}: {self.getArrivalTime(id)} -> {self.t + (self.REAL_DATAS[id][1] - self.REAL_DATAS[id][0])} - {self.REAL_DATAS[id][2]}")
        # print(f"get end: {self.t + self.REAL_DATAS[id][1] - self.REAL_DATAS[id][0]}")
        return self.t + (self.REAL_DATAS[id][1] - self.REAL_DATAS[id][0])
      return None
    else:
      return self.t + expovariate(1)
  
  def select_queue(self):
    res = randint(0, self.QUEUE_NUMBER-1)

    if self.LOCALITY:
      tmp = res
      start = tmp - (tmp%self.CHOICES)
      end = start + self.CHOICES if start + self.CHOICES <= self.QUEUE_NUMBER else self.QUEUE_NUMBER
      # print(f"check ranges [{start }, {end-1}] for {self.CHOICES} choices")
      for i in range(start, end):
        if len(self.fifo[tmp]) > len(self.fifo[i]):
          res = i
    else:
      for i in range(self.CHOICES - 1):
        tmp = randint(0, self.QUEUE_NUMBER-1)
        if len(self.fifo[tmp]) < len(self.fifo[res]):
          res = tmp
    
    return res



def start(LAMBDA = 0.7, MAXT = 1000000, NSAMPLINGS = 1001, QUEUE_NUMBER = 100, CHOICES = 1, LOCALITY = False, REAL_DATAS = None):
  
  csv_file = None
  if REAL_DATAS is not None and os.path.exists(REAL_DATAS):
    csv_file = open(REAL_DATAS, mode='r')
  
  state = State(LAMBDA, MAXT, QUEUE_NUMBER, CHOICES, NSAMPLINGS = NSAMPLINGS, LOCALITY=LOCALITY, REAL_DATAS = csv_file)
  if csv_file is not None:
    csv_file.close()
  events = state.events

  for t in range((state.MAXT)//state.NSAMPLINGS, state.MAXT, (state.MAXT)//state.NSAMPLINGS):
    heappush(state.events, (t, (0, -1)))

  start = time.time()

  print(f"Starting:\n\tLAMBDA = {LAMBDA},\n\tMAXT = {state.MAXT},\n\tNSAMPLINGS = {NSAMPLINGS},\n\tQUEUE_NUMBER = {QUEUE_NUMBER},\n\tCHOICES = {CHOICES}\n")

  while events:
    t, event = heappop(events)
    # if t > MAXT:
    #   break
    
    state.t = t
    process(state, event)
    del event
  
  end = time.time()
  print(end - start)
  
  del state.events
  del state.REAL_DATAS
  print(f"Terminated:\n\tLAMBDA = {LAMBDA},\n\tMAXT = {state.MAXT},\n\tNSAMPLINGS = {NSAMPLINGS},\n\tQUEUE_NUMBER = {QUEUE_NUMBER},\n\tCHOICES = {CHOICES}\n")
  return state

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
