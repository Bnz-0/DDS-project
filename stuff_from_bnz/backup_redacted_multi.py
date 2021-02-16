#!/usr/bin/env python3

import sys
from heapq import heappush, heappop
from random import expovariate, randint

# Shortcut constants

KB = 1024 # bytes
MB = 1024 ** 2  # bytes
GB = 1024 ** 3  # bytes
MINUTE = 60
HOUR = 60 * 60  # seconds
DAY = 24 * HOUR  # seconds
YEAR = 365 * DAY


### SYSTEM PARAMETERS
def get_arg(name, ptype=int):
	"Get the value of `param`, return `None` if not found"
	try:
		return ptype(sys.argv[
			sys.argv.index(name) + 1
		])
	except ValueError:
		return None

if 'help' in sys.argv:
	print(f"Usage:\n$ {sys.argv[0]} [N [K]]")
	sys.exit(0)

N = get_arg('N') or 10  # number of servers storing data
K = get_arg('K') or 8  # number of blocks needed to recover data

# parameters about the node backing up the data
NODE_LIFETIME = (get_arg('NODE_LIFETIME') or 30) * DAY  # average time before node crashes and loses data
NODE_UPTIME = (get_arg('NODE_UPTIME') or 8) * HOUR  # average time spent online by the node
NODE_DOWNTIME = (get_arg('NODE_DOWNTIME') or 16) * HOUR  # average time spent offline
DATA_SIZE = (get_arg('DATA_SIZE') or 100) * GB  # amount of data to backup
UPLOAD_SPEED = (get_arg('UPLOAD_SPEED') or 500) * KB  # node's speed, per second
DOWNLOAD_SPEED = (get_arg('DOWNLOAD_SPEED') or 2) * MB  # per second

# parameters as before, for the server
SERVER_LIFETIME = (get_arg('SERVER_LIFETIME') or 365) * DAY
SERVER_UPTIME = (get_arg('SERVER_UPTIME') or 30) * DAY
SERVER_DOWNTIME = (get_arg('SERVER_DOWNTIME') or 2) * HOUR

# length of the simulation
MAXT = (get_arg('MAXT') or 100) * YEAR

# additional parameters
#MULTI_BLOCK_SERVER = get_arg('MULTI_BLOCK_SERVER', bool) or False # if True a server can store multiple blocks
N_BLOCK_SERVER = N if get_arg('MULTI_BLOCK_SERVER', lambda x: x=='True') else 1 # if True a server can store multiple blocks

print('N_BLOCK_SERVER', N_BLOCK_SERVER)

block_size = DATA_SIZE / K
upload_duration = block_size / UPLOAD_SPEED
download_duration = block_size / DOWNLOAD_SPEED

def exp_rv(mean):
	"""Return an exponential random variable with the given mean."""
	return expovariate(1 / mean)

class GameOver(Exception):
	"""Not enough redundancy in the system, data is lost."""
	pass

class Server:
	def __init__(self, i):
		self.i = i
		self.online = True
		self.blocks = [False] * N_BLOCK_SERVER

	def can_have(self, i):
		return N_BLOCK_SERVER > 1 or i == self.i

	def have(self, i):
		return self.can_have(i) and self.blocks[min(N_BLOCK_SERVER-1, i)]

	def store(self, i):
		assert self.can_have(i) #TODO: remove once done
		self.blocks[min(N_BLOCK_SERVER-1, i)] = True

	def fail(self):
		self.blocks = [False] * N_BLOCK_SERVER


class State:
	def __init__(self):
		self.t = 0  # seconds
		self.node_online = True  # the node starts online
		self.servers = [Server(i) for i in range(N)]
		self.local_blocks = [True] * N  # flags each locally owned block

		# we need to access current events for uploads and download
		# terminations, in case we need to cancel them because the
		# node or one of the servers went offline
		self.current_upload = self.current_download = None

		self.events = []  # event queue

		# we add to the event queue the first events of node going
		# offline or failing
		self.schedule(exp_rv(NODE_UPTIME), NodeOffline())
		self.schedule(exp_rv(NODE_LIFETIME), NodeFail())

		# same, for each of the servers
		for i in range(N):
			self.schedule(exp_rv(SERVER_UPTIME), ServerOffline(i))
			self.schedule(exp_rv(SERVER_LIFETIME), ServerFail(i))

		# we now decide what the next upload will be
		self.schedule_next_upload()

	def schedule(self, delay, event):
		"""Add an event to the event queue after the required delay."""

		heappush(self.events, (self.t + delay, event))

	def schedule_next_upload(self):
		"""Schedule the next upload, if any."""

		# if the node is online, upload a possessed local block to an online
		# server that doesn't have it (if possible)
		if not self.node_online or self.current_upload is not None:
			return
		for j in range(N): # j-th server
			for i in range(N): # i-th block
				if self.local_blocks[i] and self.servers[j].can_have(i) and not self.servers[j].have(i):
					self.current_upload = UploadComplete(j, i)
					break
			if self.current_upload is not None:
				break
		if self.current_upload is None: return # all backed up
		self.schedule(upload_duration, self.current_upload)

	def schedule_next_download(self):
		"""Schedule the next download, if any."""

		# if the node is online, download a remote block the node doesn't
		# have from an online server which has it (if possible)
		if not self.node_online or self.current_download is not None:
			return
		for i in range(N): # i-th block
			if self.local_blocks[i]:
				continue
			for j in range(N): # j-th server
				if self.servers[j].have(i):
					self.current_download = DownloadComplete(j, i)
					break
			if self.current_download is not None:
				break
		if self.current_download is None: return # all in local
		self.schedule(download_duration, self.current_download)

	def check_game_over(self):
		"""Did we lose enough redundancy that we can't recover data?"""

		# check if we have at least K blocks saved, either locally or remotely
		blocks_saved = self.local_blocks[:]
		for i in range(N):
			if blocks_saved[i]: continue
			for server in self.servers:
				blocks_saved[i] |= server.have(i)

		if sum(blocks_saved) < K:
			raise GameOver

###### events ######

class ServerEvent:
	"""Class with a self.server attribute."""

	def __init__(self, server, block=None):
		self.server = server
		self.block = block
	def __repr__(self):
		return f'{self.__class__.__name__}({self.server}, {self.block})'
	def __str__(self):
		return repr(self)


class UploadComplete(ServerEvent):
	"""An upload is completed."""

	def process(self, state):
		if state.current_upload is self: #the upload was not interrupted
			print(" [DONE]", end='')
			state.servers[self.server].store(self.block)
		else: print(" [FAIL]", end='')
		if state.node_online:
			state.schedule_next_upload()

class DownloadComplete(ServerEvent):
	"""A download is completed."""

	def process(self, state):
		if state.current_download is self:
			print(" [DONE]", end='')
			state.local_blocks[self.server] = True
		else: print(" [FAIL]", end='')
		if sum(state.local_blocks) >= K:  # we have enough data to reconstruct all blocks
			state.local_blocks = [True] * N
		elif state.node_online:
			state.schedule_next_download()

class NodeOnline:
	"""Our node went online."""

	def process(self, state):
		# mark the node as online
		state.node_online = True
		# schedule next upload and download
		state.schedule_next_upload()
		state.schedule_next_download()
		# schedule the next offline event
		state.schedule(exp_rv(NODE_UPTIME), NodeOffline())

	def __str__(self):
		return f'{self.__class__.__name__}'


class NodeOffline:
	"""Our node went offline."""

	def process(self, state):
		# mark the node as offline
		state.node_online = False
		# cancel current upload and download
		state.current_upload = state.current_download = None
		# schedule the next online event
		state.schedule(exp_rv(NODE_DOWNTIME), NodeOnline())

	def __str__(self):
		return f'{self.__class__.__name__}'


class NodeFail(NodeOffline):
	"""Our node failed and lost all its data."""

	def process(self, state):
		# mark all local blocks as lost
		state.local_blocks = [False] * N
		state.check_game_over()
		super().process(state)

	def __str__(self):
		return f'{self.__class__.__name__}'


class ServerOnline(ServerEvent):
	"""A server that was offline went back online."""

	def process(self, state):
		# mark the server as back online
		state.servers[self.server].online = True
		# schedule the next server offline event
		state.schedule(exp_rv(SERVER_UPTIME), ServerOffline(self.server))

		# if the node was not uploading/downloading,
		# schedule new uploads/downloads to/from them
		if state.current_upload is None:
			state.schedule_next_upload()
		if state.current_download is None:
			state.schedule_next_download()

class ServerOffline(ServerEvent):
	"""A server went offline."""

	def process(self, state):
		server = self.server
		# mark the server as offline
		state.servers[self.server].online = False
		# schedule the next server online event
		state.schedule(exp_rv(SERVER_DOWNTIME), ServerOnline(server))

		# interrupt any current uploads/downloads to this server
		cu = state.current_upload
		if cu is not None and cu.server == server:
			state.current_upload = None

		cd = state.current_download
		if cd is not None and cd.server == server:
			state.current_download = None


class ServerFail(ServerOffline):
	"""A server failed and lost its data."""

	def process(self, state):
		state.servers[self.server].fail()
		state.check_game_over()
		super().process(state)


state = State()
events = state.events

try:
	while events:
		t, event = heappop(events)
		if t > MAXT:
			break
		print(f'\n{t / DAY:10.2f} {event}', end='')
		state.t = t
		event.process(state)
except GameOver:
	print(f"\nGame over after {t/YEAR:.2f} years!")
else:  # no exception
	print(f"\nData safe for {t/YEAR:.2f} years!")
