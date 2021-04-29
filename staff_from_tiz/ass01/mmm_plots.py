from matplotlib.pyplot import *
import hjson, argparse

colors = {
  "10": "tab:blue",
  "5": "tab:purple",
  "3": "tab:cyan",
  "2": "tab:green",
  "1": "r",
}

colors_lam = {
  "0.07": "b",
  "1.00011": "b",
  "0.5": "b",
  "0.7": "tab:cyan",
  "0.8": "tab:orange",
  "0.9": "y",
  "0.95": "g",
  "0.99": "r",
}
default_color = "b"

def elaborate_results(results):
  x = []
  dict_nchoice_mean_time = {}
  dict_nchoice_mean_len = {}
  dict_nchoice_lengths = {}

  for lam, res in results.items():
    if lam == "metadata":  continue
    x.append(float(lam))
    print(lam)
    for q_len, qlen_res in res.items():
      if q_len != "100": continue
      print(q_len)
      for cho, cho_res in qlen_res.items():
        if q_len == "2" and cho != "2": continue
        if q_len == "3" and cho != "3": continue
        if q_len == "5" and cho != "5": continue
        #if cho == "3": continue
        
        print(cho_res["mean_time"])
        mean_len = sum(cho_res["mean_len"])/len(cho_res["mean_len"])
        if cho not in dict_nchoice_mean_time:
          dict_nchoice_mean_time[cho] = []
          dict_nchoice_mean_len[cho] = []
        if cho not in dict_nchoice_lengths:
          dict_nchoice_lengths[cho] = {}
          dict_nchoice_lengths[cho][lam] = []
        dict_nchoice_mean_time[cho].append(cho_res["mean_time"])
        dict_nchoice_mean_len[cho].append(mean_len)

        final_res = [0 for i in range(16)]
        tot_len   = [0 for i in range(16)]
        for xc in cho_res['queue_lens']:
          for i in xc:
            if i > 15 :
              tot_len[15] += 1
              continue
            tot_len[i] += 1
        tmp = 0

        values = []
        for n,i in enumerate(tot_len[::-1]):
          tmp += i
          values.append(tmp)

        values = values[::-1]
        for i in range(len(tot_len)):
          final_res[i] += values[i]
        
        print(final_res)

        x_l = [i for i in range(16)]
        y_l = [final_res[i]/final_res[0] for i in range(16)]

        dict_nchoice_lengths[cho][lam] = [x_l,y_l]

  return x, dict_nchoice_mean_time, dict_nchoice_mean_len, dict_nchoice_lengths



def dodistrplot(x, dict_nchoice_mean_time, dict_nchoice_mean_len, dict_nchoice_lengths, fig, axs):
  for (cho, lams),(xplot,yplot) in zip(dict_nchoice_lengths.items(), [(0,0),(0,1),(1,0),(1,1)]):
    print(f'Putting {cho} in position ({xplot},{yplot})')
    axs[xplot, yplot].set_title(f"{cho} choices")

    for ax in axs.flat:
      ax.set(ylabel='Fraction of queues with at least that size', xlabel='Queue Length')

    for lam, xy in lams.items():
      LAMBDA = float(lam)
      if lam == "0.7" or lam == "0.8": continue
      axs[xplot, yplot].plot(xy[0][1:15],xy[1][1:15], default_color, label=f'λ = {lam}')
      if cho == "1":
        axs[xplot, yplot].plot(xy[0][1:15],[LAMBDA**i for i in xy[0][1:15]], f'{default_color}--', label=f'expected')
      else:
        choices = int(cho)
        axs[xplot, yplot].plot(xy[0][1:15],[LAMBDA**(((choices**i)-1)/(choices-1)) for i in xy[0][1:15]], f'{default_color}--', label=f'expected')

    axs[xplot, yplot].legend(loc="upper right")

def dodistrplot_realdatas(x, dict_nchoice_mean_time, dict_nchoice_mean_len, dict_nchoice_lengths, fig, axs):
  cho_one = dict_nchoice_lengths["1"]["1.0"]
  del dict_nchoice_lengths["1"]
  for (cho, lams),(xplot,yplot) in zip(dict_nchoice_lengths.items(), [(0,0),(0,1),(1,0),(1,1)]):
    print(cho, lams)
    print(f'Putting {cho} in position ({xplot},{yplot})')
    axs[xplot, yplot].set_title(f"{cho} choices")

    for ax in axs.flat:
      ax.set(ylabel='Fraction of queues with at least that size', xlabel='Queue Length')

    for lam, xy in lams.items():
      LAMBDA = float(lam)
      if lam == "0.7" or lam == "0.8": continue
      axs[xplot, yplot].plot(xy[0][1:15],xy[1][1:15], default_color, label=f'market model choice')
      axs[xplot, yplot].plot(cho_one[0][1:15],cho_one[1][1:15], 'r', label=f'random choice')
      # if cho == "1":
      #   axs[xplot, yplot].plot(xy[0][1:15],[LAMBDA**i for i in xy[0][1:15]], f'{col}--', label=f'expected')
      # else:
      #   choices = int(cho)
      #   axs[xplot, yplot].plot(xy[0][1:15],[LAMBDA**(((choices**i)-1)/(choices-1)) for i in xy[0][1:15]], f'{col}--', label=f'expected')

    axs[xplot, yplot].legend(loc="upper right")

def plotta(only_real = False):
  results = {}
  
  if not only_real:
    with open("results/mmm_lengths.hjson", 'r') as f:
      results = hjson.load(f)
    x, dict_nchoice_mean_time, dict_nchoice_mean_len, dict_nchoice_lengths = elaborate_results(results)
  else:
    real_results = {}
    with open("results/mmm_lengths.real.hjson", 'r') as f:
      real_results = hjson.load(f)
    x, dict_nchoice_mean_time, dict_nchoice_mean_len, dict_nchoice_lengths = elaborate_results(real_results)

  if not only_real:
    for cho, y in dict_nchoice_mean_time.items():
      print(cho, x, y)
      plot(x,y, colors[cho], label=f'{cho} choice')

    legend(loc="upper left")
    xlabel('Arrival Rate')
    ylabel('Average Time')
    show()
    clf()

  if not only_real:
    for cho, y in dict_nchoice_mean_len.items():
      print(cho, x, y)
      plot(x,y, colors[cho], label=f'{cho} choice')

    legend(loc="upper left")
    xlabel('Arrival Rate')
    ylabel('Average Queue Length')
    show()
    clf()
  

  fig, axs = subplots(2, 2)
  if only_real:
    dodistrplot_realdatas(x, dict_nchoice_mean_time, dict_nchoice_mean_len, dict_nchoice_lengths, fig, axs)
  else:
    dodistrplot(real_x, real_dict_nchoice_mean_time, real_dict_nchoice_mean_len, real_dict_nchoice_lengths, fig, axs)
    
  for ax in axs.flat:
    ax.label_outer()
  
  show()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--real-datas', default=False, action='store_true', dest='realdata', help='Use real datas results')
  args = parser.parse_args()

  plotta(only_real=args.realdata)