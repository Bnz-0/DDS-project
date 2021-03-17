import sys, hjson, json, re
from math import sqrt
import os.path, multiprocessing, random
from joblib import Parallel, delayed
import numpy as np

num_cores = multiprocessing.cpu_count()

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


def calc(results, lam):
  slam = str(lam)
  if slam not in results:
    results[slam] = {}
  
  for q_num in [10]:#,100,500]:
    sq_num = str(q_num)
    if sq_num not in results[slam]:
      results[slam][sq_num] = {}

    for cho in [1,2]:#,3,5]:
      scho = str(cho)
      if scho not in results[slam][sq_num]:
        results[slam][sq_num][scho] = {}

      if os.path.exists(f'/tmp/{MAXT}.{NSAMPLINGS}.{slam}.{sq_num}.{scho}.tmp') and os.path.getsize(f'/tmp/{MAXT}.{NSAMPLINGS}.{slam}.{sq_num}.{scho}.tmp'):
        continue
      
      state, samplings = mmm.start(LAMBDA = lam, MAXT = MAXT, NSAMPLINGS = NSAMPLINGS, QUEUE_NUMBER = q_num, CHOICES = cho)

      print("state: ", state.values_sum, state.values_count)

      values_sum = state.values_sum
      values_count = state.values_count
      # for k_arr, v_arr in state.arrivals.items(): 
      #   values_sum += state.completions[k_arr] - v_arr
      #   values_count += 1
      
      del state

      # results[slam][sq_num][scho]['queue_lens'] = []
      results[slam][sq_num][scho]['queue_lens'] = np.zeros((len(samplings), q_num), dtype=int)
      # results[slam][sq_num][scho]['ts'] = []
      results[slam][sq_num][scho]['ts'] = np.zeros(len(samplings))
      # tot_len = [0 for _ in range(q_num)]
      tot_len = np.zeros(q_num, dtype=int)
      for i_sampl,x in enumerate(samplings):
        results[slam][sq_num][scho]['queue_lens'][i_sampl] = x['queue_len']
        results[slam][sq_num][scho]['ts'][i_sampl] = round(x['t'], 4)
        for i,l in enumerate(x['queue_len']):
          tot_len[i] += l

      # for x in samplings:
      #   results[slam][sq_num][scho]['queue_lens'].append(x['queue_len'])
      #   results[slam][sq_num][scho]['ts'].append(x['t'])
      #   for i,l in enumerate(x['queue_len']):
      #     tot_len[i] += l

      # meanLengths = []
      # for t in tot_len:
      #   meanLengths.append(t/len(samplings))

      meanLengths = np.zeros(len(tot_len))
      for i,t in enumerate(tot_len):
        meanLengths[i] = t/len(samplings)
      
      results[slam][sq_num][scho]["mean_len"] = meanLengths
      results[slam][sq_num][scho]["mean_time"] = values_sum / values_count
      
      results[slam][sq_num][scho]["expected_len"] = lam/(1-lam) if lam != 1 else 'inf'
      results[slam][sq_num][scho]["expected_time"] = 1/(1-lam) if lam != 1 else 'inf'

      with open(f'/tmp/{MAXT}.{NSAMPLINGS}.{slam}.{sq_num}.{scho}.tmp', 'w') as f:
        json.dump(results[slam][sq_num][scho], f, indent=2, cls=NumpyEncoder)
  
  return slam


if sys.argv[1].lower() == "mm1":
  import mm1_redacted as mm1
  mm1.main()

  import mm1_plots as plot
  plot.plotta()
  
elif sys.argv[1].lower() == "mmn":
  import mmm_np as mmm

  MAXT = 10000000
  NSAMPLINGS = 10001

  results = {}
  if os.path.isfile('results/mmm_lengths.hjson'):
    with open('results/mmm_lengths.hjson', 'r') as f:
      hjson.load(f)

  results["metadata"] = {}
  results["metadata"]["NSAMPLINGS"] = NSAMPLINGS
  results["metadata"]["MAXT"] = MAXT

  # for lam in [0.5,0.7,0.8,0.9,0.95,0.99]:
    # calc(results, lam)
  # res = Parallel(n_jobs=num_cores)(delayed(calc)(results, lam) for lam in [0.5,0.7])#,0.8,0.9,0.95,0.99])
  # print("res: ", res)

  for lam in [0.5,0.7,0.8,0.9,0.95,0.99]:
    slam = str(lam)
    if slam not in results:
      results[slam] = {}
    for q_num in [10,100,500]:
      sq_num = str(q_num)
      if sq_num not in results[slam]:
        results[slam][sq_num] = {}
      for cho in [1,2,3,5]:
        scho = str(cho)
        if scho not in results[slam][sq_num]:
          results[slam][sq_num][scho] = {}
        if os.path.exists(f'/tmp/{MAXT}.{NSAMPLINGS}.{slam}.{sq_num}.{scho}.tmp'):
          with open(f'/tmp/{MAXT}.{NSAMPLINGS}.{slam}.{sq_num}.{scho}.tmp', 'r') as f:
            results[slam][sq_num][scho] = json.load(f)

  with open('results/mmm_lengths.hjson','w') as f:
      s = re.sub(r'([,\[])\s+', r'\1 ', json.dumps(results, indent=2, cls=NumpyEncoder))
      s = re.sub(r'(\s+)],\s+', r'],\1', s)
      s = re.sub(r'],\s+\[', '], [', s)
      s = re.sub(r'\s+]],', ']],', s)
      s = re.sub(r'(\s+)},\s+', r'\1},\n\1', s)
      s = re.sub(r'(\s+)"(.*),\s"', r'\1"\2\1"', s)
      f.write(s)



  pass
elif sys.argv[1].lower() == "mmm":
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






