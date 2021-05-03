#!/usr/bin/env python3

from collections import deque
from datetime import datetime
from heapq import heappush, heappop
from random import expovariate, randint, random
import time, sys, csv, os.path
import numpy as np
from NpFifo import Fifo
from dateutil import parser


MAXT = 1000000
LAMBDA = 0.7

s = set()
s_arr = set()

DEBUGMODE = False

def print_debug(*s, end='\n'):
  if DEBUGMODE:
    print(*s,end=end)

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

  if tmp_t is None:
    return False

  # I moved this check here so that when the time finish I will not add events anymore
  # but I will finish the ones in the queue, otherwise I would have Arrivals > Completions (nothing too bad btw)
  if tmp_t < state.MAXT:
    heappush(state.events, (tmp_t, (newjobid, -1)))
  
  q = state.select_queue()
  if not len(state.fifo[q]):
    heappush(state.events, (state.getCompletionTime(jobid), (-jobid, q)))
  
  state.fifo[q].append(jobid)
  return True

def processCompletion(state, infos):
  # * remove the first job from the FIFO queue
  # * update its completion time in state.completions
  # * insert the termination event for the next job in queue
  jobid, queue_index = infos
  tmp = state.fifo[queue_index].popleft()
  # state.completions[tmp] = state.t
  
  if state.t > 20_000:
    state.values_sum += state.t - state.arrivals[tmp]
    state.values_count += 1
    del state.arrivals[tmp]

  # check if it was not the last element
  if len(state.fifo[queue_index]):
    heappush(state.events, (state.getCompletionTime(state.fifo[queue_index][0]), (-state.fifo[queue_index][0],queue_index)))

def processSampling(state):
  print_debug("S:",state.t)
  newsampling = np.zeros(state.QUEUE_NUMBER, dtype=int)
  print(f"{len(state.samplings)}/{state.NSAMPLINGS}", end='           \r')
  for i, f in enumerate(state.fifo):
    newsampling[i] = len(f)
  state.samplings.append({"queue_len":newsampling, "t": state.t})

def process(state, infos):
  jobid, queue_index = infos
  if jobid == 0:
    processSampling(state)
    return True
  elif jobid < 0:
    processCompletion(state, (-jobid, queue_index))
    return True
  else:
    return processArrival(state, (jobid, -1))


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
    self.REAL_DATAS_ENDS = {}
    self.USE_REAL_DATAS = REAL_DATAS is not None

    self.CSV_READER = None

    if REAL_DATAS is not None:
      self.CSV_READER = csv.DictReader(REAL_DATAS, delimiter=',')
      self.LAMBDA = 1
      self.MAXT = 1000000000
  
  def _readNextTimings(self):
    end = (None, None)
    start_time = submit_time = end_time = None
    while True:
      try:
        x = self.CSV_READER.__next__()
        if x is None: 
          print_debug("stop reading csv_file")
          return end
        if x['job_status'] != 'COMPLETED': continue
      except StopIteration:
        print_debug("stop reading csv_file")
        return end
      try:
        submit_time = int(datetime.timestamp(parser.parse(x['submit_time'])))
        start_time  = int(datetime.timestamp(parser.parse(x['start_time'])))
        end_time    = int(datetime.timestamp(parser.parse(x['end_time'])))
        break
      except:
        continue

    return submit_time, end_time

  def getArrivalTime(self,_id):
    if self.USE_REAL_DATAS:
      if _id % 50000 == 0: print_debug(_id)
      start_time, end_time = self._readNextTimings()
      if start_time is None: return None
      
      if _id == 2: 
        self.STARTT = start_time
        self.REAL_DATAS_ENDS[1] = end_time - self.STARTT

        start_time, end_time = self._readNextTimings()

      self.REAL_DATAS_ENDS[_id] = end_time - self.STARTT

      print_debug("A:",start_time -self.STARTT, "C:", end_time - self.STARTT)
      return start_time - self.STARTT
    else:
      return self.t + expovariate(self.LAMBDA)

  def getCompletionTime(self,_id):
    if self.USE_REAL_DATAS:
      res = self.REAL_DATAS_ENDS[_id]
      del self.REAL_DATAS_ENDS[_id]
      return res
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



def start(LAMBDA = 0.7, MAXT = 1000000, NSAMPLINGS = 1001, QUEUE_NUMBER = 100, CHOICES = 1, LOCALITY = False, REAL_DATAS = None, DEBUG = False):
  global DEBUGMODE
  DEBUGMODE = DEBUG
  csv_file = None
  if REAL_DATAS is not None and os.path.exists(REAL_DATAS):
    csv_file = open(REAL_DATAS, mode='r')
  
  state = State(LAMBDA, MAXT, QUEUE_NUMBER, CHOICES, NSAMPLINGS = NSAMPLINGS, LOCALITY=LOCALITY, REAL_DATAS = csv_file)
  
  events = state.events

  if REAL_DATAS is None:
    for t in range((state.MAXT)//state.NSAMPLINGS, state.MAXT, (state.MAXT)//state.NSAMPLINGS):
      heappush(state.events, (t, (0, -1)))
  else:
    for t in range(0, 1000000000, 100000):
      heappush(state.events, (t, (0, -1)))

  start = time.time()

  print(f"Starting:\n\tLAMBDA = {LAMBDA},\n\tMAXT = {state.MAXT},\n\tNSAMPLINGS = {NSAMPLINGS},\n\tQUEUE_NUMBER = {QUEUE_NUMBER},\n\tCHOICES = {CHOICES}\n")

  c = True
  while events and c:
    t, event = heappop(events)
    # if t > MAXT:
    #   break
    
    state.t = t
    c = process(state, event)
    del event
  
  if csv_file is not None:
    csv_file.close()

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
