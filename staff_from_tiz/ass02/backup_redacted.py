#!/usr/bin/env python3

from heapq import heappush, heappop
from random import expovariate

# Shortcut constants

KB = 1024 # bytes
MB = 1024 ** 2  # bytes
GB = 1024 ** 3  # bytes
MINUTE = 60
HOUR = 60 * 60  # seconds
DAY = 24 * HOUR  # seconds
YEAR = 365 * DAY


### SYSTEM PARAMETERS

N = 10  # number of servers storing data
K = 8  # number of blocks needed to recover data

# parameters about the node backing up the data
NODE_LIFETIME = 30 * DAY  # average time before node crashes and loses data
NODE_UPTIME = 8 * HOUR  # average time spent online by the node
NODE_DOWNTIME = 16 * HOUR  # average time spent offline
DATA_SIZE = 100 * GB  # amount of data to backup
UPLOAD_SPEED = 500 * KB  # node's speed, per second
DOWNLOAD_SPEED = 2 * MB  # per second

# parameters as before, for the server
SERVER_LIFETIME = 365 * DAY
SERVER_UPTIME = 30 * DAY
SERVER_DOWNTIME = 2 * HOUR

# length of the simulation
MAXT = 100 * YEAR

block_size = DATA_SIZE / K
upload_duration = block_size / UPLOAD_SPEED
download_duration = block_size / DOWNLOAD_SPEED

def log(state, message):
    print(f'[{state.t/YEAR:5.2f} {sum(state.local_blocks):2} '
          f'{sum(state.remote_blocks):2}] {message}', file=sys.stderr)

def exp_rv(mean):
    """Return an exponential random variable with the given mean."""
    return expovariate(1 / mean)

class GameOver(Exception):
    """Not enough redundancy in the system, data is lost."""
    pass

class State:
    def __init__(self):
        self.t = t = 0  # seconds
        self.node_online = True  # the node starts online
        self.server_online = [True] * N  # servers all start online
        self.remote_blocks = [False] * N  # no server starts having their block
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

        if self.node_online:
          for i in range(N):
            if not self.remote_blocks and self.local_blocks and self.server_online:
              self.remote_blocks[i] = True
              break
        
        state.schedule(exp_rv(upload_duration), UploadComplete())

        # raise NotImplementedException

    def schedule_next_download(self):
        """Schedule the next download, if any."""

        # if the node is online, download a remote block the node doesn't
        # have from an online server which has it (if possible)

        if self.node_online:
          for i in range(N):
            if not self.local_blocks and self.remote_blocks and self.server_online:
              self.local_blocks[i] = True
              break
        
        state.schedule(exp_rv(download_duration), DownloadComplete())
        
        # raise NotImplementedException

    def check_game_over(self):
        """Did we lose enough redundancy that we can't recover data?"""

        # check if we have at least K blocks saved, either locally or remotely
        lbs, rbs = self.local_blocks, self.remote_blocks
        blocks_saved = [lb or rb for lb, rb in zip(lbs, rbs)]
        if sum(blocks_saved) < K:
            raise GameOver

# events

class ServerEvent:
    """Class with a self.server attribute."""
    
    def __init__(self, server):
        self.server = server
    def __str__(self):  # function to get a pretty printed name for the event
        return f'{self.__class__.__name__}({self.server})'

        
class UploadComplete(ServerEvent):
    """An upload is completed."""
    
    def process(self, state):
        if state.current_upload is not self:
            # this upload was interrupted, we ignore this event
            return
        state.remote_blocks[self.server] = True
        state.schedule_next_upload()

        
class DownloadComplete(ServerEvent):
    """A download is completed."""
    
    def process(self, state):
        if state.current_download is not self:
            # download interrupted
            return
        lb = state.local_blocks
        lb[self.server] = True
        if sum(lb) >= K:  # we have enough data to reconstruct all blocks
            state.local_blocks = [True] * N
        else:
            state.schedule_next_download()

class NodeOnline:
    """Our node went online."""
    
    def process(self, state):
        # mark the node as online
        # schedule next upload and download
        # schedule the next offline event
        state.node_online = True

        state.schedule(exp_rv(upload_duration), UploadComplete())
        state.schedule(exp_rv(download_duration), DownloadComplete())

        state.schedule(exp_rv(NODE_UPTIME), NodeOffline())

        # raise NotImplementedException
        
class NodeOffline:
    """Our node went offline."""
    
    def process(self, state):
        # mark the node as offline
        state.node_online = False
        # cancel current upload and download
        state.current_upload = state.current_download = None
        # schedule the next online event
        state.schedule(exp_rv(NODE_DOWNTIME), NodeOnline())
    
        
class NodeFail(NodeOffline):
    """Our node failed and lost all its data."""
    
    def process(self, state):
        # mark all local blocks as lost
        state.local_blocks = [False] * N
        state.check_game_over()
        state.schedule(exp_rv(NODE_LIFETIME), NodeFail(self.server))
        super().process(state)

        
class ServerOnline(ServerEvent):
    """A server that was offline went back online."""
    
    def process(self, state):
        # mark the server as back online
        # schedule the next server offline event

        # if the node was not uploading/downloading,
        # schedule new uploads/downloads to/from them

        state.server_online[server] = True

        state.schedule(exp_rv(SERVER_UPTIME), ServerOffline(server))

        cu = state.current_upload
        if cu is None and cu.server == server:
            state.current_upload = None

        cd = state.current_download
        if cd is None and cd.server == server:
            state.current_download = None
        

        raise NotImplementedException

    
class ServerOffline(ServerEvent):
    """A server went offline."""
    
    def process(self, state):
        server = self.server
        # mark the server as offline
        state.server_online[server] = False
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
        state.remote_blocks[self.server] = False
        state.check_game_over()
        state.schedule(exp_rv(SERVER_LIFETIME), ServerFail(self.server))
        super().process(state)

        
state = State()
events = state.events

try:
    while events:
        t, event = heappop(events)
        if t > MAXT:
            break
        #print(f'{t / DAY:10.2f} {event}')
        state.t = t
        event.process(state)
except GameOver:
    print(f"Game over after {t/YEAR:.2f} years!")
else:  # no exception
    print(f"Data safe for {t/YEAR:.2f} years!")