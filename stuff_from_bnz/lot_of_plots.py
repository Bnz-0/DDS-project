#!/usr/bin/env python3

from collections import Counter
import subprocess as sub
from math import sqrt
import matplotlib.pyplot as plt


class Event:
	def __init__(self, time, name, done):
		self.time = time
		self.name = name
		self.done = done

	def server_id(self):
		if '(' not in self.name:
			return None
		return self.name[self.name.find('(')+1 : self.name.find(',')]

	def block_id(self):
		if '(' not in self.name:
			return None
		return self.name[self.name.find(',')+1 : self.name.find(')')]

	def __str__(self):
		return f"{self.time:.2f} {self.name} {self.done}"

	@staticmethod
	def parse(line):
		t, event, *result = line.split(' ')
		return Event(float(t), event, result[0] == "[DONE]" if len(result) > 0 else None)

args = {
	'N': 10,
	'K': 8,
	'NODE_LIFETIME': 30,
	'NODE_UPTIME': 8,
	'NODE_DOWNTIME': 16,
	'DATA_SIZE': 100,
	'UPLOAD_SPEED': 0.5,
	'DOWNLOAD_SPEED': 2,
	'SERVER_LIFETIME': 365,
	'SERVER_UPTIME': 30,
	'SERVER_DOWNTIME': 2,
	'MAXT': 100,
	'MULTI_BLOCK_SERVER': False,
}

def add_plot_title(title):
	plt.suptitle(title, va='center', weight='bold')
	plt.title(f"[N={args['N']}, K={args['K']}, {'multiple blocks' if args['MULTI_BLOCK_SERVER'] else 'single block'} per server]",
		{'verticalalignment':'center'}
	)

def flat(d):
	flat_args = []
	for k,v in d.items():
		if v is not None:
			flat_args += [k, str(v)]
	return flat_args

def run():
    p = sub.run(['./backup_redacted_multi.py'] + flat(args), check=True, capture_output=True)
    return [Event.parse(l.decode('utf-8').strip()) for l in p.stdout.split(b'\n') if len(l) > 0]


class Plots:
	_filename = None
	_add_info = None

	@staticmethod
	def _plot_out():
		if Plots._add_info:
			plt.annotate(f"{Plots._add_info} = {args[Plots._add_info]}",
				(0,0), (-30,-20),
				xycoords='axes fraction', textcoords='offset points', va='top'
			)
		if Plots._filename:
			plt.savefig(f"img/{Plots._filename}.png", format="png")
			plt.close()
		else:
			plt.show()

	@staticmethod
	def set_output(filename, add_info=None):
		Plots._filename = filename
		Plots._add_info = add_info

	@staticmethod
	def count_events(events):
		return Counter((e.name for e in events))

	@staticmethod
	def game_over_avg(n_iter, mods, names):
		for i,(var,val) in enumerate(mods):
			print(f"running using {var}={val} {n_iter} times")
			original_val = args[var]
			args[var] = val
			runs = [run()[-1].time/365 for _ in range(n_iter)]
			avg = sum(runs) / n_iter
			variance = sqrt(sum((xi - avg) ** 2 for xi in runs) / len(runs))
			print(f"{names[i]}: avg={avg}, variance=±{variance} min={min(runs)}, max={max(runs)}")
			args[var] = original_val

	@staticmethod
	def plot_fails(events):
		d_fails = [0] ; u_fails = [0]
		d_blocks = [] ; u_blocks = []
		for e in (e for e in events if "Complete" in e.name):
			fails, blocks = (d_fails, d_blocks) if "Download" in e.name else (u_fails, u_blocks)
			if e.done:
				fails.append(0)
				blocks.append(e.block_id())
			else:
				fails[-1] += 1

		d_fails.pop() # the last is always 0
		u_fails.pop()
		# plotting
		original_filename = Plots._filename
		for fails, blocks, title in [(d_fails, d_blocks, "Download"), (u_fails, u_blocks, "Upload")]:
			add_plot_title(f"No of {title} fails before a success")
			plt.xlabel("Block id")
			plt.ylabel("No of fails")
			plt.bar(range(len(fails)), fails, tick_label=blocks)
			if original_filename: Plots._filename = title[0] + '_' + original_filename
			Plots._plot_out()
		Plots._filename = original_filename

	@staticmethod
	def plot_fails_multi(var, var_range, set_output=None):
		original_val = args[var]
		for v in var_range:
			print(f"Running using {var} = {v}")
			args[var] = v
			if set_output: Plots.set_output(*set_output(v))
			Plots.plot_fails(run())

		args[var] = original_val

	@staticmethod
	def plot_game_overs(var, var_range, n_iter, plotter = None):
		original_value = args[var]
		values = [] ; avg_timing = []
		for v in var_range:
			print(f"Running using {var} = {v} for {n_iter} times")
			args[var] = v
			values.append(v)
			avg_timing.append(sum(run()[-1].time for _ in range(n_iter)) / n_iter / 365)

		args[var] = original_value
		# plotting
		if plotter is None:
			add_plot_title(f"Years of data safe ({n_iter} iteration) (Max: {args['MAXT']})")
			plt.xlabel(var)
			plt.ylabel("Years")
			plt.plot(values, avg_timing)
			Plots._plot_out()
		else: plotter(values, avg_timing)

	@staticmethod
	def plot_game_overs_comparison(var_list, var_range, n_iter):
		# not super usable since to be meaningful the var_range must be the same
		# and many vars have a different value meaning
		add_plot_title(f"Years of data safe ({n_iter} iteration) (Max: {args['MAXT']})")
		plt.ylabel("Years")
		for var in var_list:
			Plots.plot_game_overs(var, var_range, n_iter, plt.plot)
		plt.legend(var_list)
		Plots._plot_out()


######## hardcoded plots ########

# single vs multi block for each server
#Plots.game_over_avg(50, [('MULTI_BLOCK_SERVER', False),('MULTI_BLOCK_SERVER', True)], ["single block", "multi block"])

#Plots.plot_fails_multi('DOWNLOAD_SPEED', [1,2,4,8], lambda v: (f"dlspeed-{v}",'DOWNLOAD_SPEED'))
#Plots.plot_fails_multi('UPLOAD_SPEED', [0.1,0.5,1,2], lambda v: (f"ulspeed-{v}",'UPLOAD_SPEED'))

Plots.set_output("game_over_k")
Plots.plot_game_overs('K', [7,8,9], 10)
exit(0)

Plots.set_output("game_over_conf_lifetime")
Plots.plot_game_overs_comparison(['NODE_LIFETIME','SERVER_LIFETIME'], range(35, 365, 30), 2)
