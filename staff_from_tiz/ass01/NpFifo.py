import numpy as np

class Fifo:
  def __init__(self):
    self._size = 2
    self.fifo = np.array([0,0])
    self.i_pop = 0
    self.i_push = 0

  def append(self, e):
    if self.i_push == self._size :
      print("resizing up")
      self._size *= 2
      self.fifo.resize((self._size,))
    
    self.fifo[self.i_push] = e
    self.i_push += 1

  def popleft(self):
    if self.i_pop == self.i_push:
      return None

    res = self.fifo[self.i_pop]
    self.i_pop += 1

    if self.i_pop == self._size//2 and self.i_pop != 1:
      print("resizing down")
      for i,x in enumerate(self.fifo[self._size//2:]):
        self.fifo[i] = x
      self.fifo.resize((self._size//2,))
      self.i_pop -= self._size//2
      self.i_push -= self._size//2
      self._size = self._size//2

    return res

  def pop(self):
    return self.popleft()

  def size(self):
    return self.i_push - self.i_pop 
