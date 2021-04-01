from matplotlib.pyplot import *
import hjson

colors = {
  "0.5": "tab:purple",
  "0.7": "tab:blue",
  "0.8": "tab:cyan",
  "0.9": "tab:green",
  "0.99": "lightblue",
  "1": "green",
  "1.001": "tab:orange",
  "1.01": "r",
}

lambdaToPlotTogether = [
  [0.99,1,1.01],
]

levelOfFiltering = 1

def clearPlot(ylims=(0,5000)):
  clf()
  ylim(ylims)
# yscale('log')

to_plot = {}

def filterComments(s):
  return s[0] != '#'

def plotta():
  results = []
  with open("results/mm1_lengths.hjson", 'r') as f:
    results = hjson.load(f)
  
  NSAMPLINGS = results["metadata"]["NSAMPLINGS"]
  NSAMPLINGS -= 1

  x = [i for i in range(NSAMPLINGS//levelOfFiltering)]

  for ltpt in lambdaToPlotTogether:
    clearPlot()
    xlim((0, NSAMPLINGS//levelOfFiltering))

    for lam in ltpt:
      label = str(lam)
      if label not in results.keys():
        break
      v = results[label]
      datas = v["queue_lens"]

      y = []
      for index, data in enumerate(datas):
        if (index%levelOfFiltering) == 0:
          y.append(data)
    
      print(len(x), len(y))
      plot(x[:len(y)] if len(x) >= len(y) else x, y if len(y) <= len(x) else y[:len(x)], colors[label], label="λ = " + label )

      to_plot[label] = datas
    else:
      xlabel('n-th of sampling')
      ylabel('Queue length')
      title('Queue length during the simulation')
      legend(loc="upper left")
      show()


  clearPlot((0,100))
  x = []
  y_len = []
  y_len_expected = []
  y_time = []
  y_time_expected = []
  for k, v in results.items():
    if str(k)=="metadata" : continue
    if float(k) >= 1: break

    x.append(k)
    y_len.append(v["mean_len"])
    y_len_expected.append(v["expected_len"])
    y_time.append(v["mean_time"])
    y_time_expected.append(v["expected_time"])
  
  plot(x,y_len, 'b-', label='Simulation results')
  plot(x,y_len_expected, 'b--', label='Expected')

  print(y_len, y_len_expected)
  print(y_time, y_time_expected, )

  legend(loc="upper left")
  xlabel('Arrival Rate')
  ylabel('Average Length')
  show()

  clearPlot((0,100))
  plot(x,y_time, 'g-', label='Simulation results')
  plot(x,y_time_expected, 'g--', label='Expected')
  legend(loc="upper left")
  xlabel('Arrival Rate')
  ylabel('Average Time')
  show()



if __name__ == '__main__':
  plotta()