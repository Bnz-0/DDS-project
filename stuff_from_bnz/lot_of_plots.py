#!/usr/bin/env python3

import subprocess as sub
from copy import copy
from collections import Counter
from multiprocessing import Pool
from math import sqrt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Pointer:
	def __init__(self, val):
		self.val = val

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

	def is_download(self):
		return "DownloadComplete" in self.name

	def is_upload(self):
		return "UploadComplete" in self.name

	def is_game_over(self):
		return "GameOver" in self.name or "DataSafe" in self.name

	def __str__(self):
		return f"{self.time:.2f} {self.name} {self.done}"

	@staticmethod
	def parse(line):
		t, event, *result = line.split(' ')
		return Event(float(t), event, result[0] == "[DONE]" if len(result) > 0 else None)

ARGS = {
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

def add_plot_title(title, args):
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

def run(args = ARGS):
    p = sub.run(['./backup_redacted_multi.py'] + flat(args), check=True, capture_output=True)
    return [Event.parse(l.decode('utf-8').strip()) for l in p.stdout.split(b'\n') if len(l) > 0]

def run_parallel(argsv):
       pool = Pool(processes=len(argsv))
       ps = [pool.apply_async(run, [args]) for args in argsv]
       pool.close()
       pool.join()
       return [p.get() for p in ps]

class Plots:
	_filename = None
	_add_info = None

	@staticmethod
	def _plot_out(args):
		if Plots._add_info:
			plt.annotate(f"{Plots._add_info} = {args[Plots._add_info]}",
				(0,0), (-30,-20),
				xycoords='axes fraction', textcoords='offset points', va='top'
			)
		if Plots._filename:
			plt.savefig(f"img/{Plots._filename}.png", format="png")
		else:
			plt.savefig("img/plot.png", format="png")
		plt.close()

	@staticmethod
	def set_output(filename, add_info=None):
		Plots._filename = filename
		Plots._add_info = add_info

	@staticmethod
	def count_events(events):
		return Counter((e.name for e in events))

	@staticmethod
	def game_over_avg(n_iter):
		print(f"running {n_iter} times")
		runs = [r[-1].time/365 for r in run_parallel([ARGS]*n_iter)]
		avg = sum(runs) / n_iter
		variance = sqrt(sum((xi - avg) ** 2 for xi in runs) / len(runs))
		print(f"avg={avg}, variance=±{variance} min={min(runs)}, max={max(runs)}")

	@staticmethod
	def game_over_dist(n_iter, args, t_range):
		runs = [r[-1].time/365 for r in run_parallel([args]*n_iter)]
		x = [0] * (int(args['MAXT']//t_range))
		for t in runs:
			i = int(t//t_range)
			x[i-1 if i==len(x) else i] += 1

		# plotting
		add_plot_title(f"Game over distribution ({n_iter} iteration)", args)
		plt.xlabel("years")
		plt.ylabel("#game-over")
		plt.bar(range(len(x)), x, tick_label=[f"{t*t_range}-{t*t_range + t_range}" for t in range(len(x))])
		Plots._plot_out(args)


	@staticmethod
	def plot_fails(events, args):
		d_fails = [0] ; u_fails = [0]
		d_blocks = [] ; u_blocks = []
		curr_d = Pointer(None) ; curr_u = Pointer(None)
		for e in (e for e in events if e.is_upload() or e.is_download() or e.is_game_over()):
			if e.is_game_over():
				d_blocks.append(curr_d.val)
				u_blocks.append(curr_u.val)
				break
			fails, blocks, curr = (d_fails, d_blocks, curr_d) if e.is_download() else (u_fails, u_blocks, curr_u)
			curr.val = e.block_id()
			if e.done:
				blocks.append(curr.val)
				fails.append(0)
			else:
				fails[-1] += 1

		# plotting
		original_filename = Plots._filename
		for fails, blocks, title in [(d_fails, d_blocks, "Download"), (u_fails, u_blocks, "Upload")]:
			add_plot_title(f"No. of {title} fails before a success", args)
			plt.xlabel("Block id")
			plt.ylabel("No. of fails")
			plt.bar(range(len(fails)), fails, tick_label=blocks)
			if original_filename: Plots._filename = title[0] + '_' + original_filename
			Plots._plot_out(args)
		Plots._filename = original_filename

	@staticmethod
	def plot_fails_multi(var, var_range, set_output=None):
		argsv = []
		for v in var_range:
			argsv.append(copy(ARGS))
			argsv[-1][var] = v
		for i,r in enumerate(run_parallel(argsv)):
			if set_output: Plots.set_output(*set_output(var_range[i]))
			Plots.plot_fails(r, argsv[i])

	@staticmethod
	def plot_game_overs(var, var_range, n_iter, plotter = None, args_mod = None):
		original_val = ARGS[var]
		values = var_range[:]
		avg_timing = []
		for v in var_range:
			ARGS[var] = v
			if args_mod: args_mod(ARGS)
			avg_timing.append(sum(r[-1].time for r in run_parallel([ARGS]*n_iter)) / n_iter / 365)
		# plotting
		if plotter is None:
			add_plot_title(f"Years of data safe ({n_iter} iteration) (Max: {ARGS['MAXT']})", ARGS)
			plt.xlabel(var)
			plt.ylabel("Years")
			plt.plot(values, avg_timing)
			Plots._plot_out(ARGS)
		else:
			plotter(values, avg_timing)
		ARGS[var] = original_val

	@staticmethod
	def plot_game_overs_comparison(var_list, var_range, n_iter):
		# not super usable since to be meaningful the var_range must be the same
		# and many vars have a different value meaning
		add_plot_title(f"Years of data safe ({n_iter} iteration) (Max: {ARGS['MAXT']})", ARGS)
		plt.ylabel("Years")
		for var in var_list:
			Plots.plot_game_overs(var, var_range, n_iter, plt.plot)
		plt.legend(var_list)
		Plots._plot_out(ARGS)


######## hardcoded plots ########
def set_argsk_scalar(x):
	def args_mod(args):
		args['K'] = args['N'] - x
		if args['K'] <= 0: args['K'] = 1
	return args_mod

def set_argsk_perc(perc):
	def args_mod(args):
		args['K'] = round(args['N']*perc) or 1
	return args_mod

def set_lifetime(prefix, perc_uptime, perc_downtime):
	def args_mod(args):
		lifetime = args[f"{prefix}_LIFETIME"]
		args[f"{prefix}_UPTIME"] = round(lifetime * perc_uptime)
		args[f"{prefix}_DOWNTIME"] = round(lifetime * perc_downtime)
	return args_mod


# Plots.game_over_avg(100)
# ARGS['MULTI_BLOCK_SERVER'] = True
# Plots.game_over_avg(100)
# ARGS['MULTI_BLOCK_SERVER'] = False

# Plots.set_output("single_block_dist")
# Plots.game_over_dist(100, ARGS, 10)

# Plots.set_output("single_block_N_with_K-0.8")
# Plots.plot_game_overs('N', range(1,41), 10, None, set_argsk_perc(0.8))
#
# Plots.set_output("single_block_N_with_K-2")
# Plots.plot_game_overs('N', range(1,41), 10, None, set_argsk_scalar(2))
# ARGS['N'] = 10
# ARGS['K'] = 8

# Plots.set_output("single_block_DATA_SIZE")
# Plots.plot_game_overs('DATA_SIZE', range(20,300,20), 10)

# Plots.set_output("single_block_lifetime")
# Plots.plot_game_overs_comparison(['NODE_LIFETIME','SERVER_LIFETIME'], range(35, 455, 30), 10)

# ARGS['NODE_LIFETIME'] = 365
# ARGS['SERVER_LIFETIME'] = 30
# Plots.game_over_avg(100)

# Plots.set_output("single_block_NODE_LIFETIME")
# Plots.plot_game_overs('NODE_LIFETIME', range(10,100,10), 10, None, set_lifetime('NODE', 0.25, 0.5))

# Plots.set_output("single_block_SERVER_LIFETIME")
# Plots.plot_game_overs('SERVER_LIFETIME', range(200,400,20), 10, None, set_lifetime('SERVER', 0.8, 0.005))

# Plots.plot_fails_multi('DOWNLOAD_SPEED', [1,2,4,8], lambda v: (f"dlspeed-{v}",'DOWNLOAD_SPEED'))
# Plots.plot_fails_multi('UPLOAD_SPEED', [0.1,0.5,1,2], lambda v: (f"ulspeed-{v}",'UPLOAD_SPEED'))


# ================

ARGS['MULTI_BLOCK_SERVER'] = True

# Plots.set_output("multi_block_dist")
# Plots.game_over_dist(100, ARGS, 10)

ARGS['NODE_LIFETIME'] = 365
ARGS['SERVER_LIFETIME'] = 30

# Plots.game_over_avg(100)

Plots.set_output("multi_block_DATA_SIZE")
ARGS['MULTI_BLOCK_SERVER'] = False
Plots.plot_game_overs('DATA_SIZE', range(20,300,20), 10, plt.plot)
ARGS['MULTI_BLOCK_SERVER'] = True
Plots.plot_game_overs('DATA_SIZE', range(20,300,20), 10, plt.plot)
plt.legend(['single block', 'mutli block'])
Plots._plot_out(ARGS)


# Plots.set_output("multi_block_N_with_K-0.8")
# Plots.plot_game_overs('N', range(1,41), 10, None, set_argsk_perc(0.8))
# ARGS['N'] = 10
# ARGS['K'] = 8
