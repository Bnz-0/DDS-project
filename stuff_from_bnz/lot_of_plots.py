#!/usr/bin/env python3

from collections import Counter
import subprocess as sub
import matplotlib.pyplot as plt

class Event:
	def __init__(self, f, name, done):
		self.f = f
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
		return f"{self.f:.2f} {self.name} {self.done}"

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
	'''
	=== multi-run plots
	- iterating over an input, plot after how many years you got a GameOver

	'''

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
			plt.bar(range(len(fails)), fails, tick_label=blocks)
			plt.title(title+" fails") # TODO: better title
			plt.show()

	@staticmethod
	def plot_(var, var_range, n_iter=1):
		# var: name of the input variable to change
		# var_range: tuple (init, end, step)
		# n_iter: #time run() wit the same input
		assert False, "TODO"

EVENTS = run()

print(EVENTS[-1])

print(Plots.count_events(EVENTS))
Plots.plot_fails(EVENTS)
