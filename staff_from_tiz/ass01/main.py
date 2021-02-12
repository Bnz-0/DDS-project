import sys

if sys.argv[1].lower() == "mm1":
  import mm1_redacted as mm1
  state, samplings = mm1.start(0.7, 1000000, 100000)
  tot_len = 0
  for x in samplings:
    tot_len += x['queue_len']
  print("mean: ", tot_len/len(samplings))
  pass
elif sys.argv[1].lower() == "mmn":
  pass
elif sys.argv[1].lower() == "mmm":
  pass






