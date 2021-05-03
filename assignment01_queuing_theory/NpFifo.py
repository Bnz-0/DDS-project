import numpy as np

class Fifo:
  _initialsize = 8

  def __init__(self):
    self._size = Fifo._initialsize
    self.fifo = np.zeros(self._size, dtype=int)
    self.i_pop = 0
    self.i_push = 0
  
  def __len__(self):
    return self.size()
  
  def __getitem__(self, n):
    if self.i_pop + n >= self.i_push: return None
    return self.fifo[self.i_pop + n]

  def append(self, e):
    if self.i_push == self._size :
      self._size *= 2
      self.fifo.resize((self._size,))
    
    self.fifo[self.i_push] = e
    self.i_push += 1

  def popleft(self):
    if self.i_pop == self.i_push:
      return None

    res = self.fifo[self.i_pop]
    self.i_pop += 1

    if self.i_pop == self._size//2:
      toresize = False
      if self.i_pop != Fifo._initialsize//2:
        toresize = True
      
      self.fifo[:self._size//2] = self.fifo[self._size//2:]

      if toresize:
        self.fifo.resize((self._size//2,))
      
      self.i_pop -= self._size//2
      self.i_push -= self._size//2

      if toresize:
        self._size = self._size//2

    return res

  def pop(self):
    return self.popleft()

  def size(self):
    return self.i_push - self.i_pop 
