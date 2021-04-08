import sys, hjson, json, re, argparse
from math import sqrt
import os.path, multiprocessing, random
from joblib import Parallel, delayed
import numpy as np

num_cores = multiprocessing.cpu_count()

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--force', default=False, dest='force', help='Force re-execution of results',action='store_true')
parser.add_argument('-r', '--real-datas', default='', type=str, dest='realdata', help='Path to real data')
parser.add_argument('-l', default=False, dest='locality', help='Useful only with -mmn',action='store_true')
parser.add_argument('-D', default=False, dest='debug', help='Debug mode',action='store_true')
parser.add_argument('mode', default=False, help='Execution mode: mm1, mmn or mmm')
args = parser.parse_args()

"""

TODO mm1:
- plottare lunghezza fifo con lambda < 1, = 1, > 1
- plottare lunghezza fifo con lambda = 0.5, = 0.7, = 0.9 o cose così

- plottare tempi fifo con lambda < 1, = 1, > 1
- plottare tempi fifo con lambda = 0.5, = 0.7, = 0.9 o cose così

TODO mmm:
- plottare lunghezze fifo
- plottare lunghezze fifo ...
- y average time  , x lambda: mmm vs mmn (es. p.8 paper)
- y average length, x lambda: mmm vs mmn (es. p.8 paper)

"""

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

calculateVariance = True

def getMMNTmpFile(MAXT, NSAMPLINGS, slam, sq_num, scho):
  opt = '.locality' if args.locality else ''
  opt+= '.real' if args.realdata else ''
  return  f'/tmp/{MAXT}.{NSAMPLINGS}.{slam}.{sq_num}.{scho}{opt}.tmp'

def getMMNOutFile():
  opt = '.locality' if args.locality else ''
  opt+= '.real' if args.realdata else ''
  return  f'results/mmm_lengths{opt}.hjson'


def calc(results, lam):
  slam = str(lam)
  if slam not in results:
    results[slam] = {}
  
  for q_num in [100]:
    sq_num = str(q_num)
    if sq_num not in results[slam]:
      results[slam][sq_num] = {}

    for cho in [1,2,5,10]:
      if q_num == 2 and cho != 2: continue
      if q_num == 3 and cho != 3: continue
      if q_num == 5 and cho != 5: continue
      
      if q_num == 1 and cho != 1:
        continue 
      scho = str(cho)
      if scho not in results[slam][sq_num]:
        results[slam][sq_num][scho] = {}

      if not args.force and os.path.exists(getMMNTmpFile(MAXT, NSAMPLINGS,slam,sq_num,scho)) and os.path.getsize(getMMNTmpFile(MAXT, NSAMPLINGS,slam,sq_num,scho)):
        continue
      
      state = mmm.start(LAMBDA = lam, MAXT = MAXT, NSAMPLINGS = NSAMPLINGS, QUEUE_NUMBER = q_num, CHOICES = cho, LOCALITY=args.locality, REAL_DATAS=args.realdata, DEBUG = args.debug)
      samplings = state.samplings

      print("state: ", state.values_sum, state.values_count)

      values_sum = state.values_sum
      values_count = state.values_count
      # for k_arr, v_arr in state.arrivals.items(): 
      #   values_sum += state.completions[k_arr] - v_arr
      #   values_count += 1
      
      del state

      results[slam][sq_num][scho]['queue_lens'] = np.zeros((len(samplings), q_num), dtype=int)
      results[slam][sq_num][scho]['ts'] = np.zeros(len(samplings))
      
      tot_len = np.zeros(q_num, dtype=int)
      for i_sampl,x in enumerate(samplings):
        results[slam][sq_num][scho]['queue_lens'][i_sampl] = x['queue_len']
        results[slam][sq_num][scho]['ts'][i_sampl] = round(x['t'], 4)
        for i,l in enumerate(x['queue_len']):
          tot_len[i] += l

      meanLengths = np.zeros(len(tot_len))
      for i,t in enumerate(tot_len):
        meanLengths[i] = t/len(samplings)
      
      results[slam][sq_num][scho]["mean_len"] = meanLengths
      results[slam][sq_num][scho]["mean_time"] = values_sum / values_count
      
      results[slam][sq_num][scho]["expected_len"] = lam/(1-lam) if lam != 1 else 'inf'
      results[slam][sq_num][scho]["expected_time"] = 1/(1-lam) if lam != 1 else 'inf'

      with open(getMMNTmpFile(MAXT, NSAMPLINGS,slam,sq_num,scho), 'w') as f:
        json.dump(results[slam][sq_num][scho], f, indent=2, cls=NumpyEncoder)
  
  return slam


if args.mode == 'mm1':
  import mm1_redacted as mm1
  mm1.main()

  import mm1_plots as plot
  plot.plotta()
  
elif args.mode == 'mmn':
  import mmm_np as mmm

  MAXT = 1000000
  NSAMPLINGS = 51 if args.realdata else 1001
  LOCALITY = False

  results = {}
  if not args.force and os.path.isfile(getMMNOutFile()):
    with open(getMMNOutFile(), 'r') as f:
      results = hjson.load(f)
      print("Successfully loaded results")

  results["metadata"] = {}
  results["metadata"]["NSAMPLINGS"] = NSAMPLINGS
  results["metadata"]["MAXT"] = MAXT

  # for lam in [0.5,0.7,0.8,0.9,0.95,0.99]:
    # calc(results, lam)
  res = Parallel(n_jobs=num_cores)(delayed(calc)(results, lam) for lam in [0.07])

  for lam in [0.07]:
    slam = str(lam)
    if slam not in results:
      results[slam] = {}
    for q_num in [1,2,3,5,10,100,500]:
      sq_num = str(q_num)
      if sq_num not in results[slam]:
        results[slam][sq_num] = {}
      for cho in [1,2,3,5,10]:
        scho = str(cho)
        if scho not in results[slam][sq_num]:
          results[slam][sq_num][scho] = {}
        elif len(results[slam][sq_num][scho].keys()) > 0: continue
        if os.path.exists(getMMNTmpFile(MAXT, NSAMPLINGS,slam,sq_num,scho)):
          with open(getMMNTmpFile(MAXT, NSAMPLINGS,slam,sq_num,scho), 'r') as f:
            results[slam][sq_num][scho] = json.load(f)

  with open(getMMNOutFile(),'w') as f:
      s = re.sub(r'([,\[])\s+', r'\1 ', json.dumps(results, indent=2, cls=NumpyEncoder))
      s = re.sub(r'(\s+)],\s+', r'],\1', s)
      s = re.sub(r'],\s+\[', '], [', s)
      s = re.sub(r'\s+]],', ']],', s)
      s = re.sub(r'(\s+)},\s+', r'\1},\n\1', s)
      s = re.sub(r'(\s+)"(.*),\s"', r'\1"\2\1"', s)
      f.write(s)

elif args.mode == 'mmm':
  import mmm_2 as mmm

  final_res = [0 for i in range(16)]
  laststate = None

  MAXT = 1000000
  NSAMPLINGS = 11
  QUEUE_NUMBER = 100
  CHOICES = 2

  results["metadata"] = {}
  results["metadata"]["NSAMPLINGS"] = NSAMPLINGS
  results["metadata"]["MAXT"] = MAXT

  
  for lam in [0.5,0.7,0.8,0.9,0.95,0.99]:
    slam = str(lam)
    results[slam] = {}
    results[slam]['queue_lens'] = []
    results[slam]['ts'] = []

    try:
      state, samplings = mmm.start(lam, MAXT, NSAMPLINGS, QUEUE_NUMBER=QUEUE_NUMBER, CHOICES=CHOICES)
      for x in samplings:
        results[slam]['queue_lens'].append(x['queue_len'])
        results[slam]['ts'].append(x['t'])
      laststate = state
    except TypeError as e:
      print("error", e)
      continue
    
    with open('results/mmm_lengths.hjson','w') as f:
      s = re.sub(r'([,\[])\s+', r'\1 ', json.dumps(results, indent=2))
      s = re.sub(r'(\s+)],\s+', r'],\1', s)
      s = re.sub(r'(\s+)},\s+', r'\1},\n\1', s)
      s = re.sub(r'(\s+)"(.*),\s"', r'\1"\2\1"', s)
      f.write(s)

    # print(k, len(samplings), [samplings[h]["t"] for h in range(len(samplings))], end="\r")
    # state, samplings = mmm.start(0.5, 100000, 100, 10, 1) -> http://www.graphreader.com/plotter?x=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15&y=1.0,0.4653,0.2376,0.1227,0.0613,0.0425,0.0168,0.0099,0.0029,0.0019,0.0,0.0,0.0,0.0,0.0,0.0

    tot_len = [0 for i in range(16)]
    for x in samplings:
      for i in x['queue_len']:
        if i > 15 : continue
        tot_len[i] += 1
    tmp = 0

    values = []
    for n,i in enumerate(tot_len[::-1]):
      tmp += i
      
      values.append(tmp)
    # print("mean: ", tot_len/len(samplings))

    values = values[::-1]
    for i in range(len(tot_len)):
      final_res[i] += values[i]

  x = [i for i in range(16)]
  y = [final_res[i]/final_res[0] for i in range(16)]

  deltas = {}
  values_sum = 0
  values_count = 0
  for k_arr, v_arr in laststate.completions.items():
    dt = v_arr - laststate.arrivals[k_arr]
    deltas[k_arr] = dt
    values_sum += dt
    values_count += 1

  mean = values_sum / values_count


  print(f"Mean time is : {mean}")

  #plt.plot(x,y,'b-')
  print(final_res)
  print(x, y)

  pass






