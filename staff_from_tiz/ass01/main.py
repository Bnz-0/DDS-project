import sys

"""
TODO mm1:
- plottare lunghezza fifo con lambda < 1, = 1, > 1
- plottare lunghezza fifo con lambda = 0.5, = 0.7, =0.9 o cose così

TODO mmm:
- plottare lunghezze fifo
- plottare lunghezze fifo ...


"""

if sys.argv[1].lower() == "mm1":
  import mm1_redacted as mm1
  state, samplings = mm1.start(0.7, 1000000, 100000)
  tot_len = 0
  for x in samplings:
    tot_len += x['queue_len']
  print("number of samplings: ", len(samplings))
  print("mean: ", tot_len/len(samplings))
  pass
elif sys.argv[1].lower() == "mmn":
  pass
elif sys.argv[1].lower() == "mmm":
  import mmm_2 as mmm

  final_res = [0 for i in range(16)]
  laststate = None

  for k in range(1):
    try:
      state, samplings = mmm.start(0.5, 1000000, 10, 100, 2)
      laststate = state
    except TypeError as e:
      print("error", e)
      continue
    
    print(k, len(samplings), [samplings[h]["t"] for h in range(len(samplings))], end="\r")
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






