#!/usr/bin/env python3

from collections import Counter
import subprocess as sub
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
	'UPLOAD_SPEED': 500,
	'DOWNLOAD_SPEED': 2,
	'SERVER_LIFETIME': 365,
	'SERVER_UPTIME': 30,
	'SERVER_DOWNTIME': 2,
	'MAXT': 100,
	'MULTI_BLOCK_SERVER': False,
}

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
	@staticmethod
	def count_events(events):
		return Counter((e.name for e in events))

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
		for fails, blocks, title in [(d_fails, d_blocks, "Download"), (u_fails, u_blocks, "Upload")]:
			plt.title(f"No of {title} fails before a success")
			plt.xlabel("No of fails")
			plt.ylabel("Block id")
			plt.bar(range(len(fails)), fails, tick_label=blocks)
			plt.show()

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
	   		plt.title(f"Years of data safe ({n_iter} iteration) (Max: {args['MAXT']})")
	   		plt.xlabel(var)
	   		plt.ylabel("Years")
	   		plt.plot(values, avg_timing)
	   		plt.show()
		else: plotter(values, avg_timing)

	@staticmethod
	def plot_game_overs_comparison(var_list, var_range, n_iter):
		# not super usable since to be meaningful the var_range must be the same
		# and many vars have a different value meaning
		plt.title(f"Years of data safe ({n_iter} iteration) (Max: {args['MAXT']})")
		plt.ylabel("Years")
		for var in var_list:
			Plots.plot_game_overs(var, var_range, n_iter, plt.plot)
		plt.legend(var_list)
		plt.show()

EVENTS = run()
print(EVENTS[-1])

print(Plots.count_events(EVENTS))
Plots.plot_fails(EVENTS)

Plots.plot_game_overs_comparison(['NODE_LIFETIME','SERVER_LIFETIME'], range(10,41,5), 1)

# TODOs:
# - safeness? (a metric to get how your data is safe at that moment,
#              which depends on N, K, #local_blocks at time t, #remote_blocks at time t)
